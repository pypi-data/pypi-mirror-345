from __future__ import annotations

import io
import json
import logging
import os
from datetime import datetime, timezone
from typing import Any, Self
from uuid import UUID

import lancedb
import numpy as np
import pyarrow as pa
from PIL import Image

from ..utils.pydantic import Vector
from .memory_types import (
    LabeledMemory,
    LabeledMemoryLookup,
    Memory,
    MemoryLookup,
    ScoredMemory,
    ScoredMemoryLookup,
)
from .repository import CACHE_SIZE, CACHE_TTL, MemorysetConfig, MemorysetRepository


def _encode_image(image: Image.Image) -> bytes:
    buffer = io.BytesIO()
    image.save(buffer, format=image.format)
    return buffer.getvalue()


def _decode_image(image_bytes: bytes) -> Image.Image:
    return Image.open(io.BytesIO(image_bytes))


def _encode_numpy_array(array: np.ndarray) -> bytes:
    buffer = io.BytesIO()
    np.save(buffer, array)
    return buffer.getvalue()


def _decode_numpy_array(array_bytes: bytes) -> np.ndarray:
    return np.load(io.BytesIO(array_bytes))


class BaseMemorysetLanceDBRepository[TMemory: Memory, TLookup: MemoryLookup](MemorysetRepository[TMemory, TLookup]):
    SCHEMA_VERSION = 2
    """
    The version of the schema of the data and config collections.

    Version 1:
    - Added source_id, updated_at, created_at on data collection
    - Added schema_version on config collection

    Version 2:
    - Added metrics json field to memory
    """

    METADATA_TABLE_NAME = "memoryset_metadata"

    def __init__(
        self,
        database_uri: str,
        collection_name: str = "memories",
        cache_ttl: int = CACHE_TTL,
        cache_size: int = CACHE_SIZE,
    ) -> None:
        super().__init__(database_uri, collection_name, cache_ttl, cache_size)
        self.is_local_database = True
        self.table_name = collection_name

    _connections: dict[str, lancedb.DBConnection] = {}

    @classmethod
    def _get_db_connection(cls, database_uri: str) -> lancedb.DBConnection:
        if database_uri not in cls._connections:
            cls._connections[database_uri] = lancedb.connect(database_uri)
        return cls._connections[database_uri]

    def _drop_database(self):
        self._get_db_connection(self.database_uri).drop_database()

    __config_table: lancedb.table.Table | None = None

    @property
    def _config_table(self) -> lancedb.table.Table | None:
        if self.__config_table is not None:
            return self.__config_table
        # We don't want to create the database if it doesn't exist yet
        if not os.path.exists(self.database_uri):
            return None
        db = self._get_db_connection(self.database_uri)
        if self.METADATA_TABLE_NAME not in db.table_names():
            logging.info(f"Creating config table for {self.database_uri}")
            config_table = db.create_table(
                self.METADATA_TABLE_NAME,
                schema=pa.schema(
                    [
                        pa.field("memoryset_table_name", pa.string(), nullable=False),
                        pa.field("label_names", pa.string()),
                        pa.field("embedding_dim", pa.int64(), nullable=False),
                        pa.field("embedding_model_name", pa.string(), nullable=False),
                        pa.field("embedding_model_max_seq_length_overwrite", pa.int64()),
                        pa.field("schema_version", pa.int64(), nullable=False),
                    ]
                ),
            )
        else:
            config_table = db.open_table(self.METADATA_TABLE_NAME)
            # if the table already exists, migrate it to the latest schema
            if "embedding_model_max_seq_length_overwrite" not in config_table.schema.names:
                if "embedding_model_max_seq_length" in config_table.schema.names:
                    config_table.alter_columns(
                        {"path": "embedding_model_max_seq_length", "name": "embedding_model_max_seq_length_overwrite"}  # type: ignore -- lancedb types are wrong
                    )
                else:
                    config_table.add_columns({"embedding_model_max_seq_length_overwrite": "null"})

            if "embedding_model_version" in config_table.schema.names:
                config_table.drop_columns(["embedding_model_version"])
            if "embedding_model_query_prompt" in config_table.schema.names:
                config_table.drop_columns(["embedding_model_query_prompt"])
            if "embedding_model_document_prompt" in config_table.schema.names:
                config_table.drop_columns(["embedding_model_document_prompt"])
            if "embedding_model_embedding_dim" in config_table.schema.names:
                if "embedding_dim" not in config_table.schema.names:
                    config_table.alter_columns(
                        {"path": "embedding_model_embedding_dim", "name": "embedding_dim"}  # type: ignore -- lancedb types are wrong
                    )
                else:
                    config_table.drop_columns(["embedding_model_embedding_dim"])

            if "label_names" not in config_table.schema.names:
                config_table.add_columns({"label_names": "'[]'"})

            if "schema_version" not in config_table.schema.names:
                config_table.add_columns({"schema_version": "0"})
        self.__config_table = config_table
        return config_table

    def get_collection_names(self) -> list[str]:
        if self._config_table is None:
            return []
        result = self._config_table.search().select(["memoryset_table_name"]).to_list()
        return [row["memoryset_table_name"] for row in result]

    def drop(self):
        self.__config_table = None
        self.__data_table = None
        if self._config_table is None:
            logging.warning(f"Database not found at {self.database_uri}")
            return
        db = self._get_db_connection(self.database_uri)
        if self.table_name not in db.table_names():
            logging.warning(f"Memoryset {self.table_name} not found in {self.database_uri}")
        else:
            db.drop_table(self.table_name)
        self._config_table.delete(f"memoryset_table_name == '{self.table_name}'")
        self._cache.clear()

    def get_config(self) -> MemorysetConfig | None:
        if self._config_table is None:
            return None
        config = self._config_table.search().where(f"memoryset_table_name == '{self.table_name}'").to_list()
        if len(config) == 0:
            return None
        if len(config) > 1:
            raise RuntimeError(f"Found {len(config)} config entries for memoryset {self.table_name}")
        return MemorysetConfig(
            label_names=json.loads(config[0]["label_names"]),
            embedding_dim=config[0]["embedding_dim"],
            embedding_model_name=config[0]["embedding_model_name"],
            # TODO: fix once LanceDB supports null for ints https://github.com/lancedb/lancedb/issues/1325
            embedding_model_max_seq_length_override=(
                config[0]["embedding_model_max_seq_length_overwrite"]
                if config[0]["embedding_model_max_seq_length_overwrite"] != -1
                else None
            ),
            schema_version=config[0]["schema_version"],
        )

    __data_table: lancedb.table.Table | None = None

    def _get_schema_fields(self, embedding_model_dim: int) -> list[pa.Field]:
        """Get the schema fields for the data table. Override in subclasses."""
        raise NotImplementedError

    def _initialize_data_table(self, db: lancedb.DBConnection, embedding_model_dim: int) -> None:
        if self.table_name not in db.table_names():
            schema = pa.schema(self._get_schema_fields(embedding_model_dim))
            self.__data_table = db.create_table(self.table_name, schema=schema, exist_ok=False)
        else:
            self.__data_table = db.open_table(self.table_name)

    __config: MemorysetConfig | None = None

    @property
    def _config(self) -> MemorysetConfig:
        if self.__config is None:
            raise RuntimeError("You need to connect the storage backend before using it")
        return self.__config

    def _upsert_config(self, config: MemorysetConfig) -> None:
        assert self._config_table is not None, "make sure to call self._get_db_connection before this"
        self._config_table.merge_insert(
            "memoryset_table_name"
        ).when_matched_update_all().when_not_matched_insert_all().execute(
            [
                {
                    "memoryset_table_name": self.table_name,
                    "label_names": json.dumps(config.label_names),
                    "embedding_dim": config.embedding_dim,
                    "embedding_model_name": config.embedding_model_name,
                    # TODO: fix once LanceDB supports null for ints https://github.com/lancedb/lancedb/issues/1325
                    "embedding_model_max_seq_length_overwrite": (
                        config.embedding_model_max_seq_length_override
                        if config.embedding_model_max_seq_length_override is not None
                        else -1
                    ),
                    # we do automatically migrate on connect, so schema will always be up to date
                    "schema_version": self.SCHEMA_VERSION,
                }
            ]
        )
        self.__config = config

    def update_config(self, config: MemorysetConfig) -> MemorysetConfig:
        original_config = self._config
        self._upsert_config(config)
        if original_config.label_names != config.label_names:
            self._cache.clear()
        return config

    @property
    def _data_table(self) -> lancedb.table.Table:
        if self.__data_table is None:
            raise RuntimeError("You need to connect the storage backend before using it")
        return self.__data_table

    def connect(self, config: MemorysetConfig) -> Self:
        db = self._get_db_connection(self.database_uri)
        self.connected = True
        self._upsert_config(config)
        self._initialize_data_table(db, config.embedding_dim)
        return self

    def insert(self, data: list[TMemory]) -> None:
        if len(data) == 0:
            return
        data_to_insert = [self._prepare_for_insert(d) for d in data]
        self._data_table.add(data_to_insert)
        self._cache.clear()

    def lookup(self, queries: list[Vector], k: int, *, use_cache: bool) -> list[list[TLookup]]:
        def single_lookup(q: Vector) -> list[TLookup]:
            cache_key = self._get_cache_key(q, k)
            result = self._cache.get(cache_key, None) if use_cache else None
            if result is None:
                rows = self._data_table.search(q).with_row_id(True).limit(k).to_list()
                result = [self._to_memory_lookup(row, q) for row in rows]
                if use_cache:
                    self._cache[cache_key] = result
            return result

        return [single_lookup(q) for q in queries]

    def list(self, *, limit: int | None = None, offset: int | None = None, filters=[]) -> list[TMemory]:
        if filters != []:
            raise NotImplementedError("LanceDB does not support filters")
        result = self._data_table.search().limit(limit).offset(offset or 0).to_list()
        return [self._to_memory(row) for row in result]

    def count(self, filters=[]) -> int:
        if filters != []:
            raise NotImplementedError("LanceDB does not support filters")
        return self._data_table.count_rows()

    def get(self, memory_id: UUID) -> TMemory | None:
        result = self._data_table.search().where(f"memory_id == '{str(memory_id)}'").to_list()
        if len(result) == 0:
            return None
        assert len(result) == 1
        return self._to_memory(result[0])

    def get_multi(self, memory_ids: list[UUID]) -> dict[UUID, TMemory]:
        ids_string = ", ".join([f"'{str(mid)}'" for mid in memory_ids])

        result = self._data_table.search().where(f"memory_id in ({ids_string})").to_list()

        return {UUID(row["memory_id"]): self._to_memory(row) for row in result}

    def upsert(self, memory: TMemory) -> TMemory:
        data_to_insert = [self._prepare_for_insert(memory)]
        self._data_table.merge_insert("memory_id").when_matched_update_all().when_not_matched_insert_all().execute(
            data_to_insert
        )
        updated_memory = self.get(memory.memory_id)
        if updated_memory is None:
            raise ValueError(f"Upserted memory {memory.memory_id} could not be found")
        self._cache.clear()
        return updated_memory

    def upsert_multi(self, memories: list[TMemory]) -> dict[UUID, TMemory]:
        data_to_insert = [self._prepare_for_insert(m) for m in memories]
        self._data_table.merge_insert("memory_id").when_matched_update_all().when_not_matched_insert_all().execute(
            data_to_insert
        )
        updated_memories = self.get_multi([m.memory_id for m in memories])
        if len(updated_memories) != len(memories):
            raise ValueError("Upserted memories could not be found")
        self._cache.clear()
        return updated_memories

    def delete_multi(self, memory_ids: list[UUID]) -> bool:
        existing_ids = self.get_multi(memory_ids).keys()

        ids_string = ", ".join([f"'{str(mid)}'" for mid in existing_ids])

        self._data_table.delete(f"memory_id in ({ids_string})")

        self._cache.clear()

        return all((id in existing_ids) for id in memory_ids)

    def _prepare_for_insert(self, memory: TMemory) -> dict[str, Any]:
        """Prepare a memory object for insertion. Override in subclasses."""
        raise NotImplementedError

    def _to_memory(self, row: dict[str, Any]) -> TMemory:
        """Convert a database row to a memory object. Override in subclasses."""
        raise NotImplementedError

    def _to_memory_lookup(self, row: dict[str, Any], query: np.ndarray) -> TLookup:
        """Convert a database row to a memory lookup object. Override in subclasses."""
        raise NotImplementedError


class LabeledMemorysetLanceDBRepository(BaseMemorysetLanceDBRepository[LabeledMemory, LabeledMemoryLookup]):
    def _get_schema_fields(self, embedding_model_dim: int) -> list[pa.Field]:
        return [
            pa.field("text", pa.string()),
            pa.field("image", pa.binary()),
            pa.field("timeseries", pa.binary()),
            pa.field("label", pa.int64()),
            pa.field("metadata", pa.string()),
            pa.field("metrics", pa.string()),
            pa.field("memory_id", pa.string()),
            pa.field("memory_version", pa.int64()),
            pa.field("source_id", pa.string()),
            pa.field("embedding", pa.list_(pa.float32(), list_size=embedding_model_dim)),
            pa.field("created_at", pa.string()),
            pa.field("updated_at", pa.string()),
        ]

    def _prepare_for_insert(self, memory: LabeledMemory) -> dict[str, Any]:
        return {
            "text": memory.value if isinstance(memory.value, str) else None,
            "image": _encode_image(memory.value) if isinstance(memory.value, Image.Image) else None,
            "timeseries": _encode_numpy_array(memory.value) if isinstance(memory.value, np.ndarray) else None,
            "label": memory.label,
            "metadata": json.dumps(memory.metadata) if memory.metadata is not None else "{}",
            "memory_id": str(memory.memory_id),
            "memory_version": memory.memory_version,
            "source_id": str(memory.source_id) if memory.source_id is not None else None,
            "embedding": memory.embedding,
            "created_at": (
                memory.created_at.isoformat()
                if memory.created_at is not None
                else datetime.now(timezone.utc).isoformat()
            ),
            "updated_at": (
                memory.updated_at.isoformat()
                if memory.updated_at is not None
                else datetime.now(timezone.utc).isoformat()
            ),
            "metrics": json.dumps(memory.metrics or {}),
        }

    def _to_memory(self, row: dict[str, Any]) -> LabeledMemory:
        if row["image"] is not None:
            value = _decode_image(row["image"])
        elif row["timeseries"] is not None:
            value = _decode_numpy_array(row["timeseries"])
        else:
            value = row["text"]
        return LabeledMemory(
            value=value,
            label=row["label"],
            label_name=self._config.label_names[row["label"]] if row["label"] < len(self._config.label_names) else None,
            metadata=json.loads(row["metadata"]) if row["metadata"] is not None else {},
            source_id=row.get("source_id", None),
            embedding=np.array(row["embedding"], dtype=np.float32),
            memory_id=UUID(row["memory_id"]),
            memory_version=row.get("memory_version", 1),
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
            metrics=json.loads(row["metrics"]),
        )

    def _to_memory_lookup(self, row: dict[str, Any], query: np.ndarray) -> LabeledMemoryLookup:
        memory = self._to_memory(row)
        return LabeledMemoryLookup(**memory.__dict__, lookup_score=float(np.dot(query, memory.embedding)))


class ScoredMemorysetLanceDBRepository(BaseMemorysetLanceDBRepository[ScoredMemory, ScoredMemoryLookup]):
    def _get_schema_fields(self, embedding_model_dim: int) -> list[pa.Field]:
        return [
            pa.field("text", pa.string()),
            pa.field("image", pa.binary()),
            pa.field("score", pa.float32()),
            pa.field("metadata", pa.string()),
            pa.field("metrics", pa.string()),
            pa.field("memory_id", pa.string()),
            pa.field("memory_version", pa.int64()),
            pa.field("source_id", pa.string()),
            pa.field("embedding", pa.list_(pa.float32(), list_size=embedding_model_dim)),
            pa.field("created_at", pa.string()),
            pa.field("updated_at", pa.string()),
        ]

    def _prepare_for_insert(self, memory: ScoredMemory) -> dict[str, Any]:
        return {
            "text": memory.value if isinstance(memory.value, str) else None,
            "image": _encode_image(memory.value) if isinstance(memory.value, Image.Image) else None,
            "score": memory.score,
            "metadata": json.dumps(memory.metadata) if memory.metadata is not None else "{}",
            "memory_id": str(memory.memory_id),
            "memory_version": memory.memory_version,
            "source_id": str(memory.source_id) if memory.source_id is not None else None,
            "embedding": memory.embedding,
            "created_at": (
                memory.created_at.isoformat()
                if memory.created_at is not None
                else datetime.now(timezone.utc).isoformat()
            ),
            "updated_at": (
                memory.updated_at.isoformat()
                if memory.updated_at is not None
                else datetime.now(timezone.utc).isoformat()
            ),
            "metrics": json.dumps(memory.metrics or {}),
        }

    def _to_memory(self, row: dict[str, Any]) -> ScoredMemory:
        return ScoredMemory(
            value=_decode_image(row["image"]) if row["image"] is not None else row["text"],
            score=row["score"],
            metadata=json.loads(row["metadata"]) if row["metadata"] is not None else {},
            source_id=row.get("source_id", None),
            embedding=np.array(row["embedding"], dtype=np.float32),
            memory_id=UUID(row["memory_id"]),
            memory_version=row.get("memory_version", 1),
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
            metrics=json.loads(row["metrics"]),
        )

    def _to_memory_lookup(self, row: dict[str, Any], query: np.ndarray) -> ScoredMemoryLookup:
        memory = self._to_memory(row)
        return ScoredMemoryLookup(**memory.__dict__, lookup_score=float(np.dot(query, memory.embedding)))
