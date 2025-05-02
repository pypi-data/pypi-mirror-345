from __future__ import annotations

import logging
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from functools import lru_cache
from itertools import islice
from typing import (
    Any,
    Callable,
    Iterable,
    Iterator,
    Literal,
    Type,
    TypeVar,
    cast,
    overload,
)
from uuid import UUID

import numpy as np
import PIL.Image as pil
from datasets import ClassLabel, Dataset, Features, Image, Sequence, Value
from networkx import Graph, connected_components
from pandas import DataFrame
from tqdm.auto import tqdm
from uuid_utils.compat import uuid7

from ..embedding import EmbeddingModel, EmbeddingModelContext
from ..utils.dataset import parse_dataset, parse_label_names
from ..utils.progress import OnProgressCallback, safely_call_on_progress
from ..utils.pydantic import UNSET, UUID7, Metadata, Vector
from .memory_types import (
    InputType,
    InputTypeList,
    LabeledMemory,
    LabeledMemoryInsert,
    LabeledMemoryLookup,
    LabeledMemoryLookupColumnResult,
    LabeledMemoryMetrics,
    LabeledMemoryUpdate,
    LookupReturnType,
    Memory,
    MemoryInsert,
    MemoryLookup,
    MemoryMetrics,
    MemoryUpdate,
    ScoredMemory,
    ScoredMemoryInsert,
    ScoredMemoryLookup,
    ScoredMemoryLookupColumnResult,
    ScoredMemoryUpdate,
)
from .repository import (
    FilterItem,
    FilterItemTuple,
    MemorysetConfig,
    MemorysetRepository,
)
from .repository_lancedb import (
    BaseMemorysetLanceDBRepository,
    LabeledMemorysetLanceDBRepository,
    ScoredMemorysetLanceDBRepository,
)
from .repository_memory import (
    BaseMemorysetInMemoryRepository,
    LabeledMemorysetInMemoryRepository,
    ScoredMemorysetInMemoryRepository,
)
from .repository_milvus import (
    BaseMemorysetMilvusRepository,
    LabeledMemorysetMilvusRepository,
    ScoredMemorysetMilvusRepository,
)

logging.basicConfig(level=logging.INFO)

# Type variables for the base memoryset class
TInsert = TypeVar("TInsert")  # e.g., LabeledMemoryInsert or ScoredMemoryInsert
TUpdate = TypeVar("TUpdate")  # e.g., LabeledMemoryUpdate or ScoredMemoryUpdate
TLookupColumnResult = TypeVar(
    "TLookupColumnResult"
)  # e.g., LabeledMemoryLookupColumnResult or ScoredMemoryLookupColumnResult


class BaseMemoryset[
    TMemory: Memory,
    TLookup: MemoryLookup,
    TInsert: MemoryInsert,
    TUpdate: MemoryUpdate,
    TLookupColumnResult,
](ABC):
    """Base class defining the interface for all memoryset types."""

    repository: MemorysetRepository
    """Storage backend used to persist the memoryset"""

    embedding_model: EmbeddingModel
    """Embedding model used to generate embeddings for semantic similarity search"""

    config: MemorysetConfig

    DEFAULT_TABLE_NAME = "memories"

    _embedding_context: EmbeddingModelContext | None

    def _init_base(
        self,
        location: str | MemorysetRepository,
        *,
        embedding_model: EmbeddingModel | None = None,
        config: MemorysetConfig | None = None,
    ) -> None:
        """Common initialization logic for all memoryset types"""
        disconnected_repository = self.repository_from_uri(location) if isinstance(location, str) else location
        config = config if config is not None else disconnected_repository.get_config()
        if config is None:
            if embedding_model is None:
                raise ValueError("Embedding model must be specified when creating a new memoryset.")
            self.embedding_model = embedding_model
            self.config = self._create_config(embedding_model)
        else:
            if embedding_model and embedding_model.path != config.embedding_model_name:
                raise ValueError(
                    f"Given embedding model ({embedding_model.path}) does not match previously used embedding model ({config.embedding_model_name})."
                )
            self.embedding_model = embedding_model or EmbeddingModel(
                config.embedding_model_name,
                max_seq_length_override=config.embedding_model_max_seq_length_override,
            )
            self.config = config
        self.repository = disconnected_repository.connect(self.config)
        if self.embedding_model.uses_context:
            # NOTE: To avoid loading all memories into memory, we only load a sample of 10000 memories
            context = list(islice(self, 10000))

            self._embedding_context = (
                self.embedding_model.compute_context([m.value for m in context if isinstance(m.value, str)])
                if len(self) > 10
                else None
            )

    @abstractmethod
    def _create_config(self, embedding_model: EmbeddingModel) -> MemorysetConfig:
        """Create the appropriate config for this memoryset type"""
        pass

    @classmethod
    @abstractmethod
    def _get_milvus_repo_class(cls) -> Type[BaseMemorysetMilvusRepository[TMemory, TLookup]]:
        pass

    @classmethod
    @abstractmethod
    def _get_lancedb_repo_class(cls) -> Type[BaseMemorysetLanceDBRepository[TMemory, TLookup]]:
        pass

    @classmethod
    @abstractmethod
    def _get_inmemory_repo_class(cls) -> Type[BaseMemorysetInMemoryRepository[TMemory, TLookup]]:
        pass

    @classmethod
    def repository_from_uri(cls, uri: str) -> MemorysetRepository[TMemory, TLookup]:
        if not cls._is_database_uri(uri):
            if "MILVUS_URL" in os.environ and os.environ["MILVUS_URL"]:
                database_uri = os.environ["MILVUS_URL"]
                logging.info(f"Using `MILVUS_URL` env var for memoryset `{database_uri}#{uri}`")
                return cls._get_milvus_repo_class()(collection_name=uri, database_uri=database_uri)
            elif "LANCEDB_URI" in os.environ and os.environ["LANCEDB_URI"]:
                database_uri = os.environ["LANCEDB_URI"]
                logging.info(f"Using `LANCEDB_URI` env var for memoryset `{database_uri}#{uri}`")
                return cls._get_lancedb_repo_class()(collection_name=uri, database_uri=database_uri)
            else:
                logging.error("URI only contains collection name and no `MILVUS_URL` or `LANCEDB_URI` env var present")
                # for lighthouse testing we still want to return a milvus repository that we can mock out
                return cls._get_milvus_repo_class()(collection_name=uri, database_uri="fake")
        uri = uri.replace("file://", "").replace("file:", "")
        database_uri, collection_name = uri.split("#") if "#" in uri else (uri, cls.DEFAULT_TABLE_NAME)
        if database_uri == "memory:":
            return cls._get_inmemory_repo_class()(collection_name=collection_name)
        elif "milvus" in database_uri:
            logging.info(f"Inferring Milvus storage backend from URI: {database_uri}")
            return cls._get_milvus_repo_class()(collection_name=collection_name, database_uri=database_uri)
        else:
            logging.info(f"Inferring LanceDB storage backend from URI: {database_uri}")
            return cls._get_lancedb_repo_class()(collection_name=collection_name, database_uri=database_uri)

    @staticmethod
    def _is_database_uri(uri: str) -> bool:
        """Check if a given URI is a database URI."""
        return ".db" in uri or uri.startswith("http") or uri.startswith("memory:")

    @property
    def uri(self) -> str:
        """URI where the memoryset is stored."""
        return self.repository.database_uri + "#" + self.repository.collection_name

    def reset(self):
        """Remove all memories and reinitialize."""
        self.repository.reset(self.config)

    def to_list(self, limit: int | None = None) -> list[TMemory]:
        """Get a list of all memories."""
        return self.repository.list(limit=limit)

    def to_pandas(self, limit: int | None = None) -> DataFrame:
        """Get a pandas DataFrame representation."""
        return DataFrame([m.model_dump() for m in self.repository.list(limit=limit)])

    def count(self, filters: list[FilterItem] | list[FilterItemTuple] = []) -> int:
        """Count memories matching filters."""
        return self.repository.count(filters=FilterItem.from_tuple_list(filters))

    @classmethod
    def drop(cls, uri: str):
        """
        Drop the memoryset and its config from the database.

        Args:
            uri: URI where the memoryset is stored (e.g. `"file:~/.orca/milvus.db#my_memoryset"`) or
                just the collection name (e.g. `"my_memoryset"`) if a `MILVUS_URL` or `LANCEDB_URI`
                environment variable is set.
        """
        cls.repository_from_uri(uri).drop()

    @classmethod
    def exists(cls, uri: str) -> bool:
        """
        Check if a memoryset exists.

        Args:
            uri: URI where the memoryset is stored (e.g. `"file:~/.orca/milvus.db#my_memoryset"`) or
                just the collection name (e.g. `"my_memoryset"`) if a `MILVUS_URL` or `LANCEDB_URI`
                environment variable is set.

        Returns:
            True if the memoryset exists, False otherwise.
        """
        return cls.repository_from_uri(uri).get_config() is not None

    @abstractmethod
    def __init__(
        self,
        location: str | MemorysetRepository,
        *,
        embedding_model: EmbeddingModel | None = None,
        config: MemorysetConfig | None = None,
    ):
        """Initialize a memoryset."""
        pass

    @abstractmethod
    def to_dataset(self, **kwargs) -> Dataset:
        """Get a Dataset representation."""
        pass

    def query(
        self,
        *,
        limit: int | None = None,
        offset: int | None = None,
        filters: list[FilterItem] | list[FilterItemTuple] = [],
    ) -> list[TMemory]:
        """
        Query the memoryset for memories that match the query.

        Args:
            limit: Maximum number of memories to return.
            offset: Number of memories to skip.
            filters: Filters to apply to the query.

        Returns:
            List of memories that match the query.
        """
        return self.repository.list(limit=limit, offset=offset, filters=FilterItem.from_tuple_list(filters))

    def _embed(self, values: InputTypeList, use_cache: bool = True, **kwargs) -> list[Vector]:
        return self.embedding_model.embed(
            values,
            context=self._embedding_context if self.embedding_model.uses_context else None,
            use_cache=use_cache,
            **kwargs,
        )

    @abstractmethod
    def insert(self, dataset: Dataset | list[TMemory] | list[TInsert] | list[dict], **kwargs) -> list[UUID]:
        """Insert new memories."""
        pass

    @abstractmethod
    def lookup(
        self,
        query: InputType | InputTypeList | list[Vector],
        *,
        count: int = 1,
        exclude_exact_match: bool = False,
        return_type: LookupReturnType | str = LookupReturnType.ROWS,
        use_cache: bool = True,
    ) -> list[list[TLookup]] | list[TLookup] | TLookupColumnResult:  # Any for column results
        """Look up similar memories."""
        pass

    @abstractmethod
    def get(self, memory_ids: UUID | list[UUID]) -> TMemory | None | list[TMemory | None]:
        """Get memories by ID."""
        pass

    @abstractmethod
    def update(self, updates: TUpdate | list[TUpdate]) -> TMemory | None | list[TMemory | None]:
        """Update existing memories."""
        pass

    @abstractmethod
    def _update_multi(
        self,
        updates: list[TUpdate],
    ) -> dict[UUID, TMemory]:
        """Update multiple memories at once."""
        pass

    def delete(self, memory_ids: UUID | Iterable[UUID]) -> bool:
        """
        Delete a memory from the memoryset.

        Args:
            memory_ids: The UUID of the memory to delete, or a list of such UUIDs.
        Returns:
            True if a memory was deleted, False otherwise.
        """
        if isinstance(memory_ids, UUID):
            return self.repository.delete(memory_ids)
        return self.repository.delete_multi(list(memory_ids))

    @abstractmethod
    def _prepare_destination(self, destination: str | MemorysetRepository, config: MemorysetConfig) -> BaseMemoryset:
        """Prepare a destination memoryset for operations like filter/map/clone."""
        pass

    @abstractmethod
    def filter(
        self,
        fn: Callable[[TMemory], bool],
        destination: str | MemorysetRepository,
        *,
        show_progress_bar: bool = True,
    ) -> BaseMemoryset:
        """Filter memories into a new memoryset."""
        pass

    @abstractmethod
    def map(
        self,
        fn: Callable[[TMemory], dict[str, Any]],
        destination: str | MemorysetRepository,
        *,
        show_progress_bar: bool = True,
    ) -> BaseMemoryset:
        """Map memories into a new memoryset."""
        pass

    @abstractmethod
    def clone(
        self,
        destination: str | MemorysetRepository,
        *,
        embedding_model: EmbeddingModel | None = None,
        limit: int | None = None,
        offset: int | None = None,
        batch_size: int = 32,
        show_progress_bar: bool = True,
        on_progress: OnProgressCallback | None = None,
    ) -> BaseMemoryset:
        """Clone the memoryset."""
        pass

    def __iter__(self) -> Iterator[TMemory]:
        """
        Allow iterating over the memories.
        """
        return self.repository.iterator()

    def __len__(self) -> int:
        return self.repository.count()

    @property
    def num_rows(self) -> int:
        """Number of memories in the memoryset."""
        return len(self)

    @overload
    def __getitem__(self, index: slice) -> list[TMemory]:
        pass

    @overload
    def __getitem__(self, index: int | str | UUID) -> TMemory:
        pass

    def __getitem__(self, index: slice | int | UUID | str) -> list[TMemory] | TMemory:
        if isinstance(index, int):
            if index >= len(self):
                raise IndexError(f"Index {index} out of bounds for memoryset with length {len(self)}")
            return self.repository.list(offset=index, limit=1)[0]
        if isinstance(index, UUID) or isinstance(index, str):
            memory = self.repository.get(index if isinstance(index, UUID) else UUID(index))
            if memory is None:
                raise IndexError(f"Memory with id {index} not found")
            return memory
        if isinstance(index, slice):
            if index.step is not None:
                raise NotImplementedError("Stepping through a memoryset is not supported")

            start = index.start or 0
            stop = index.stop or len(self)
            slice_length = stop - start

            return self.repository.list(offset=start, limit=slice_length)

        raise ValueError(f"Invalid index type: {type(index)}")

    @property
    def value_type(self) -> Literal["string", "image", "timeseries"]:
        match self[0].value:
            case str():
                return "string"
            case pil.Image():
                return "image"
            case np.ndarray():
                return "timeseries"
            case _:
                raise ValueError(f"Unknown value type: {type(self[0].value)}")


class LabeledMemoryset(
    BaseMemoryset[
        LabeledMemory, LabeledMemoryLookup, LabeledMemoryInsert, LabeledMemoryUpdate, LabeledMemoryLookupColumnResult
    ]
):
    @classmethod
    def _get_milvus_repo_class(cls) -> Type[LabeledMemorysetMilvusRepository]:
        return LabeledMemorysetMilvusRepository

    @classmethod
    def _get_lancedb_repo_class(cls) -> Type[LabeledMemorysetLanceDBRepository]:
        return LabeledMemorysetLanceDBRepository

    @classmethod
    def _get_inmemory_repo_class(cls) -> Type[LabeledMemorysetInMemoryRepository]:
        return LabeledMemorysetInMemoryRepository

    @classmethod
    @lru_cache(maxsize=100)
    def connect(cls, uri: str) -> LabeledMemoryset:
        """
        Connect to an existing memoryset.

        Args:
            uri: URI where the memoryset is stored (e.g. `"file:~/.orca/milvus.db#my_memoryset"`) or
                just the collection name (e.g. `"my_memoryset"`) if a `MILVUS_URL` or `LANCEDB_URI`
                environment variable is set.

        Returns:
            A memoryset at the given location

        Raises:
            ValueError: if the memoryset does not exist at the given location
        """
        repository = cls.repository_from_uri(uri)
        config = repository.get_config()
        if config is None:
            raise ValueError(f"Memoryset does not exist at {uri}")
        return LabeledMemoryset(repository, config=config)

    def __init__(
        self,
        location: str | MemorysetRepository,
        *,
        embedding_model: EmbeddingModel | None = None,
        label_names: list[str] | None = None,
        config: MemorysetConfig | None = None,
    ):
        """
        Initialize a labeled memoryset

        Args:
            location: location where the memoryset is stored. Can either be directly a storage
                backend instance, or a URI like `"file:~/.orca/milvus.db#my_memoryset"`, or just a
                collection name like `"my_memoryset"` if a `MILVUS_URL` or `LANCEDB_URI` environment
                variable is set.
            embedding_model: Embedding model to use for semantic similarity search. When reconnecting
                to an existing memoryset the correct embedding model will automatically be loaded,
                otherwise an embedding model must be specified.
            label_names: List with label names, where each index maps the integer value of the label
                to the name of the label. When reconnecting to an existing memoryset, the label names
                will be loaded, otherwise the label names should be specified.
        """
        self._label_names = label_names
        self._init_base(location, embedding_model=embedding_model, config=config)

    def _create_config(self, embedding_model: EmbeddingModel) -> MemorysetConfig:
        if self._label_names is None:
            logging.warning("No label names specified, memoryset will not be able to resolve label names.")
        return MemorysetConfig(
            label_names=self._label_names or [],
            embedding_dim=embedding_model.embedding_dim,
            embedding_model_name=embedding_model.path,
            embedding_model_max_seq_length_override=embedding_model.max_seq_length_override,
        )

    @property
    def label_names(self) -> list[str]:
        """List of label names, where each index maps the integer value of the label to the name of the label."""
        return self.config.label_names

    @label_names.setter
    def label_names(self, label_names: list[str]):
        self.config = self.repository.update_config(
            MemorysetConfig(**(self.config.model_dump() | {"label_names": label_names}))
        )

    def get_label_name(self, label: int) -> str | None:
        """Get the name for a label value based on the set label names."""
        return self.label_names[label] if label < len(self.label_names) else None

    def __repr__(self) -> str:
        return (
            "LabeledMemoryset({\n"
            f"    uri: {self.uri},\n"
            f"    embedding_model: {self.embedding_model},\n"
            f"    num_rows: {len(self)},\n"
            f"    label_names: {self.label_names},\n"
            "})"
        )

    def to_dataset(self, *, value_column: str = "value", label_column: str = "label", **kwargs) -> Dataset:
        """
        Get a [Dataset][datasets.Dataset] representation of the memoryset.

        Args:
            value_column: name of the column containing the values
            label_column: name of the column containing the labels

        Returns:
            Dataset of the memories with value, label, embedding, memory_id, memory_version, source_id, metadata, and metrics features
        """
        value_type = self.value_type

        if value_type == "string":
            value_feature = Value(dtype="string")
        elif value_type == "image":
            value_feature = Image()
        else:  # time series
            value_feature = Sequence(feature=Value(dtype="float32"))

        return Dataset.from_list(
            [
                {
                    value_column: memory.value,
                    label_column: memory.label,
                    "embedding": memory.embedding.tolist(),
                    "memory_id": str(memory.memory_id),
                    "memory_version": memory.memory_version,
                    "source_id": memory.source_id,
                    "metadata": memory.metadata,
                    "metrics": memory.metrics,
                }
                for memory in self
            ],
            features=Features(
                {
                    value_column: value_feature,
                    label_column: ClassLabel(names=self.label_names) if self.label_names else Value(dtype="int64"),
                    "embedding": Sequence(feature=Value(dtype="float32")),
                    "memory_id": Value(dtype="string"),
                    "memory_version": Value(dtype="int64"),
                    "source_id": Value(dtype="string"),
                    "metadata": dict(),  # this defines that the feature is of type dict
                    "metrics": dict(),  # this defines that the feature is of type dict
                }
            ),
        )

    @property
    def num_classes(self) -> int:
        """Number of unique labels in the memoryset."""
        if self.label_names:
            return len(self.label_names)
        logging.warning(
            f"Could not find label names in memoryset config, counting unique labels instead for {self.uri}. This may be slow."
        )
        return len(set(mem.label for mem in self))

    def insert(
        self,
        # TODO: pass iterables when calling this from copy, map, list to save machine memory
        dataset: Dataset | list[LabeledMemory] | list[LabeledMemoryInsert] | list[dict],
        *,
        value_column: str = "value",
        label_column: str = "label",
        source_id_column: str | None = None,
        other_columns_as_metadata: bool = True,
        show_progress_bar: bool = True,
        compute_embeddings: bool = True,
        batch_size: int = 32,
        only_if_empty: bool = False,
        on_progress: OnProgressCallback | None = None,
        **kwargs,
    ) -> list[UUID]:
        """
        Inserts a dataset into the LabeledMemoryset database.

        For dict-like or list of dict-like datasets, there must be a `label` key and one of the following keys: `text`, `image`, or `value`.
        If there are only two keys and one is `label`, the other will be inferred to be `value`.

        For list-like datasets, the first element of each tuple must be the value and the second must be the label.

        Args:
            dataset: data to insert into the memoryset
            label_column: name of the dataset column containing the labels
            value_column: name of the dataset column containing the values
            source_id_column: name of a dataset column containing ids used for the memories in an external system
            other_columns_as_metadata: collect all other column values in the metadata dictionary
            show_progress_bar: whether to show a progress bar
            compute_embeddings: optionally disable embedding computation when copying labeled memories
            batch_size: the batch size when creating embeddings from memories
            only_if_empty: whether to skip the insert if the memoryset is not empty
            on_progress: callback function to call with the already inserted and total number of rows

        Examples:
            >>> dataset = Dataset.from_list([
            ...    {"text": "text 1", "label": 0},
            ...    {"text": "text 2", "label": 1},
            ... ])
            >>> memoryset = LabeledMemoryset("file:///path/to/memoryset")
            >>> memoryset.insert(dataset)
        """
        if only_if_empty and len(self):
            logging.warning("Skipping insert: `only_if_empty` is True and memoryset is not empty.")
            return []

        insert_num_rows = len(dataset)
        if insert_num_rows == 0:
            logging.warning("Nothing to insert")
            return []

        if not compute_embeddings and not isinstance(dataset, list) and not isinstance(dataset[0], LabeledMemory):
            raise ValueError("compute_embeddings can only be disabled when inserting LabeledMemory objects")

        # this type mirrors LabeledMemory with optional embedding which is computed at the end
        @dataclass
        class InsertItem:
            value: InputType
            label: int
            metadata: Metadata = field(default_factory=dict)
            source_id: str | None = None
            embedding: Vector | None = None
            memory_id: UUID7 = field(default_factory=uuid7)
            memory_version: int = 1
            created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
            updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
            metrics: LabeledMemoryMetrics = field(default_factory=lambda: LabeledMemoryMetrics())
            label_name: None = None  # computed from memoryset.label_names and label

        if isinstance(dataset, list) and isinstance(dataset[0], dict):
            dataset = Dataset.from_list(cast(list[dict], dataset))
        else:
            dataset = cast(Dataset | list[LabeledMemory] | list[LabeledMemoryInsert], dataset)

        if isinstance(dataset, Dataset):
            label_names = parse_label_names(dataset, label_column=label_column)
            if self.label_names == [] and label_names is not None:
                self.label_names = label_names
            parsed_dataset = parse_dataset(
                dataset,
                value_column=value_column,
                label_column=label_column,
                source_id_column=source_id_column,
                other_columns_as_metadata=other_columns_as_metadata,
                label_names=self.label_names or None,
            )
            insert_items = [
                InsertItem(
                    value=item["value"],
                    label=item["label"],
                    metadata=item["metadata"] if "metadata" in item else {},
                    source_id=item["source_id"] if "source_id" in item else None,
                )
                for item in cast(list[dict], parsed_dataset)
            ]
        else:
            insert_items = [
                (
                    InsertItem(**m.model_dump())
                    if isinstance(m, LabeledMemory)
                    else InsertItem(
                        value=m.value,
                        label=m.label,
                        metadata=m.metadata,
                        source_id=m.source_id,
                    )
                )
                for m in dataset
            ]

        # Some embedding models use a context to customize the embeddings for a specific task
        # if the model uses it and there are enough memories then update the context
        if self.embedding_model.uses_context:
            current_num_rows = len(self)
            if insert_num_rows > 10 and insert_num_rows > current_num_rows / 5:
                # the dataset changed by more than 20% and at least 10 items
                insert_values = [m.value for m in insert_items]
                current_values = [m.value for m in self]

                self._embedding_context = self.embedding_model.compute_context(insert_values + current_values)

        if compute_embeddings and insert_num_rows > 0 and not isinstance(insert_items[0].value, np.ndarray):
            # Sort the data by text length / image size so that batches are created from similar
            # length samples to minimize padding and thus the overall computational complexity.
            insert_items = sorted(
                insert_items,
                key=lambda x: (sum(x.value.size) if isinstance(x.value, pil.Image) else len(x.value)),
                reverse=True,
            )

        for i in tqdm(range(0, insert_num_rows, batch_size), disable=not show_progress_bar):
            safely_call_on_progress(on_progress, i, insert_num_rows)
            item_batch = insert_items[i : i + batch_size]

            # compute embeddings if not already provided
            if compute_embeddings:
                embeddings = self._embed([m.value for m in item_batch], value_kind="document", batch_size=batch_size)
            else:
                embeddings: list[Vector] = []
                for item in item_batch:
                    embedding = item.embedding
                    assert embedding is not None
                    embeddings.append(embedding)
            # insert fully populated labeled memory objects
            self.repository.insert(
                [
                    LabeledMemory(
                        value=item.value,
                        label=item.label,
                        embedding=embedding,
                        memory_id=item.memory_id,
                        memory_version=item.memory_version,
                        source_id=item.source_id,
                        metadata=item.metadata,
                        metrics=item.metrics,
                        created_at=item.created_at,
                        updated_at=item.updated_at,
                        label_name=item.label_name,
                    )
                    for item, embedding in zip(item_batch, embeddings)
                ]
            )
        safely_call_on_progress(on_progress, insert_num_rows, insert_num_rows)
        return [m.memory_id for m in insert_items]

    @overload
    def lookup(
        self,
        query: InputTypeList,
        *,
        exclude_exact_match: bool = False,
        return_type: Literal[LookupReturnType.ROWS, "rows"] = LookupReturnType.ROWS,
        count: int = 1,
        use_cache: bool = True,
    ) -> list[list[LabeledMemoryLookup]]:
        pass

    @overload
    def lookup(
        self,
        query: InputType,
        *,
        exclude_exact_match: bool = False,
        return_type: Literal[LookupReturnType.ROWS, "rows"] = LookupReturnType.ROWS,
        count: int = 1,
        use_cache: bool = True,
    ) -> list[LabeledMemoryLookup]:
        pass

    @overload
    def lookup(
        self,
        query: InputTypeList | InputType,
        *,
        exclude_exact_match: bool = False,
        return_type: Literal["columns", LookupReturnType.COLUMNS],
        count: int = 1,
        use_cache: bool = True,
    ) -> LabeledMemoryLookupColumnResult:
        pass

    def lookup(  # noqa: C901
        self,
        query: InputType | InputTypeList,
        *,
        count: int = 1,
        exclude_exact_match: bool = False,
        return_type: LookupReturnType | str = LookupReturnType.ROWS,
        use_cache: bool = True,
    ) -> list[list[LabeledMemoryLookup]] | list[LabeledMemoryLookup] | LabeledMemoryLookupColumnResult:
        """
        Retrieves the most similar memories to the query from the memoryset.

        Args:
            query: The query to retrieve memories for. Can be a single value or a list of values.
            count: The number of memories to retrieve.
            exclude_exact_match: Whether to exclude a maximum of one exact match from the results.
            return_type: Whether to return a list of memory lookups or a dictionary of columns.
            use_cache: Whether to use the cache to speed up lookups. This controls both reading from the
                cache and storing results in the cache.

        Returns:
            The memory lookup results for the query. If the return type is columns, this will be a
                dictionary of columns containing the embeddings for the inputs and all the query
                results. If a single input value is passed the result will be a list of memory
                lookups. If a list of input values is passed the result will be a list of lists
                of memory lookups.

        Examples:
            Retrieve the most similar memory to a query
            >>> memories = memoryset.lookup("happy")
            [LabeledMemoryLookup(
                value='im feeling quite joyful today',
                label=0,
                embedding=<array.float32(768,)>,
                memory_id=1027,
                memory_version=1,
                lookup_score=0.7021239399909973,
            )]

            Retrieve memories for a batch of queries
            >>> res = memoryset.lookup(["happy", "angry"], count=3, return_type="columns")
            >>> res["memories_values"]
            [['joyful', 'brimming', 'ecstatic'], ['frustrated', 'annoyed', 'disheartened']]
            >>> res["memories_labels"]
            [[0, 0, 0], [1, 1, 1]]
            >>> res["input_embeddings"]
            [array([...], dtype=float32), array([...], dtype=float32)]
            >>> res["memories_embeddings"]
            [[array([...], dtype=float32), array([...], dtype=float32), array([...], dtype=float32)],
             [array([...], dtype=float32), array([...], dtype=float32), array([...], dtype=float32)]]
            >>> res["memories_lookup_scores"]
            [[0.7021238803863525, 0.6859346628189087, 0.6833891272544861],
             [0.7464785575866699, 0.7334979772567749, 0.7299057245254517]]
        """
        # Verify inputs
        if count < 0:
            raise ValueError("lookup count must be greater than or equal to 0")

        if exclude_exact_match:
            # to exclude the exact match, we fetch one extra memory and then remove the top hit
            count += 1

        if len(self) < count:
            raise ValueError(f"Requested {count} memories but memoryset only contains {len(self)} memories")

        # create embedded query matrix of shape num_queries x embedding_dim
        embedded_queries = self._embed(query if isinstance(query, list) else [query], use_cache=use_cache)

        memory_lookups_batch = self._perform_lookup(embedded_queries, count=count, use_cache=use_cache)

        if exclude_exact_match:
            self._exclude_exact_lookup_matches(memory_lookups_batch, query)

        # return correctly formatted results
        if return_type == "columns":
            return self._format_lookup_column_result(memory_lookups_batch, embedded_queries)

        if not isinstance(query, list):
            assert len(memory_lookups_batch) == 1
            return memory_lookups_batch[0]

        return memory_lookups_batch

    @overload
    def lookup_by_embedding(
        self,
        query: Vector,
        *,
        count: int = 1,
        return_type: Literal[LookupReturnType.ROWS, "rows"] = LookupReturnType.ROWS,
        use_cache: bool = True,
    ) -> list[LabeledMemoryLookup]:
        ...

    @overload
    def lookup_by_embedding(
        self,
        query: list[Vector],
        *,
        count: int = 1,
        return_type: Literal[LookupReturnType.ROWS, "rows"] = LookupReturnType.ROWS,
        use_cache: bool = True,
    ) -> list[list[LabeledMemoryLookup]]:
        ...

    @overload
    def lookup_by_embedding(
        self,
        query: Vector | list[Vector],
        *,
        return_type: Literal["columns", LookupReturnType.COLUMNS],
        count: int = 1,
        use_cache: bool = True,
    ) -> LabeledMemoryLookupColumnResult:
        pass

    def lookup_by_embedding(
        self,
        query: Vector | list[Vector],
        *,
        count: int = 1,
        return_type: LookupReturnType | str = LookupReturnType.ROWS,
        use_cache: bool = True,
    ) -> list[list[LabeledMemoryLookup]] | list[LabeledMemoryLookup] | LabeledMemoryLookupColumnResult:
        """
        Retrieves the most similar memories to the query embeddings from the memoryset.

        Args:
            query: The embedding or embeddings to retrieve memories for. Expects an ndarray of shape
                (embedding_dim,) for a single query or a list of such ndarrays for multiple queries.
            count: The number of memories to retrieve.
            return_type: Whether to return a list of memory lookups or a dictionary of columns.
            use_cache: Whether to use the cache to speed up lookups. This controls both reading from the
                cache and storing results in the cache.

        Returns:
            The memory lookup results for the query. If the return type is columns, this will be a
                dictionary of columns containing the embeddings for the inputs and all the query
                results. If a single input value is passed the result will be a list of memory
                lookups. If a list of input values is passed the result will be a list of lists
                of memory lookups.
        """

        # Verify inputs
        if count < 0:
            raise ValueError("lookup count must be greater than or equal to 0")

        if len(self) < count:
            raise ValueError(f"Requested {count} memories but memoryset only contains {len(self)} memories")

        if not isinstance(query, list):
            query = [query]
            single_lookup = True
        else:
            single_lookup = False

        memory_lookups_batch = self._perform_lookup(query, count=count, use_cache=use_cache)

        # return correctly formatted results
        if return_type == "columns":
            return self._format_lookup_column_result(memory_lookups_batch, query)

        if single_lookup:
            assert len(memory_lookups_batch) == 1
            return memory_lookups_batch[0]

        return memory_lookups_batch

    def _perform_lookup(
        self, embedded_queries: list[Vector], count: int, use_cache: bool
    ) -> list[list[LabeledMemoryLookup]]:
        if count == 0:
            return [[] for _ in range(len(embedded_queries))]
        memory_lookups_batch = self.repository.lookup(embedded_queries, k=count, use_cache=use_cache)
        if not all(len(memories) == count for memories in memory_lookups_batch):
            raise Exception("lookup failed to return the correct number of memories")
        return memory_lookups_batch

    def _exclude_exact_lookup_matches(
        self, memory_lookups_batch: list[list[LabeledMemoryLookup]], query: InputType | InputTypeList
    ):
        if isinstance(query, np.ndarray):
            raise ValueError("cannot exclude exact match when passing a numpy array as the query")
        for i, memory_lookups in enumerate(memory_lookups_batch):
            query_item = query[i] if isinstance(query, list) else query
            exact_match_count = 0
            for j, memory_lookup in enumerate(memory_lookups):
                if memory_lookup.value == query_item:
                    if exact_match_count == 0:
                        memory_lookups_batch[i] = memory_lookups[:j] + memory_lookups[j + 1 :]
                    exact_match_count += 1
            if exact_match_count == 0:
                memory_lookups_batch[i] = memory_lookups[:-1]
            if exact_match_count > 1:
                logging.warning(
                    f"Found {exact_match_count} exact matches for '{query_item}' in the memoryset, run find duplicate analysis to remove duplicates"
                )

    def _format_lookup_column_result(
        self,
        memory_lookups_batch: list[list[LabeledMemoryLookup]],
        embedded_queries: list[Vector],
    ) -> LabeledMemoryLookupColumnResult:
        return LabeledMemoryLookupColumnResult(
            input_embeddings=np.vstack(embedded_queries),
            memories_embeddings=np.array(
                [[m.embedding for m in memories] for memories in memory_lookups_batch], dtype=np.float32
            ),
            memories_labels=np.array(
                [[m.label for m in memories] for memories in memory_lookups_batch], dtype=np.int64
            ),
            memories_lookup_scores=np.array(
                [[m.lookup_score for m in memories] for memories in memory_lookups_batch], dtype=np.float32
            ),
            memories_values=[[m.value for m in memories] for memories in memory_lookups_batch],
            memories_label_names=[[m.label_name for m in memories] for memories in memory_lookups_batch],
            memories_ids=[[m.memory_id for m in memories] for memories in memory_lookups_batch],
            memories_versions=[[m.memory_version for m in memories] for memories in memory_lookups_batch],
            memories_metadata=[[m.metadata for m in memories] for memories in memory_lookups_batch],
            memories_metrics=[[m.metrics or {} for m in memories] for memories in memory_lookups_batch],
            memories_source_ids=[[m.source_id for m in memories] for memories in memory_lookups_batch],
            memories_created_ats=[[m.created_at for m in memories] for memories in memory_lookups_batch],
            memories_updated_ats=[[m.updated_at for m in memories] for memories in memory_lookups_batch],
        )

    @overload
    def get(self, memory_ids: UUID) -> LabeledMemory | None:
        pass

    @overload
    def get(self, memory_ids: list[UUID]) -> list[LabeledMemory | None]:
        pass

    def get(self, memory_ids: UUID | list[UUID]) -> LabeledMemory | None | list[LabeledMemory | None]:
        """
        Get a memory from the memoryset by its UUID or list of UUIDs.

        Args:
            memory_ids: The UUID of the memory to get, or a list of such UUIDs.
        Returns:
            The memory if it exists, otherwise None. If a list of memory ids is provided, it returns a list of memories.
        """

        if isinstance(memory_ids, list):
            memories_dict = self.repository.get_multi(memory_ids)
            return [memories_dict.get(m_id, None) for m_id in memory_ids]
        else:
            memories_dict = self.repository.get_multi([memory_ids])
            return memories_dict.get(memory_ids, None)

    @overload
    def update(self, updates: LabeledMemoryUpdate) -> LabeledMemory | None:
        pass

    @overload
    def update(self, updates: list[LabeledMemoryUpdate]) -> list[LabeledMemory | None]:
        pass

    def update(
        self, updates: LabeledMemoryUpdate | list[LabeledMemoryUpdate]
    ) -> LabeledMemory | None | list[LabeledMemory | None]:
        """
        Update a memory in the memoryset.

        Args:
            memory_ids: The UUID of the memory to update.
            updates: A dictionary containing the values to update in the memory.

        Returns:
            The updated memory if a memory was found and updated, otherwise None.
        """

        if isinstance(updates, list):
            updates_dict = self._update_multi(updates)
            memory_ids = [update.memory_id for update in updates]
            return [updates_dict.get(m_id, None) for m_id in memory_ids]
        else:
            updates_dict = self._update_multi([updates])
            return updates_dict.get(updates.memory_id, None)

    def _update_multi(
        self,
        updates: list[LabeledMemoryUpdate],
    ) -> dict[UUID, LabeledMemory]:
        memory_ids = [update.memory_id for update in updates]
        if len(memory_ids) != len(set(memory_ids)):
            raise ValueError("Duplicate memory ids in updates.")

        updates_dict = dict(zip(memory_ids, updates))

        existing_memories = self.repository.get_multi(memory_ids)

        if len(existing_memories) != len(memory_ids):
            missing_memory_ids = set(memory_ids) - set(existing_memories.keys())
            raise ValueError(f"{len(missing_memory_ids)} memories not found in memoryset: {missing_memory_ids}")

        updated_memories = {}
        embeddings_to_compute = {}

        for memory_id, existing_memory in existing_memories.items():
            update = updates_dict[memory_id]

            if update.metadata is None:
                # if metadata is explicitly set to None, reset the metadata field
                update.metadata = {}

            if update.metrics is None:
                # if metrics is explicitly set to None, reset the metrics field
                update.metrics = {}

            updated_memory = LabeledMemory(
                **(
                    existing_memory.model_dump()
                    | update.model_dump(exclude_unset=True, exclude={"memory_id"})
                    | dict(updated_at=datetime.now(timezone.utc))
                ),
            )

            if update.metadata:
                # if metadata is passed, merge it with the existing metadata
                updated_memory.metadata = existing_memory.metadata | update.metadata

            if update.metrics:
                # if metrics is passed, merge it with the existing metrics
                updated_memory.metrics = existing_memory.metrics | update.metrics

            if existing_memory.value != updated_memory.value:
                embeddings_to_compute[memory_id] = updated_memory.value

            if existing_memory.value != updated_memory.value or existing_memory.label != updated_memory.label:
                updated_memory.memory_version = existing_memory.memory_version + 1
                updated_memory.updated_at = datetime.now(timezone.utc)
                if update.metrics is UNSET:
                    updated_memory.metrics = {}

            updated_memories[memory_id] = updated_memory

        if embeddings_to_compute:
            embeddings_ids = list(embeddings_to_compute.keys())
            embeddings = self._embed([embeddings_to_compute[memory_id] for memory_id in embeddings_ids])
            for memory_id, embedding in zip(embeddings_ids, embeddings):
                updated_memories[memory_id].embedding = embedding

        return self.repository.upsert_multi(list(updated_memories.values()))

    def _prepare_destination(self, destination: str | MemorysetRepository, config: MemorysetConfig) -> LabeledMemoryset:
        if isinstance(destination, str) and not self._is_database_uri(destination):
            destination = f"{self.repository.database_uri}#{destination}"
        destination_memoryset = LabeledMemoryset(destination, config=config)
        if destination_memoryset.repository == self.repository:
            raise ValueError("Destination memoryset cannot be the same as the source memoryset.")
        if len(destination_memoryset) > 0:
            raise ValueError("Destination memoryset must be empty.")
        return destination_memoryset

    def filter(
        self,
        fn: Callable[[LabeledMemory], bool],
        destination: str | MemorysetRepository,
        *,
        show_progress_bar: bool = True,
    ) -> LabeledMemoryset:
        """
        Filter memories out from the current memoryset and store them in a new destination.

        Args:
            fn: Function that takes in the memory and returns a boolean indicating whether the
                memory should be included or not.
            destination: location where the filtered memoryset will be stored. Can either be
                a storage backend instance, or a URI like `"file:~/.orca/milvus.db#my_memoryset"`,
                or a table name like `"my_memoryset"` which will be created in the same database as
                the source memoryset.
            show_progress_bar: whether to show a progress bar

        Returns:
            The memoryset with the filtered memories at the given destination.

        Examples:
            Create a memoryset with a subset of memories that have some metadata:
            >>> memoryset = LabeledMemoryset("./lance.db#my_memoryset")
            >>> filtered_memoryset = memoryset.filter(
            ...     lambda m: m.metadata["key"] == "filter_value",
            ...     "./lance.db#my_filtered_memoryset"
            ... )
        """
        destination_memoryset = self._prepare_destination(destination, self.config)
        values_to_insert = [m for m in self if fn(m)]
        destination_memoryset.insert(values_to_insert, compute_embeddings=False, show_progress_bar=show_progress_bar)
        return destination_memoryset

    def map(
        self,
        fn: Callable[[LabeledMemory], dict[str, Any]],
        destination: str | MemorysetRepository,
        *,
        show_progress_bar: bool = True,
    ) -> LabeledMemoryset:
        """
        Apply updates to all the memories in the memoryset and store them in a new destination.

        Args:
            fn: Function that takes in the memory and returns a dictionary containing the values to
                update in the memory.
            destination: location where the updated memoryset will be stored. Can either be
                a storage backend instance, or a URI like `"file:~/.orca/milvus.db#my_memoryset"`,
                or a table name like `"my_memoryset"` which will be created in the same database as
                the source memoryset.
            show_progress_bar: whether to show a progress bar

        Returns:
            The memoryset with the changed memories at the given destination.

        Examples:
            Create a new memoryset with swapped labels
            >>> memoryset = LabeledMemoryset("./lance.db#my_memoryset")
            >>> swapped_memoryset = memoryset.map(
            ...     lambda m: dict(label=1 if m.label == 0 else 0),
            ...     "./lance.db#my_swapped_memoryset"
            ... )
        """

        def replace_fn(memory: LabeledMemory) -> LabeledMemory:
            # TODO: This function calculates embeddings one at a time. It should be optimized to calculate embeddings in batches.
            fn_result = fn(memory)
            if not isinstance(fn_result, dict):
                raise ValueError("Map function must return a dictionary with updates.")
            if "embedding" in fn_result:
                raise ValueError(
                    "Embedding cannot be updated. Memoryset automatically calculates embeddings as needed."
                )
            value_changed = "value" in fn_result and memory.value != fn_result["value"]
            label_changed = "label" in fn_result and memory.label != fn_result["label"]
            if value_changed:
                fn_result["embedding"] = destination_memoryset._embed([fn_result["value"]])[0]
            if value_changed or label_changed:
                fn_result["memory_version"] = memory.memory_version + 1
                fn_result["updated_at"] = datetime.now(timezone.utc)
            return LabeledMemory(**(memory.model_dump() | fn_result))

        destination_memoryset = self._prepare_destination(destination, self.config)
        mapped_memories = [replace_fn(memory) for memory in self]
        destination_memoryset.insert(
            mapped_memories,
            compute_embeddings=False,
            show_progress_bar=show_progress_bar,
        )
        return destination_memoryset

    def clone(
        self,
        destination: str | MemorysetRepository,
        *,
        embedding_model: EmbeddingModel | None = None,
        limit: int | None = None,
        offset: int | None = None,
        batch_size: int = 32,
        show_progress_bar: bool = True,
        on_progress: OnProgressCallback | None = None,
    ) -> LabeledMemoryset:
        """
        Clone the current memoryset into a new memoryset.

        Args:
            destination: location where the copied memoryset will be stored. Can either be
                a storage backend instance, or a URI like `"file:~/.orca/milvus.db#my_memoryset"`,
                or a table name like `"my_memoryset"` which will be created in the same database as
                the source memoryset.
            embedding_model: optional different embedding model to use for the cloned memoryset.
                When provided the memories will be re-embedded using the new embedding model. If not
                provided, the cloned memoryset will use the same embedding model as the current
                memoryset and the embeddings are not recomputed.
            limit: optional maximum number of memories to clone. If not provided, all memories will be cloned.
            batch_size: size of the batches to use for re-embedding the memories
            show_progress_bar: whether to show a progress bar
            on_progress: callback function to update the progress of the cloning process
        Returns:
            The memoryset that the memories were cloned into at the given destination.

        Examples:
            Clone a local memoryset into a hosted database:
            >>> memoryset = LabeledMemoryset("./lance.db#my_memoryset")
            >>> memoryset.clone("https://my_database.region.milvus.cloud#my_memoryset")

            Clone a local memoryset into a new table with a different embedding model:
            >>> memoryset = LabeledMemoryset("./lance.db#my_memoryset")
            >>> memoryset.clone("./lance.db#my_new_memoryset", embedding_model=EmbeddingModel.CLIP_BASE)
        """
        destination_memoryset = self._prepare_destination(
            destination,
            (
                self.config
                if embedding_model is None
                else MemorysetConfig(
                    label_names=self.config.label_names,
                    embedding_dim=embedding_model.embedding_dim,
                    embedding_model_name=embedding_model.path,
                    embedding_model_max_seq_length_override=embedding_model.max_seq_length_override,
                )
            ),
        )
        destination_memoryset.insert(
            self.repository.list(offset=offset, limit=limit),
            batch_size=batch_size,
            compute_embeddings=embedding_model is not None and embedding_model != self.embedding_model,
            show_progress_bar=show_progress_bar,
            on_progress=on_progress,
        )
        return destination_memoryset


class ScoredMemoryset(
    BaseMemoryset[
        ScoredMemory, ScoredMemoryLookup, ScoredMemoryInsert, ScoredMemoryUpdate, ScoredMemoryLookupColumnResult
    ]
):
    @classmethod
    def _get_milvus_repo_class(cls) -> Type[ScoredMemorysetMilvusRepository]:
        return ScoredMemorysetMilvusRepository

    @classmethod
    def _get_lancedb_repo_class(cls) -> Type[ScoredMemorysetLanceDBRepository]:
        return ScoredMemorysetLanceDBRepository

    @classmethod
    def _get_inmemory_repo_class(cls) -> Type[ScoredMemorysetInMemoryRepository]:
        return ScoredMemorysetInMemoryRepository

    @classmethod
    @lru_cache(maxsize=100)
    def connect(cls, uri: str) -> ScoredMemoryset:
        repository = cls.repository_from_uri(uri)
        config = repository.get_config()
        if config is None:
            raise ValueError(f"Scored memoryset does not exist at {uri}")
        return ScoredMemoryset(repository, config=config)

    def __init__(
        self,
        location: str | MemorysetRepository,
        *,
        embedding_model: EmbeddingModel | None = None,
        config: MemorysetConfig | None = None,
    ):
        self._init_base(location, embedding_model=embedding_model, config=config)

    def _create_config(self, embedding_model: EmbeddingModel) -> MemorysetConfig:
        return MemorysetConfig(
            label_names=[],  # Not used for scored memoryset
            embedding_dim=embedding_model.embedding_dim,
            embedding_model_name=embedding_model.path,
            embedding_model_max_seq_length_override=embedding_model.max_seq_length_override,
        )

    def __repr__(self) -> str:
        return (
            "ScoredMemoryset({\n"
            f"    uri: {self.uri},\n"
            f"    embedding_model: {self.embedding_model},\n"
            f"    num_rows: {len(self)},\n"
            "})"
        )

    def to_dataset(self, *, value_column: str = "value", score_column: str = "score", **kwargs) -> Dataset:
        return Dataset.from_list(
            [
                {
                    value_column: memory.value,
                    score_column: memory.score,
                    "embedding": memory.embedding.tolist(),
                    "memory_id": str(memory.memory_id),
                    "memory_version": memory.memory_version,
                    "source_id": memory.source_id,
                    "metadata": memory.metadata,
                    "metrics": memory.metrics,
                }
                for memory in self
            ],
            features=Features(
                {
                    value_column: Value(dtype="string") if self.value_type == "string" else Image(),
                    score_column: Value(dtype="float32"),
                    "embedding": Sequence(feature=Value(dtype="float32")),
                    "memory_id": Value(dtype="string"),
                    "memory_version": Value(dtype="int64"),
                    "source_id": Value(dtype="string"),
                    "metadata": dict(),
                    "metrics": dict(),
                }
            ),
        )

    def insert(
        self,
        dataset: Dataset | list[ScoredMemory] | list[ScoredMemoryInsert] | list[dict],
        *,
        value_column: str = "value",
        score_column: str = "score",
        source_id_column: str | None = None,
        other_columns_as_metadata: bool = True,
        show_progress_bar: bool = True,
        compute_embeddings: bool = True,
        batch_size: int = 32,
        only_if_empty: bool = False,
        on_progress: OnProgressCallback | None = None,
        **kwargs,
    ) -> list[UUID]:
        if only_if_empty and len(self):
            logging.warning("Skipping insert: `only_if_empty` is True and scored memoryset is not empty.")
            return []

        insert_num_rows = len(dataset)
        if insert_num_rows == 0:
            logging.warning("Nothing to insert")
            return []

        if not compute_embeddings and not isinstance(dataset, list) and not isinstance(dataset[0], ScoredMemory):
            raise ValueError("compute_embeddings can only be disabled when inserting ScoredMemory objects")

        @dataclass
        class InsertItem:
            value: InputType
            score: float
            metadata: Metadata = field(default_factory=dict)
            source_id: str | None = None
            embedding: Vector | None = None
            memory_id: UUID7 = field(default_factory=uuid7)
            memory_version: int = 1
            created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
            updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
            metrics: MemoryMetrics = field(default_factory=MemoryMetrics)

        if isinstance(dataset, list) and isinstance(dataset[0], dict):
            if "score" not in dataset[0]:
                raise ValueError("Dataset dictionaries must contain a 'score' key.")
            dataset = Dataset.from_list(cast(list[dict], dataset))
        else:
            dataset = cast(Dataset | list[ScoredMemory] | list[ScoredMemoryInsert], dataset)

        if isinstance(dataset, Dataset):
            parsed_dataset = parse_dataset(
                dataset,
                value_column=value_column,
                score_column=score_column,
                source_id_column=source_id_column,
                other_columns_as_metadata=other_columns_as_metadata,
            )
            insert_items = [
                InsertItem(
                    value=item["value"],
                    score=item["score"],
                    metadata=item.get("metadata", {}),
                    source_id=item.get("source_id"),
                )
                for item in cast(list[dict], parsed_dataset)
            ]
        else:
            insert_items = [
                (
                    InsertItem(**m.model_dump())
                    if isinstance(m, ScoredMemory)
                    else InsertItem(
                        value=m.value,
                        score=m.score,
                        metadata=m.metadata,
                        source_id=m.source_id,
                    )
                )
                for m in dataset
            ]

        if compute_embeddings and insert_num_rows > 0 and not isinstance(insert_items[0].value, np.ndarray):
            insert_items = sorted(
                insert_items,
                key=lambda x: (sum(x.value.size) if isinstance(x.value, pil.Image) else len(x.value)),
                reverse=True,
            )

        for i in tqdm(range(0, insert_num_rows, batch_size), disable=not show_progress_bar):
            safely_call_on_progress(on_progress, i, insert_num_rows)
            item_batch = insert_items[i : i + batch_size]
            if compute_embeddings:
                embeddings = self._embed([m.value for m in item_batch], value_kind="document", batch_size=batch_size)
            else:
                embeddings = []
                for item in item_batch:
                    embedding = item.embedding
                    assert embedding is not None
                    embeddings.append(embedding)
            self.repository.insert(
                [
                    ScoredMemory(
                        value=item.value,
                        score=item.score,
                        embedding=embedding,
                        memory_id=item.memory_id,
                        memory_version=item.memory_version,
                        source_id=item.source_id,
                        metadata=item.metadata,
                        metrics=item.metrics,
                        created_at=item.created_at,
                        updated_at=item.updated_at,
                    )
                    for item, embedding in zip(item_batch, embeddings)
                ]
            )
        safely_call_on_progress(on_progress, insert_num_rows, insert_num_rows)
        return [m.memory_id for m in insert_items]

    def _compute_embeddings(
        self,
        query: InputType | InputTypeList | list[Vector],
        use_cache: bool = True,
    ) -> tuple[list[Vector], int]:
        num_queries = len(query) if isinstance(query, list) else 1
        if isinstance(query, list) and isinstance(query[0], np.ndarray):
            embedded_queries = cast(list[Vector], query)
        else:
            embedded_queries = self._embed(
                cast(InputTypeList, query) if isinstance(query, list) else cast(InputTypeList, [query]),
                use_cache=use_cache,
            )
        return embedded_queries, num_queries

    def _handle_exact_matches(
        self,
        memory_lookups_batch: list[list[ScoredMemoryLookup]],
        query: InputType | InputTypeList | list[Vector],
    ) -> list[list[ScoredMemoryLookup]]:
        if isinstance(query, np.ndarray):
            raise ValueError("cannot exclude exact match when passing a numpy array as the query")
        for i, memory_lookups in enumerate(memory_lookups_batch):
            query_item = query[i] if isinstance(query, list) else query
            exact_match_count = 0
            for j, memory_lookup in enumerate(memory_lookups):
                if memory_lookup.value == query_item:
                    if exact_match_count == 0:
                        memory_lookups_batch[i] = memory_lookups[:j] + memory_lookups[j + 1 :]
                    exact_match_count += 1
            if exact_match_count == 0:
                memory_lookups_batch[i] = memory_lookups[:-1]
            if exact_match_count > 1:
                logging.warning(f"Found {exact_match_count} exact matches for '{query_item}' in the scored memoryset.")
        return memory_lookups_batch

    def _format_column_result(
        self,
        memory_lookups_batch: list[list[ScoredMemoryLookup]],
        embedded_queries: list[Vector],
    ) -> ScoredMemoryLookupColumnResult:
        return ScoredMemoryLookupColumnResult(
            input_embeddings=np.vstack(embedded_queries),
            memories_embeddings=np.array(
                [[m.embedding for m in memories] for memories in memory_lookups_batch], dtype=np.float32
            ),
            memories_scores=np.array(
                [[m.score for m in memories] for memories in memory_lookups_batch], dtype=np.float32
            ),
            memories_lookup_scores=np.array(
                [[m.lookup_score for m in memories] for memories in memory_lookups_batch], dtype=np.float32
            ),
            memories_values=[[m.value for m in memories] for memories in memory_lookups_batch],
            memories_ids=[[m.memory_id for m in memories] for memories in memory_lookups_batch],
            memories_versions=[[m.memory_version for m in memories] for memories in memory_lookups_batch],
            memories_metadata=[[m.metadata for m in memories] for memories in memory_lookups_batch],
            memories_metrics=[[m.metrics or {} for m in memories] for memories in memory_lookups_batch],
            memories_source_ids=[[m.source_id for m in memories] for memories in memory_lookups_batch],
            memories_created_ats=[[m.created_at for m in memories] for memories in memory_lookups_batch],
            memories_updated_ats=[[m.updated_at for m in memories] for memories in memory_lookups_batch],
        )

    @overload
    def lookup(
        self,
        query: InputTypeList,
        *,
        exclude_exact_match: bool = False,
        return_type: Literal[LookupReturnType.ROWS, "rows"] = LookupReturnType.ROWS,
        count: int = 1,
        use_cache: bool = True,
    ) -> list[list[ScoredMemoryLookup]]:
        pass

    @overload
    def lookup(
        self,
        query: InputType,
        *,
        exclude_exact_match: bool = False,
        return_type: Literal[LookupReturnType.ROWS, "rows"] = LookupReturnType.ROWS,
        count: int = 1,
        use_cache: bool = True,
    ) -> list[ScoredMemoryLookup]:
        pass

    @overload
    def lookup(
        self,
        query: InputTypeList | InputType,
        *,
        exclude_exact_match: bool = False,
        return_type: Literal["columns", LookupReturnType.COLUMNS],
        count: int = 1,
        use_cache: bool = True,
    ) -> ScoredMemoryLookupColumnResult:
        pass

    def lookup(
        self,
        query: InputType | InputTypeList,
        *,
        count: int = 1,
        exclude_exact_match: bool = False,
        return_type: LookupReturnType | str = LookupReturnType.ROWS,
        use_cache: bool = True,
    ) -> list[list[ScoredMemoryLookup]] | list[ScoredMemoryLookup] | ScoredMemoryLookupColumnResult:
        if count < 0:
            raise ValueError("lookup count must be greater than or equal to 0")

        if exclude_exact_match:
            count += 1

        if len(self) < count:
            raise ValueError(f"Requested {count} memories but scored memoryset only contains {len(self)} memories")

        embedded_queries = self._embed(query if isinstance(query, list) else [query], use_cache=use_cache)

        if count == 0:
            memory_lookups_batch = [[] for _ in range(len(embedded_queries))]
        else:
            memory_lookups_batch = self.repository.lookup(embedded_queries, k=count, use_cache=use_cache)
            if not all(len(memories) == count for memories in memory_lookups_batch):
                raise Exception("lookup failed to return the correct number of memories")

        if exclude_exact_match:
            memory_lookups_batch = self._handle_exact_matches(memory_lookups_batch, query)

        if return_type == "columns":
            return self._format_column_result(memory_lookups_batch, embedded_queries)

        if not isinstance(query, list) and not isinstance(query, np.ndarray):
            assert len(memory_lookups_batch) == 1
            return memory_lookups_batch[0]

        return memory_lookups_batch

    @overload
    def get(self, memory_ids: UUID) -> ScoredMemory | None:
        pass

    @overload
    def get(self, memory_ids: list[UUID]) -> list[ScoredMemory | None]:
        pass

    def get(self, memory_ids: UUID | list[UUID]) -> ScoredMemory | None | list[ScoredMemory | None]:
        if isinstance(memory_ids, list):
            memories_dict = self.repository.get_multi(memory_ids)
            return [memories_dict.get(m_id, None) for m_id in memory_ids]
        else:
            memories_dict = self.repository.get_multi([memory_ids])
            return memories_dict.get(memory_ids, None)

    @overload
    def update(self, updates: ScoredMemoryUpdate) -> ScoredMemory | None:
        pass

    @overload
    def update(self, updates: list[ScoredMemoryUpdate]) -> list[ScoredMemory | None]:
        pass

    def update(
        self, updates: ScoredMemoryUpdate | list[ScoredMemoryUpdate]
    ) -> ScoredMemory | None | list[ScoredMemory | None]:
        if isinstance(updates, list):
            updates_dict = self._update_multi(updates)
            memory_ids = [update.memory_id for update in updates]
            return [updates_dict.get(m_id, None) for m_id in memory_ids]
        else:
            updates_dict = self._update_multi([updates])
            return updates_dict.get(updates.memory_id, None)

    def _update_multi(
        self,
        updates: list[ScoredMemoryUpdate],
    ) -> dict[UUID, ScoredMemory]:
        memory_ids = [update.memory_id for update in updates]
        updates_dict = dict(zip(memory_ids, updates))

        existing_memories = self.repository.get_multi(memory_ids)

        updated_memories = {}
        embeddings_to_compute = {}

        for memory_id, existing_memory in existing_memories.items():
            update = updates_dict[memory_id]

            if update.metadata is None:
                # if metadata is explicitly set to None, reset the metadata field
                update.metadata = {}

            if update.metrics is None:
                # if metrics is explicitly set to None, reset the metrics field
                update.metrics = {}

            updated_memory = ScoredMemory(
                **(
                    existing_memory.model_dump()
                    | update.model_dump(exclude_unset=True, exclude={"memory_id"})
                    | dict(updated_at=datetime.now(timezone.utc))
                ),
            )

            if update.metadata:
                # if metadata is passed, merge it with the existing metadata
                updated_memory.metadata = existing_memory.metadata | update.metadata

            if update.metrics:
                # if metrics is passed, merge it with the existing metrics
                updated_memory.metrics = existing_memory.metrics | update.metrics

            if existing_memory.value != updated_memory.value:
                embeddings_to_compute[memory_id] = updated_memory.value

            if existing_memory.value != updated_memory.value or existing_memory.score != updated_memory.score:
                updated_memory.memory_version = existing_memory.memory_version + 1
                updated_memory.updated_at = datetime.now(timezone.utc)
                if update.metrics is UNSET:
                    updated_memory.metrics = {}

            updated_memories[memory_id] = updated_memory

        if embeddings_to_compute:
            embeddings_ids = list(embeddings_to_compute.keys())
            embeddings = self._embed([embeddings_to_compute[memory_id] for memory_id in embeddings_ids])
            for memory_id, embedding in zip(embeddings_ids, embeddings):
                updated_memories[memory_id].embedding = embedding

        return self.repository.upsert_multi(list(updated_memories.values()))

    def _prepare_destination(self, destination: str | MemorysetRepository, config: MemorysetConfig) -> ScoredMemoryset:
        if isinstance(destination, str) and not self._is_database_uri(destination):
            destination = f"{self.repository.database_uri}#{destination}"
        destination_memoryset = ScoredMemoryset(destination, config=config)
        if destination_memoryset.repository == self.repository:
            raise ValueError("Destination memoryset cannot be the same as the source memoryset.")
        if len(destination_memoryset) > 0:
            raise ValueError("Destination memoryset must be empty.")
        return destination_memoryset

    def filter(
        self,
        fn: Callable[[ScoredMemory], bool],
        destination: str | MemorysetRepository,
        *,
        show_progress_bar: bool = True,
    ) -> ScoredMemoryset:
        destination_memoryset = self._prepare_destination(destination, self.config)
        values_to_insert = [m for m in self if fn(m)]
        destination_memoryset.insert(values_to_insert, compute_embeddings=False, show_progress_bar=show_progress_bar)
        return destination_memoryset

    def map(
        self,
        fn: Callable[[ScoredMemory], dict[str, Any]],
        destination: str | MemorysetRepository,
        *,
        show_progress_bar: bool = True,
    ) -> ScoredMemoryset:
        def replace_fn(memory: ScoredMemory) -> ScoredMemory:
            fn_result = fn(memory)
            if not isinstance(fn_result, dict):
                raise ValueError("Map function must return a dictionary with updates.")
            if "embedding" in fn_result:
                raise ValueError(
                    "Embedding cannot be updated. Scored memoryset automatically calculates embeddings as needed."
                )
            # Only allow updates to value, label, source_id, and metadata
            allowed_fields = {"value", "label", "source_id", "metadata", "metrics"}
            disallowed_updates = set(fn_result.keys()) - allowed_fields
            if disallowed_updates:
                raise ValueError(f"Map function can only update {allowed_fields} not {disallowed_updates}")
            value_changed = "value" in fn_result and memory.value != fn_result["value"]
            score_changed = "score" in fn_result and memory.score != fn_result["score"]
            if value_changed:
                fn_result["embedding"] = destination_memoryset._embed([fn_result["value"]])[0]
            if value_changed or score_changed:
                fn_result["memory_version"] = memory.memory_version + 1
                fn_result["updated_at"] = datetime.now(timezone.utc)
            return ScoredMemory(**(memory.model_dump() | fn_result))

        destination_memoryset = self._prepare_destination(destination, self.config)
        mapped_memories = [replace_fn(memory) for memory in self]
        destination_memoryset.insert(
            mapped_memories,
            compute_embeddings=False,
            show_progress_bar=show_progress_bar,
        )
        return destination_memoryset

    def clone(
        self,
        destination: str | MemorysetRepository,
        *,
        embedding_model: EmbeddingModel | None = None,
        limit: int | None = None,
        offset: int | None = None,
        batch_size: int = 32,
        show_progress_bar: bool = True,
        on_progress: OnProgressCallback | None = None,
    ) -> ScoredMemoryset:
        destination_memoryset = self._prepare_destination(
            destination,
            (
                self.config
                if embedding_model is None
                else MemorysetConfig(
                    label_names=self.config.label_names,
                    embedding_dim=embedding_model.embedding_dim,
                    embedding_model_name=embedding_model.path,
                    embedding_model_max_seq_length_override=embedding_model.max_seq_length_override,
                )
            ),
        )
        destination_memoryset.insert(
            self.repository.list(offset=offset, limit=limit),
            batch_size=batch_size,
            compute_embeddings=embedding_model is not None and embedding_model != self.embedding_model,
            show_progress_bar=show_progress_bar,
            on_progress=on_progress,
        )
        return destination_memoryset
