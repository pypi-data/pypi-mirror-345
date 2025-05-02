from __future__ import annotations

import json
import logging
import os
import time
from abc import abstractmethod
from datetime import datetime, timezone
from typing import Any, Iterator, Self, cast
from uuid import UUID

import numpy as np
from PIL import Image
from pymilvus import Collection, DataType, MilvusClient
from pymilvus.orm.constants import UNLIMITED

from ..utils.pydantic import (
    Vector,
    base64_encode_image,
    base64_encode_numpy_array,
    decode_base64_image,
    decode_base64_numpy_array,
)
from .memory_types import (
    LabeledMemory,
    LabeledMemoryLookup,
    Memory,
    MemoryLookup,
    ScoredMemory,
    ScoredMemoryLookup,
)
from .repository import (
    CACHE_SIZE,
    CACHE_TTL,
    FilterItem,
    MemorysetConfig,
    MemorysetRepository,
)

logging.getLogger("pymilvus.milvus_client.milvus_client").setLevel(logging.WARNING)


MEMORY_FIELDS = [
    "text",
    "image",
    "timeseries",
    "embedding",
    "metadata",
    "source_id",
    "memory_id",
    "memory_version",
    "created_at",
    "updated_at",
    "metrics",
]


# TODO: Replace this once Milvus Lite supports null values for scalar fields: https://github.com/milvus-io/pymilvus/issues/2495
def _none_to_empty(value: Any | None, klass) -> Any:
    if klass == str:
        return value if value is not None else ""
    elif klass == int:
        return value if value is not None else -1
    elif klass == float:
        return value if value is not None else float("nan")
    elif klass == dict:
        return value if value is not None else {}
    elif klass == list:
        return value if value is not None else []
    elif klass == bytes:
        return value if value is not None else ""
    else:
        raise ValueError(f"Unsupported class {klass}")


def _empty_to_none(value: Any, klass) -> Any:
    if klass == str:
        return value if value != "" else None
    elif klass == int:
        return value if value != -1 else None
    elif klass == float:
        return value if value != float("nan") else None
    elif klass == dict:
        return value if value != {} else None
    elif klass == list:
        return value if value != [] else None
    else:
        raise ValueError(f"Unsupported class {klass}")


def _safely_trim_to_bytes(s: str, max_bytes: int) -> str:
    encoded = s.encode("utf-8")
    if len(encoded) <= max_bytes:
        return s

    # Binary search to find the max char length that fits
    low, high = 0, len(s)
    while low < high:
        mid = (low + high) // 2
        if len(s[:mid].encode("utf-8")) <= max_bytes:
            low = mid + 1
        else:
            high = mid

    # Final substring that safely fits
    return s[: low - 1]


def _prepare_for_insert(memory: Memory | LabeledMemory | ScoredMemory) -> dict[str, Any]:
    # Milvus does not support storing UUIDs in JSON fields, so we need to convert the UUIDs in the metrics to strings
    memory_metrics = cast(dict, memory.metrics)
    if memory_metrics is not None:
        if memory_metrics.get("duplicate_memory_ids"):
            memory_metrics["duplicate_memory_ids"] = [
                str(memory_id) for memory_id in memory_metrics["duplicate_memory_ids"]
            ]
        if memory_metrics.get("potential_duplicate_memory_ids"):
            memory_metrics["potential_duplicate_memory_ids"] = [
                str(memory_id) for memory_id in memory_metrics["potential_duplicate_memory_ids"]
            ]

    base_dict = {
        "text": (
            _safely_trim_to_bytes(memory.value, BaseMemorysetMilvusRepository.MAX_TEXT_LENGTH)
            if isinstance(memory.value, str)
            else ""
        ),
        "image": base64_encode_image(memory.value) if isinstance(memory.value, Image.Image) else "",
        "timeseries": base64_encode_numpy_array(memory.value) if isinstance(memory.value, np.ndarray) else "",
        "metadata": memory.metadata,
        "memory_id": str(memory.memory_id),
        "memory_version": memory.memory_version,
        "source_id": _none_to_empty(memory.source_id, str),
        "embedding": memory.embedding,
        "created_at": int(memory.created_at.timestamp() * 1000),  # millisecond precision
        "updated_at": int(memory.updated_at.timestamp() * 1000),  # millisecond precision
        "metrics": memory_metrics or {},
    }

    if isinstance(memory, LabeledMemory):
        base_dict["label"] = memory.label
    elif isinstance(memory, ScoredMemory):
        base_dict["score"] = memory.score

    return base_dict


def _parse_row(row: dict[str, Any]) -> dict:
    if "image" in row and _empty_to_none(row["image"], str) is not None:
        value = decode_base64_image(row["image"])
    elif "timeseries" in row and _empty_to_none(row["timeseries"], str) is not None:
        value = decode_base64_numpy_array(row["timeseries"])
    else:
        value = row["text"]

    # Milvus does not support storing UUIDs in JSON fields, so we save them as strings in the DB
    # and convert them back to UUIDs here.
    if row["metrics"] is not None:
        if row["metrics"].get("duplicate_memory_ids"):
            row["metrics"]["duplicate_memory_ids"] = [
                UUID(memory_id) for memory_id in row["metrics"]["duplicate_memory_ids"]
            ]
        if row["metrics"].get("potential_duplicate_memory_ids"):
            row["metrics"]["potential_duplicate_memory_ids"] = [
                UUID(memory_id) for memory_id in row["metrics"]["potential_duplicate_memory_ids"]
            ]

    base_dict = dict(
        embedding=np.array(row["embedding"], dtype=np.float32),
        memory_id=UUID(row["memory_id"]),
        memory_version=row["memory_version"],
        source_id=_empty_to_none(row["source_id"], str),
        metadata=row["metadata"],
        value=value,
        created_at=datetime.fromtimestamp(row["created_at"] / 1000, timezone.utc),
        updated_at=datetime.fromtimestamp(row["updated_at"] / 1000, timezone.utc),
        metrics=row["metrics"],
    )
    if "label" in row:
        base_dict["label"] = row["label"]
    if "score" in row:
        base_dict["score"] = row["score"]
    return base_dict


def _format_filter_item(filter_item: FilterItem) -> str:
    # TODO: Add support for contains/not contains once tags are supported
    if (filter_item.op in ["in", "not in"]) and not isinstance(filter_item.value, list):
        raise ValueError(f"Filter value for '{filter_item.op}' operation must be a list, got '{filter_item.value}'")

    if filter_item.op in ["==", "!="] and isinstance(filter_item.value, list):
        raise ValueError(
            f"Filter value for '{filter_item.op}' operation cannot be a list. Please use the 'in' or 'not in' operators instead."
        )

    if filter_item.op == "like":
        if not isinstance(filter_item.value, str):
            raise ValueError(f"Filter value for '{filter_item.op}' operation must be a string, got {filter_item.value}")
        if "%" not in filter_item.value:
            raise ValueError(
                f"'{filter_item.op}' operator requires the use of a wildcard character ('%') in the value, got {filter_item.value}. "
                "If you would like to filter on string equality please use the '==' operator."
            )

    value = filter_item.value

    # Transform field being filtered on to valid Milvus format (i.e. metadata, metadata["tags"], metadata["tags"][0], etc.)
    field = (
        "text" if filter_item.field[0] == "value" else filter_item.field[0]
    )  # Transform field name "value" to "text". This is same transformation we do when inserting data.
    for subfield in filter_item.field[1:]:
        if isinstance(subfield, int):
            field = f"{field}[{subfield}]"
        else:
            field = f'{field}["{subfield}"]'

    if field in ["created_at", "updated_at"]:
        if not isinstance(value, (datetime, str, int, float)):
            raise ValueError(f"Unsupported filter value type for {field}: {value}")
        if isinstance(value, datetime):
            value = int(value.timestamp() * 1000)  # millisecond precision
        elif isinstance(value, str):
            value = int(datetime.fromisoformat(value).timestamp() * 1000)  # millisecond precision
        else:
            value = int(value)

    if filter_item.op in [">", ">=", "<", "<="] and (
        not isinstance(filter_item.value, (int, float, datetime)) or isinstance(filter_item.value, bool)
    ):
        raise ValueError(f"Filter value for '{filter_item.op}' operation must be a number, got '{filter_item.value}'")

    # Format string filter value to be compatible with Milvus
    if isinstance(value, str):
        value = f'"{value}"'

    if value is None:
        value = '""'  # This is how Milvus filters for null values

    return f"{field} {filter_item.op} {value}"


def _format_filters(filters: list[FilterItem]) -> str:
    # WARNING: the casing of the connectors ARE important! ONLY lowercase "and" is supported
    return " and ".join(_format_filter_item(filter_item) for filter_item in filters)


class BaseMemorysetMilvusRepository[TMemory: Memory, TLookup: MemoryLookup](MemorysetRepository[TMemory, TLookup]):
    SCHEMA_VERSION = 3
    """
    The version of the schema of the data and config collections.

    Version 1:
    - Added source_id, updated_at, created_at on data collection
    - Added schema_version on config collection

    Version 2:
    - Updated metadata to be a JSON field

    Version 3:
    - Added metrics JSON field to memory
    """

    # Note: We use the "Bounded" consistency level because it is the default for Milvus cloud. Using "Strong" can
    # cause performance issues and is not necessary for our use case. See https://milvus.io/docs/consistency.md
    DEFAULT_CONSISTENCY_LEVEL = "Bounded"

    METRIC_TYPE = "IP"  # We always use inner product similarity because we used normalize embeddings

    CONFIG_COLLECTION_NAME = "memoryset_configs"

    MAX_TEXT_LENGTH = 60000

    @property
    @abstractmethod
    def MEMORY_FIELDS(self) -> list[str]:
        raise NotImplementedError

    def __init__(
        self,
        database_uri: str,
        collection_name: str = "default",
        cache_ttl: int = CACHE_TTL,
        cache_size: int = CACHE_SIZE,
    ):
        super().__init__(database_uri, collection_name, cache_ttl, cache_size)
        self.is_local_database = not database_uri.startswith("http")

    _connections: dict[str, MilvusClient] = {}

    @classmethod
    def _get_client(cls, database_uri: str, create: bool = False) -> MilvusClient | None:
        if database_uri not in cls._connections:
            if not database_uri.startswith("http"):
                database_uri = os.path.abspath(os.path.expanduser(database_uri))
                if not os.path.exists(database_uri):
                    if not create:
                        # Don't create a local database file if it doesn't exist yet unless create=True
                        return None
                    logging.info(f"Creating local database file at {database_uri}")
                    os.makedirs(os.path.dirname(database_uri), exist_ok=True)
            logging.info(f"Creating Milvus client for {database_uri}")
            cls._connections[database_uri] = MilvusClient(database_uri)
        return cls._connections[database_uri]

    def _drop_database(self):
        raise NotImplementedError("Milvus Lite does not support dropping databases")

    def _initialize_config_collection(self):
        client = self._get_client(self.database_uri)
        if client is None:
            logging.warning(f"Database not found at {self.database_uri}")
            return None
        if not client.has_collection(self.CONFIG_COLLECTION_NAME):
            logging.info(f"Creating config collection for {self.database_uri}")
            schema = client.create_schema(auto_id=False, enable_dynamic_field=True)
            schema.add_field("memoryset_collection_name", DataType.VARCHAR, is_primary=True, max_length=256)
            schema.add_field("label_names", DataType.VARCHAR, is_primary=False, max_length=256)
            schema.add_field("embedding_dim", DataType.INT64, is_primary=False)
            schema.add_field("embedding_model_name", DataType.VARCHAR, is_primary=False, max_length=256)
            schema.add_field("embedding_model_max_seq_length_overwrite", DataType.INT64, is_primary=False)
            schema.add_field("updated_at", DataType.VARCHAR, is_primary=False, max_length=48)
            schema.add_field("schema_version", DataType.INT64, is_primary=False)
            schema.add_field("_unused", DataType.FLOAT_VECTOR, is_primary=False, dim=2)
            client.create_collection(collection_name=self.CONFIG_COLLECTION_NAME, schema=schema)
            # Milvus cloud requires an index, so we create one on the _unused field
            index_params = MilvusClient.prepare_index_params()
            index_params.add_index(field_name="_unused", index_name="_unused", index_type="FLAT", metric_type="L2")
            client.create_index(
                self.CONFIG_COLLECTION_NAME,
                index_params=index_params,
                consistency_level=self.DEFAULT_CONSISTENCY_LEVEL,
            )
        client.load_collection(self.CONFIG_COLLECTION_NAME)

    def get_collection_count(self) -> int:
        client = self._get_client(self.database_uri, create=True)
        if client is None:
            raise RuntimeError(f"Database not found at {self.database_uri}")
        self._initialize_config_collection()
        result = client.query(
            collection_name=self.CONFIG_COLLECTION_NAME,
            output_fields=["count(*)"],
            filter="memoryset_collection_name != ''",
            consistency_level=self.DEFAULT_CONSISTENCY_LEVEL,
        )
        return result[0]["count(*)"]

    def get_collection_names(self) -> list[str]:
        client = self._get_client(self.database_uri)
        if client is None:
            logging.warning(f"Database not found at {self.database_uri}")
            return []
        self._initialize_config_collection()
        result = client.query(
            filter="memoryset_collection_name != ''",
            collection_name=self.CONFIG_COLLECTION_NAME,
            output_fields=["memoryset_collection_name"],
            consistency_level=self.DEFAULT_CONSISTENCY_LEVEL,
        )
        return [row["memoryset_collection_name"] for row in result]

    def drop(self):
        client = self._get_client(self.database_uri)
        if client is None:
            logging.warning(f"Database not found at {self.database_uri}")
            return
        self._initialize_config_collection()

        if not client.has_collection(self.collection_name):
            logging.warning(f"Memoryset {self.collection_name} not found in {self.database_uri}")
        else:
            client.drop_collection(self.collection_name)
        client.delete(
            collection_name=self.CONFIG_COLLECTION_NAME,
            filter=f"memoryset_collection_name == '{self.collection_name}'",
        )
        self._cache.clear()

    def get_config(self) -> MemorysetConfig | None:
        client = self._get_client(self.database_uri)
        if client is None:
            logging.warning(f"Database not found at {self.database_uri}")
            return None
        self._initialize_config_collection()
        config = client.query(
            collection_name=self.CONFIG_COLLECTION_NAME,
            filter=f"memoryset_collection_name == '{self.collection_name}'",
            output_fields=[
                "schema_version",
                "label_names",
                "embedding_dim",
                "embedding_model_name",
                "embedding_model_max_seq_length_overwrite",
            ],
            # We use strong consistency to make sure we are getting the final config in case it was updated
            # by other connections recently.
            consistency_level="Strong",
        )
        if len(config) == 0:
            return None
        elif len(config) > 1:
            raise ValueError("Found multiple config entries for memoryset")

        return MemorysetConfig(
            embedding_dim=config[0]["embedding_dim"],
            embedding_model_name=config[0]["embedding_model_name"],
            embedding_model_max_seq_length_override=_empty_to_none(
                config[0]["embedding_model_max_seq_length_overwrite"], int
            ),
            label_names=json.loads(config[0]["label_names"]),
            schema_version=config[0]["schema_version"] or 0,
        )

    _client_handle: MilvusClient | None = None

    @property
    def _client(self) -> MilvusClient:
        if self._client_handle is None:
            raise RuntimeError("You need to connect the storage backend before using it")
        return self._client_handle

    def _get_schema_fields(self, embedding_dim: int) -> list[tuple[str, DataType, dict[str, Any]]]:
        """Get the schema fields for the data table. Override in subclasses."""
        raise NotImplementedError

    def _initialize_data_collection(self, embedding_dim: int) -> None:
        if not self._client.has_collection(self.collection_name):
            logging.info(f"Creating collection {self.collection_name}")
            schema = self._client.create_schema(auto_id=False, enable_dynamic_field=True)
            schema.add_field("memory_id", DataType.VARCHAR, is_primary=True, max_length=36)
            schema.add_field("memory_version", DataType.INT64, is_primary=False)
            schema.add_field("embedding", DataType.FLOAT_VECTOR, dim=embedding_dim, is_primary=False)
            schema.add_field("metadata", DataType.JSON, is_primary=False)
            schema.add_field("text", DataType.VARCHAR, is_primary=False, max_length=self.MAX_TEXT_LENGTH)
            # Milvus does not support storing bytes and varchar requires a max length, so to support
            # images and timeseries, we set `enable_dynamic_field=True` and don't specify the field
            # type. Images and timeseries are stored as base64 encoded strings in respective fields
            # for now. In the future, we will probably switch to storing images separately and just
            # storing a URI to the image in Milvus.
            schema.add_field("source_id", DataType.VARCHAR, is_primary=False, max_length=512)
            schema.add_field("created_at", DataType.INT64, is_primary=False)
            schema.add_field("updated_at", DataType.INT64, is_primary=False)
            schema.add_field("metrics", DataType.JSON, is_primary=False)
            # Add type-specific fields
            for field_name, field_type, field_kwargs in self._get_schema_fields(embedding_dim):
                schema.add_field(field_name, field_type, is_primary=False, **field_kwargs)
            self._client.create_collection(collection_name=self.collection_name, schema=schema)
            # Create embedding index
            logging.info(f"Creating embedding index for collection {self.collection_name}")
            embedding_index_params = MilvusClient.prepare_index_params()
            embedding_index_params.add_index(
                field_name="embedding",
                index_name=self.collection_name + "_index",
                index_type="FLAT",  # We don't support other index types that need more config yet
                metric_type=self.METRIC_TYPE,
            )
            self._client.create_index(collection_name=self.collection_name, index_params=embedding_index_params)
            # Create source_id index
            logging.info(f"Creating source_id index for collection {self.collection_name}")
            source_id_index_params = MilvusClient.prepare_index_params()
            source_id_index_params.add_index(
                field_name="source_id",
                index_name=self.collection_name + "_source_id_index",
                # TODO: set `index_type` to B-Tree once Milvus supports it
            )
            self._client.create_index(collection_name=self.collection_name, index_params=source_id_index_params)
        self._client.load_collection(self.collection_name)

    __config: MemorysetConfig | None = None

    @property
    def _config(self) -> MemorysetConfig:
        if self.__config is None:
            raise RuntimeError("You need to connect the storage backend before using it")
        return self.__config

    def _upsert_config(self, config: MemorysetConfig) -> None:
        logging.info(f"Upserting config for {self.collection_name}")
        self._initialize_config_collection()
        current_config_res = self._client.get(self.CONFIG_COLLECTION_NAME, ids=[self.collection_name])
        schema_version = current_config_res[0]["schema_version"] if len(current_config_res) > 0 else self.SCHEMA_VERSION
        self._client.upsert(
            collection_name=self.CONFIG_COLLECTION_NAME,
            data=[
                {
                    "memoryset_collection_name": self.collection_name,
                    "label_names": json.dumps(config.label_names),
                    "embedding_dim": config.embedding_dim,
                    "embedding_model_name": config.embedding_model_name,
                    "embedding_model_max_seq_length_overwrite": _none_to_empty(
                        config.embedding_model_max_seq_length_override, int
                    ),
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                    "schema_version": schema_version,
                    "_unused": [0.0, 0.0],
                }
            ],
        )
        self.__config = config

    def update_config(self, config: MemorysetConfig) -> MemorysetConfig:
        original_config = self._config
        self._upsert_config(config)
        if original_config.label_names != config.label_names:
            self._cache.clear()
        return config

    def connect(self, config: MemorysetConfig) -> Self:
        self._client_handle = self._get_client(self.database_uri, create=True)
        assert self._client_handle is not None and self._get_client(self.database_uri) is not None
        self._upsert_config(config)
        self._initialize_data_collection(embedding_dim=config.embedding_dim)
        return self

    def insert(self, data: list[TMemory]) -> None:
        data_to_insert = [_prepare_for_insert(d) for d in data]
        self._client.insert(collection_name=self.collection_name, data=data_to_insert)
        self._cache.clear()

    @abstractmethod
    def _to_memory(self, row: dict[str, Any]) -> TMemory:
        """Convert a database row to a memory object. Override in subclasses."""
        raise NotImplementedError

    @abstractmethod
    def _to_memory_lookup(self, row: dict[str, Any]) -> TLookup:
        """Convert a database row to a memory lookup object. Override in subclasses."""
        raise NotImplementedError

    def _lookup(self, queries: list[Vector], k: int) -> list[list[TLookup]]:
        if self.is_local_database:
            # We found that MilvusList is 60x slower for batched lookups (tested 11/22/2024)
            # TODO: file an issue about this at https://github.com/milvus-io/milvus-lite/issues
            rows_batch = [
                self._client.search(
                    collection_name=self.collection_name,
                    data=[q],
                    limit=k,
                    output_fields=self.MEMORY_FIELDS,
                    search_params={"metric_type": self.METRIC_TYPE},
                )[0]
                for q in queries
            ]
        else:
            # TODO: benchmark batching vs non-batching on cloud milvus
            rows_batch = self._client.search(
                collection_name=self.collection_name,
                data=[q.tolist() for q in queries],
                limit=k,
                output_fields=self.MEMORY_FIELDS,
                search_params={"metric_type": self.METRIC_TYPE},
            )
        return [[self._to_memory_lookup(row) for row in rows] for rows in rows_batch]

    def lookup(self, queries: list[Vector], k: int, *, use_cache: bool) -> list[list[TLookup]]:
        # if caching is disabled, we can just lookup the queries directly
        if not use_cache:
            return self._lookup(queries, k)

        # otherwise we first resolve cache hits and collect the new queries to lookup
        new_queries: list[Vector] = []
        new_queries_indices: list[int] = []
        new_queries_cache_keys: list[str] = []
        all_results: list[tuple[int, list[TLookup]]] = []  # (index, result)
        for i, q in enumerate(queries):
            cache_key = self._get_cache_key(q, k)
            result = self._cache.get(cache_key, None)
            if result is not None:
                all_results.append((i, result))
            else:
                new_queries.append(q)
                new_queries_indices.append(i)
                new_queries_cache_keys.append(cache_key)

        # if everything was cached, we can just return the cached results
        if len(new_queries) == 0:
            return [r for _, r in all_results]

        # otherwise, perform lookup for the new queries
        new_results = self._lookup(new_queries, k)

        # if nothing was cached, we can just store the new results and return them
        if len(all_results) == 0:
            for cache_key, result in zip(new_queries_cache_keys, new_results):
                self._cache[cache_key] = result
            return new_results

        # otherwise, store the new results and return the combined results in given order
        for i, cache_key, result in zip(new_queries_indices, new_queries_cache_keys, new_results):
            self._cache[cache_key] = result
            all_results.append((i, result))
        all_results.sort(key=lambda x: x[0])
        return [r for _, r in all_results]

    def list(
        self,
        *,
        limit: int | None = None,
        offset: int | None = None,
        filters: list[FilterItem] = [],
        verbose: bool = False,
    ) -> list[TMemory]:
        offset = offset or 0
        if filters == []:
            filter = "memory_id != ''"  # This is necessary to avoid an error when no limit is set
        else:
            filter = _format_filters(filters)

        if verbose:
            logging.info(f"Milvus Query {self.collection_name} - filter: {filter}, limit: {limit}, offset: {offset}")

        # Note: Milvus does not support sort by: https://github.com/milvus-io/milvus/issues/33295
        result = self._client.query(
            collection_name=self.collection_name,
            output_fields=self.MEMORY_FIELDS,
            limit=limit,
            offset=offset,
            filter=filter,
        )
        return [self._to_memory(row) for row in result]

    def iterator(
        self,
        *,
        limit: int | None = UNLIMITED,
        batch_size: int = 100,
        filters: list[FilterItem] = [],
    ) -> Iterator[TMemory]:
        collection = Collection(self.collection_name, using=self._client._using)

        if filters == []:
            expr = ""
        else:
            expr = _format_filters(filters)

        iterator = collection.query_iterator(
            batch_size=batch_size,
            limit=limit,
            expr=expr,
            output_fields=self.MEMORY_FIELDS,
        )

        # See https://milvus.io/docs/get-and-scalar-query.md#Use-QueryIterator for more details

        while True:
            batch = iterator.next()

            if not batch:
                iterator.close()
                break

            for item in batch:
                yield self._to_memory(item)

    def count(self, filters: list[FilterItem] = []) -> int:
        # Note: We use strong consistency to make sure we are getting the final count
        try:
            result = self._client.query(
                collection_name=self.collection_name,
                output_fields=["count(*)"],
                filter=_format_filters(filters),
                # Important: We use "Session" consistency level to ensure all writes from the same session are visible. In the past
                # we used "Strong" consistency level, but this caused performance issues.
                consistency_level="Session",
            )
            return result[0]["count(*)"]
        except Exception as e:
            raise RuntimeError(f"Error counting memories in {self.collection_name}: {e}")

    def get(self, memory_id: UUID) -> TMemory | None:
        result = self._client.get(collection_name=self.collection_name, ids=[memory_id])
        if len(result) == 0:
            return None
        assert len(result) == 1
        return self._to_memory(result[0])

    def get_multi(self, memory_ids: list[UUID], consistency_level: str = "Bounded") -> dict[UUID, TMemory]:
        result = self._client.get(
            collection_name=self.collection_name, ids=memory_ids, consistency_level=consistency_level
        )

        return {UUID(row["memory_id"]): self._to_memory(row) for row in result}

    def upsert(self, memory: TMemory) -> TMemory:
        data_to_insert = [_prepare_for_insert(memory)]
        res = self._client.upsert(collection_name=self.collection_name, data=data_to_insert)
        if res["upsert_count"] == 0:
            raise ValueError(f"Upsert failed for memory {memory.memory_id}")
        if self.is_local_database:  # milvus lite doesn't guarantee that the upsert is completed
            time.sleep(0.1)
        updated_memory = self.get(memory.memory_id)
        if updated_memory is None:
            raise ValueError(f"Upserted memory {memory.memory_id} could not be found")
        self._cache.clear()
        return updated_memory

    def upsert_multi(self, memories: list[TMemory]) -> dict[UUID, TMemory]:
        data_to_insert = [_prepare_for_insert(d) for d in memories]
        res = self._client.upsert(collection_name=self.collection_name, data=data_to_insert)

        if res["upsert_count"] != len(memories):
            raise ValueError("Upsert failed for some memories")

        if self.is_local_database:  # milvus lite doesn't guarantee that the upsert is completed
            time.sleep(0.1)

        updated_memories = self.get_multi([m.memory_id for m in memories], consistency_level="Session")

        if len(updated_memories) != len(memories):
            raise ValueError("Upserted memories could not be found")

        self._cache.clear()

        return updated_memories

    def delete_multi(self, memory_ids: list[UUID]) -> bool:
        existing_memories = self.get_multi(memory_ids)
        to_delete = [str(memory_id) for memory_id in memory_ids if memory_id in existing_memories]

        if not to_delete:
            return False

        res = self._client.delete(collection_name=self.collection_name, ids=to_delete)

        if self.is_local_database and isinstance(res, list):
            # milvus lite returns a list of deleted ids instead of a dict with delete_count
            num_deleted = len(res)
        else:
            num_deleted = res["delete_count"]

        self._cache.clear()

        return num_deleted == len(memory_ids)


class LabeledMemorysetMilvusRepository(BaseMemorysetMilvusRepository[LabeledMemory, LabeledMemoryLookup]):
    @property
    def MEMORY_FIELDS(self) -> list[str]:
        return MEMORY_FIELDS + ["label"]

    def _get_schema_fields(self, embedding_dim: int) -> list[tuple[str, DataType, dict[str, Any]]]:
        return [("label", DataType.INT64, {})]

    def _to_memory(self, row: dict[str, Any]) -> LabeledMemory:
        label_names = self._config.label_names
        return LabeledMemory(
            **_parse_row(row),
            label_name=label_names[row["label"]] if row["label"] < len(label_names) else None,
        )

    def _to_memory_lookup(self, row: dict[str, Any]) -> LabeledMemoryLookup:
        return LabeledMemoryLookup(**self._to_memory(row["entity"]).model_dump(), lookup_score=row["distance"])


class ScoredMemorysetMilvusRepository(BaseMemorysetMilvusRepository[ScoredMemory, ScoredMemoryLookup]):
    @property
    def MEMORY_FIELDS(self) -> list[str]:
        return MEMORY_FIELDS + ["score"]

    def _get_schema_fields(self, embedding_dim: int) -> list[tuple[str, DataType, dict[str, Any]]]:
        return [("score", DataType.FLOAT, {})]

    def _to_memory(self, row: dict[str, Any]) -> ScoredMemory:
        return ScoredMemory(**_parse_row(row))

    def _to_memory_lookup(self, row: dict[str, Any]) -> ScoredMemoryLookup:
        return ScoredMemoryLookup(**self._to_memory(row["entity"]).model_dump(), lookup_score=row["distance"])
