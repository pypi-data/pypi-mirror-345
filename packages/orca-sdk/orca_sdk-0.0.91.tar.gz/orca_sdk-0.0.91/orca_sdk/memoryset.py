from __future__ import annotations

import logging
from datetime import datetime, timedelta
from os import PathLike
from typing import Any, Iterable, Literal, cast, overload

import pandas as pd
import pyarrow as pa
from datasets import Dataset
from torch.utils.data import DataLoader as TorchDataLoader
from torch.utils.data import Dataset as TorchDataset

from ._generated_api_client.api import (
    analyze_memoryset,
    clone_memoryset,
    create_embedding_evaluation,
    create_memoryset,
    delete_memories,
    delete_memoryset,
    get_analysis,
    get_embedding_evaluation,
    get_memories,
    get_memory,
    get_memoryset,
    insert_memories_gpu,
    list_memories_with_feedback,
    list_memorysets,
    memoryset_lookup_gpu,
    potential_duplicate_groups,
    query_memoryset,
    update_memories_gpu,
    update_memory_gpu,
    update_memoryset,
)
from ._generated_api_client.models import (
    CloneLabeledMemorysetRequest,
    CreateLabeledMemorysetRequest,
    DeleteMemoriesRequest,
    EmbeddingEvaluationRequest,
    FilterItem,
    FilterItemOp,
    GetMemoriesRequest,
)
from ._generated_api_client.models import LabeledMemory as LabeledMemoryResponse
from ._generated_api_client.models import (
    LabeledMemoryInsert,
    LabeledMemoryInsertMetadata,
)
from ._generated_api_client.models import (
    LabeledMemoryLookup as LabeledMemoryLookupResponse,
)
from ._generated_api_client.models import (
    LabeledMemorysetMetadata,
    LabeledMemorysetUpdate,
    LabeledMemoryUpdate,
    LabeledMemoryUpdateMetadataType0,
    LabeledMemoryWithFeedbackMetrics,
    LabelPredictionMemoryLookup,
    ListMemoriesRequest,
    LookupRequest,
    MemorysetAnalysisConfigs,
    MemorysetAnalysisRequest,
    PretrainedEmbeddingModelName,
    TaskStatus,
    TelemetryFilterItem,
    TelemetryFilterItemOp,
    TelemetryMemoriesRequest,
    TelemetrySortOptions,
    TelemetrySortOptionsDirection,
)
from ._generated_api_client.types import UNSET as CLIENT_UNSET
from ._utils.common import UNSET, CreateMode, DropMode
from ._utils.task import wait_for_task
from .datasource import Datasource
from .embedding_model import (
    FinetunedEmbeddingModel,
    PretrainedEmbeddingModel,
    _EmbeddingModel,
)

TelemetrySortItem = tuple[str, Literal["asc", "desc"]]
"""
Sort expression for telemetry data consisting of a field and a direction.

* **`field`**: The field to sort on.
* **`direction`**: The direction to sort in.

Examples:
    >>> ("feedback_metrics.accuracy.avg", "asc")
    >>> ("lookup.count", "desc")
"""

FilterOperation = Literal["==", "!=", ">", ">=", "<", "<=", "in", "not in", "like"]
"""
Operations that can be used in a filter expression.
"""

FilterValue = str | int | float | bool | datetime | None | list[str] | list[int] | list[float] | list[bool]
"""
Values that can be used in a filter expression.
"""

FilterItemTuple = tuple[str, FilterOperation, FilterValue]
"""
Filter expression consisting of a field, an operator, and a value:

* **`field`**: The field to filter on.
* **`operation`**: The operation to apply to the field and value.
* **`value`**: The value to compare the field against.

Examples:
    >>> ("label", "==", 0)
    >>> ("metadata.author", "like", "John")
    >>> ("source_id", "in", ["123", "456"])
    >>> ("feedback_metrics.accuracy.avg", ">", 0.95)
"""


DEFAULT_COLUMN_NAMES = {"value", "label", "source_id"}
FORBIDDEN_METADATA_COLUMN_NAMES = {
    "memory_id",
    "memory_version",
    "embedding",
    "created_at",
    "updated_at",
    "metrics",
    "feedback_metrics",
    "lookup",
}


def _parse_filter_item_from_tuple(input: FilterItemTuple) -> FilterItem | TelemetryFilterItem:
    field = input[0].split(".")
    if len(field) == 1 and field[0] not in DEFAULT_COLUMN_NAMES | FORBIDDEN_METADATA_COLUMN_NAMES:
        field = ["metadata", field[0]]
    op = FilterItemOp(input[1])
    value = input[2]
    if field[0] in ["feedback_metrics", "lookup"]:
        if not (
            (isinstance(value, list) and all(isinstance(v, float) or isinstance(v, int) for v in value))
            or isinstance(value, float)
            or isinstance(value, int)
        ):
            raise ValueError(f"Invalid value for {field[0]} filter: {value}")
        if field[0] == "feedback_metrics" and (len(field) != 3 or field[2] not in ["avg", "count"]):
            raise ValueError(
                "Feedback metrics filters must follow the format `feedback_metrics.<feedback_category_name>.<avg | count>`"
            )
        elif field[0] == "lookup" and (len(field) != 2 or field[1] != "count"):
            raise ValueError("Lookup filters must follow the format `lookup.count`")
        op = TelemetryFilterItemOp(op)

        return TelemetryFilterItem(field=field, op=op, value=cast(list[float] | list[int] | float | int, value))

    return FilterItem(field=field, op=op, value=value)


def _parse_sort_item_from_tuple(
    input: TelemetrySortItem,
) -> TelemetrySortOptions:
    field = input[0].split(".")

    if len(field) == 1:
        raise ValueError("Sort field must be a telemetry field with an aggregate function name value")
    if field[0] not in ["feedback_metrics", "lookup"]:
        raise ValueError("Sort field must be one of telemetry fields: feedback_metrics or lookup")
    if field[0] == "feedback_metrics":
        if len(field) != 3:
            raise ValueError(
                "Feedback metrics must follow the format `feedback_metrics.<feedback_category_name>.<avg | count>`"
            )
        if field[2] not in ["avg", "count"]:
            raise ValueError("Feedback metrics can only be sorted on avg or count")
    if field[0] == "lookup":
        if len(field) != 2:
            raise ValueError("Lookup must follow the format `lookup.count`")
        if field[1] != "count":
            raise ValueError("Lookup can only be sorted on count")
    return TelemetrySortOptions(field=field, direction=TelemetrySortOptionsDirection(input[1]))


def _parse_memory_insert(memory: dict[str, Any]) -> LabeledMemoryInsert:
    value = memory.get("value")
    if not isinstance(value, str):
        raise ValueError("Memory value must be a string")
    label = memory.get("label")
    if not isinstance(label, int):
        raise ValueError("Memory label must be an integer")
    source_id = memory.get("source_id")
    if source_id and not isinstance(source_id, str):
        raise ValueError("Memory source_id must be a string")
    metadata = LabeledMemoryInsertMetadata.from_dict({k: v for k, v in memory.items() if k not in DEFAULT_COLUMN_NAMES})
    if any(k in metadata for k in FORBIDDEN_METADATA_COLUMN_NAMES):
        raise ValueError(f"The following column names are reserved: {', '.join(FORBIDDEN_METADATA_COLUMN_NAMES)}")
    return LabeledMemoryInsert(value=value, label=label, source_id=source_id, metadata=metadata)


def _parse_memory_update(update: dict[str, Any]) -> LabeledMemoryUpdate:
    if "memory_id" not in update:
        raise ValueError("memory_id must be specified in the update dictionary")
    memory_id = update["memory_id"]
    if not isinstance(memory_id, str):
        raise ValueError("memory_id must be a string")
    value = update.get("value", CLIENT_UNSET)
    if value is not CLIENT_UNSET and not isinstance(value, str):
        raise ValueError("value must be a string or unset")
    label = update.get("label", CLIENT_UNSET)
    if label is not CLIENT_UNSET and not isinstance(label, int):
        raise ValueError("label must be an integer or unset")
    source_id = update.get("source_id", CLIENT_UNSET)
    if source_id is not CLIENT_UNSET and not isinstance(source_id, str):
        raise ValueError("source_id must be a string or unset")
    metadata = LabeledMemoryUpdateMetadataType0.from_dict(
        {k: v for k, v in update.items() if k not in DEFAULT_COLUMN_NAMES | {"memory_id"}}
    )
    if any(k in metadata for k in FORBIDDEN_METADATA_COLUMN_NAMES):
        raise ValueError(f"Cannot update the following metadata keys: {', '.join(FORBIDDEN_METADATA_COLUMN_NAMES)}")
    return LabeledMemoryUpdate(memory_id=memory_id, value=value, label=label, source_id=source_id, metadata=metadata)


class LabeledMemory:
    """
    A row of the [`LabeledMemoryset`][orca_sdk.LabeledMemoryset]

    Attributes:
        value: Value represented by the row
        embedding: Embedding of the value of the memory for semantic search, automatically generated
            with the [`LabeledMemoryset.embedding_model`][orca_sdk.LabeledMemoryset]
        label: Class label of the memory
        label_name: Human-readable name of the label, automatically populated from the
            [`LabeledMemoryset.label_names`][orca_sdk.LabeledMemoryset]
        source_id: Optional unique identifier of the memory in a system of reference
        metrics: Metrics about the memory, generated when running an analysis on the
            [`LabeledMemoryset`][orca_sdk.LabeledMemoryset]
        metadata: Metadata associated with the memory that is not used in the model. Metadata
            properties are also accessible as individual attributes on the instance.
        memory_id: Unique identifier for the memory, automatically generated on insert
        memory_version: Version of the memory, automatically updated when the label or value changes
        created_at: When the memory was created, automatically generated on insert
        updated_at: When the memory was last updated, automatically updated on update

    ## Other Attributes:
    * **`...`** (<code>[str][str] | [float][float] | [int][int] | [bool][bool] | None</code>): All metadata properties can be accessed as attributes
    """

    value: str | list[list[float]]
    embedding: list[float]
    label: int
    label_name: str | None
    source_id: str | None
    created_at: datetime
    updated_at: datetime
    metadata: dict[str, str | float | int | bool | None]
    metrics: dict[str, Any]
    memory_id: str
    memory_version: int
    feedback_metrics: dict[str, Any]
    lookup_count: int

    def __init__(
        self,
        memoryset_id: str,
        memory: (
            LabeledMemoryResponse
            | LabeledMemoryLookupResponse
            | LabelPredictionMemoryLookup
            | LabeledMemoryWithFeedbackMetrics
        ),
    ):
        # for internal use only, do not document
        self.memoryset_id = memoryset_id
        self.memory_id = memory.memory_id
        self.memory_version = memory.memory_version
        self.value = memory.value
        self.embedding = memory.embedding
        self.label = memory.label
        self.label_name = memory.label_name
        self.source_id = memory.source_id
        self.created_at = memory.created_at
        self.updated_at = memory.updated_at
        self.metadata = memory.metadata.to_dict()
        self.metrics = memory.metrics.to_dict() if memory.metrics else {}
        self.feedback_metrics = (
            memory.feedback_metrics.to_dict() if isinstance(memory, LabeledMemoryWithFeedbackMetrics) else {}
        )
        self.lookup_count = memory.lookup_count if isinstance(memory, LabeledMemoryWithFeedbackMetrics) else 0

    def __getattr__(self, key: str) -> Any:
        if key.startswith("__") or key not in self.metadata:
            raise AttributeError(f"{key} is not a valid attribute")
        return self.metadata[key]

    def __repr__(self) -> str:
        return (
            "LabeledMemory({ "
            + f"label: {('<' + self.label_name + ': ' + str(self.label) + '>') if self.label_name else str(self.label)}"
            + f", value: '{self.value[:100] + '...' if isinstance(self.value, str) and len(self.value) > 100 else self.value}'"
            + (f", source_id: '{self.source_id}'" if self.source_id is not None else "")
            + " })"
        )

    def __eq__(self, other: object) -> bool:
        return isinstance(other, LabeledMemory) and self.memory_id == other.memory_id

    def update(
        self,
        *,
        value: str = UNSET,
        label: int = UNSET,
        source_id: str | None = UNSET,
        **metadata: None | bool | float | int | str,
    ) -> LabeledMemory:
        """
        Update the memory with new values

        Note:
            If a field is not provided, it will default to [UNSET][orca_sdk.UNSET] and not be updated.

        Params:
            value: New value of the memory
            label: New label of the memory
            source_id: New source ID of the memory
            **metadata: New values for metadata properties

        Returns:
            The updated memory
        """
        response = update_memory_gpu(
            self.memoryset_id,
            body=_parse_memory_update(
                {"memory_id": self.memory_id}
                | ({"value": value} if value is not UNSET else {})
                | ({"label": label} if label is not UNSET else {})
                | ({"source_id": source_id} if source_id is not UNSET else {})
                | metadata
            ),
        )
        self.__dict__.update(LabeledMemory(self.memoryset_id, response).__dict__)
        return self


class LabeledMemoryLookup(LabeledMemory):
    """
    Lookup result for a memory in a memoryset

    Attributes:
        lookup_score: Similarity between the memory embedding and search query embedding
        attention_weight: Weight the model assigned to the memory during prediction if this lookup
            happened as part of a prediction
        value: Value represented by the row
        embedding: Embedding of the value of the memory for semantic search, automatically generated
            with the [`LabeledMemoryset.embedding_model`][orca_sdk.LabeledMemoryset]
        label: Class label of the memory
        label_name: Human-readable name of the label, automatically populated from the
            [`LabeledMemoryset.label_names`][orca_sdk.LabeledMemoryset]
        source_id: Optional unique identifier of the memory in a system of reference
        metrics: Metrics about the memory, generated when running an analysis on the
            [`LabeledMemoryset`][orca_sdk.LabeledMemoryset]
        metadata: Metadata associated with the memory that is not used in the model. Metadata
            properties are also accessible as individual attributes on the instance.
        memory_id: The unique identifier for the memory, automatically generated on insert
        memory_version: The version of the memory, automatically updated when the label or value changes
        created_at: When the memory was created, automatically generated on insert
        updated_at: When the memory was last updated, automatically updated on update

    ## Other Attributes:
    * **`...`** (<code>[str][str] | [float][float] | [int][int] | [bool][bool] | None</code>): All metadata properties can be accessed as attributes
    """

    lookup_score: float
    attention_weight: float | None

    def __init__(self, memoryset_id: str, memory_lookup: LabeledMemoryLookupResponse | LabelPredictionMemoryLookup):
        # for internal use only, do not document
        super().__init__(memoryset_id, memory_lookup)
        self.lookup_score = memory_lookup.lookup_score
        self.attention_weight = (
            memory_lookup.attention_weight if isinstance(memory_lookup, LabelPredictionMemoryLookup) else None
        )

    def __repr__(self) -> str:
        return (
            "LabeledMemoryLookup({ "
            + f"label: {('<' + self.label_name + ': ' + str(self.label) + '>') if self.label_name else str(self.label)}"
            + f", lookup_score: {self.lookup_score:.2f}"
            + (f", attention_weight: {self.attention_weight:.2f}" if self.attention_weight is not None else "")
            + f", value: '{self.value[:100] + '...' if isinstance(self.value, str) and len(self.value) > 100 else self.value}'"
            + (f", source_id: '{self.source_id}'" if self.source_id is not None else "")
            + " })"
        )


class LabeledMemoryset:
    """
    A Handle to a collection of memories with labels in the OrcaCloud

    Attributes:
        id: Unique identifier for the memoryset
        name: Unique name of the memoryset
        description: Description of the memoryset
        label_names: Names for the class labels in the memoryset
        length: Number of memories in the memoryset
        embedding_model: Embedding model used to embed the memory values for semantic search
        created_at: When the memoryset was created, automatically generated on create
        updated_at: When the memoryset was last updated, automatically updated on updates
    """

    id: str
    name: str
    description: str | None
    label_names: list[str]
    length: int
    created_at: datetime
    updated_at: datetime
    insertion_status: TaskStatus
    embedding_model: _EmbeddingModel

    def __init__(self, metadata: LabeledMemorysetMetadata):
        # for internal use only, do not document
        if metadata.pretrained_embedding_model_name:
            self.embedding_model = PretrainedEmbeddingModel._get(metadata.pretrained_embedding_model_name)
        elif metadata.finetuned_embedding_model_id:
            self.embedding_model = FinetunedEmbeddingModel.open(metadata.finetuned_embedding_model_id)
        else:
            raise ValueError("Either pretrained_embedding_model_name or finetuned_embedding_model_id must be provided")
        self.id = metadata.id
        self.name = metadata.name
        self.description = metadata.description
        self.label_names = metadata.label_names
        self.length = metadata.length
        self.created_at = metadata.created_at
        self.updated_at = metadata.updated_at
        self.insertion_status = metadata.insertion_status
        self._last_refresh = datetime.now()

    def __eq__(self, other) -> bool:
        return isinstance(other, LabeledMemoryset) and self.id == other.id

    def __repr__(self) -> str:
        return (
            "LabeledMemoryset({\n"
            f"    name: '{self.name}',\n"
            f"    length: {self.length},\n"
            f"    label_names: {self.label_names},\n"
            f"    embedding_model: {self.embedding_model},\n"
            "})"
        )

    @classmethod
    def create(
        cls,
        name: str,
        datasource: Datasource,
        *,
        embedding_model: FinetunedEmbeddingModel | PretrainedEmbeddingModel | None = None,
        value_column: str = "value",
        label_column: str = "label",
        source_id_column: str | None = None,
        description: str | None = None,
        label_names: list[str] | None = None,
        max_seq_length_override: int | None = None,
        remove_duplicates: bool = True,
        if_exists: CreateMode = "error",
    ) -> LabeledMemoryset:
        """
        Create a new memoryset in the OrcaCloud

        All columns from the datasource that are not specified in the `value_column`,
        `label_column`, or `source_id_column` will be stored as metadata in the memoryset.

        Params:
            name: Name for the new memoryset (must be unique)
            datasource: Source data to populate the memories in the memoryset
            embedding_model: Embedding model to use for embedding memory values for semantic search.
                If not provided, a default embedding model for the memoryset will be used.
            value_column: Name of the column in the datasource that contains the memory values
            label_column: Name of the column in the datasource that contains the memory labels,
                these must be contiguous integers starting from 0
            source_id_column: Optional name of the column in the datasource that contains the ids in
                the system of reference
            description: Optional description for the memoryset, this will be used in agentic flows,
                so make sure it is concise and describes the contents of your memoryset not the
                datasource or the embedding model.
            label_names: List of human-readable names for the labels in the memoryset, must match
                the number of labels in the `label_column`. Will be automatically inferred if a
                [Dataset][datasets.Dataset] with a [`ClassLabel`][datasets.ClassLabel] feature for
                labels is used as the datasource
            max_seq_length_override: Maximum sequence length of values in the memoryset, if the
                value is longer than this it will be truncated, will default to the model's max
                sequence length if not provided
            remove_duplicates: Whether to remove duplicates from the datasource before inserting
                into the memoryset
            if_exists: What to do if a memoryset with the same name already exists, defaults to
                `"error"`. Other option is `"open"` to open the existing memoryset.

        Returns:
            Handle to the new memoryset in the OrcaCloud

        Raises:
            ValueError: If the memoryset already exists and if_exists is `"error"` or if it is
                `"open"` and the params do not match those of the existing memoryset.
        """
        if embedding_model is None:
            embedding_model = PretrainedEmbeddingModel.CDE_SMALL

        if cls.exists(name):
            if if_exists == "error":
                raise ValueError(f"Memoryset with name {name} already exists")
            elif if_exists == "open":
                existing = cls.open(name)
                for attribute in {"label_names", "embedding_model"}:
                    if locals()[attribute] is not None and locals()[attribute] != getattr(existing, attribute):
                        raise ValueError(f"Memoryset with name {name} already exists with a different {attribute}.")
                return existing

        response = create_memoryset(
            body=CreateLabeledMemorysetRequest(
                name=name,
                description=description,
                datasource_id=datasource.id,
                datasource_label_column=label_column,
                datasource_value_column=value_column,
                datasource_source_id_column=source_id_column,
                pretrained_embedding_model_name=(
                    embedding_model._model_name if isinstance(embedding_model, PretrainedEmbeddingModel) else None
                ),
                finetuned_embedding_model_id=(
                    embedding_model.id if isinstance(embedding_model, FinetunedEmbeddingModel) else None
                ),
                label_names=label_names or [],
                max_seq_length_override=max_seq_length_override,
                remove_duplicates=remove_duplicates,
            ),
        )
        wait_for_task(response.insertion_task_id, description="Inserting datasource")
        return cls.open(response.id)

    @classmethod
    def from_hf_dataset(cls, name: str, hf_dataset: Dataset, **kwargs: Any) -> LabeledMemoryset:
        """
        Create a new memoryset from a Hugging Face [`Dataset`][datasets.Dataset] in the OrcaCloud

        This will automatically create a [`Datasource`][orca_sdk.Datasource] with the same name
        appended with `_datasource` and use that as the datasource for the memoryset.

        All features that are not specified to be used as `value_column`, `label_column`, or
        `source_id_column` will be stored as metadata in the memoryset.

        Params:
            name: Name for the new memoryset (must be unique)
            hf_dataset: Hugging Face dataset to create the memoryset from
            kwargs: Additional parameters for creating the memoryset. See
                [`create`][orca_sdk.LabeledMemoryset.create] attributes for details.


        Returns:
            Handle to the new memoryset in the OrcaCloud
        """
        datasource = Datasource.from_hf_dataset(
            f"{name}_datasource", hf_dataset, if_exists=kwargs.get("if_exists", "error")
        )
        return cls.create(name, datasource, **kwargs)

    @classmethod
    def from_pytorch(
        cls,
        name: str,
        torch_data: TorchDataLoader | TorchDataset,
        *,
        column_names: list[str] | None = None,
        **kwargs: Any,
    ) -> LabeledMemoryset:
        """
        Create a new memoryset from a PyTorch [`DataLoader`][torch.utils.data.DataLoader] or
        [`Dataset`][torch.utils.data.Dataset] in the OrcaCloud

        This will automatically create a [`Datasource`][orca_sdk.Datasource] with the same name
        appended with `_datasource` and use that as the datasource for the memoryset.

        All properties that are not specified to be used as `value_column`, `label_column`, or
        `source_id_column` will be stored as metadata in the memoryset.

        Params:
            name: Name for the new memoryset (must be unique)
            torch_data: PyTorch data loader or dataset to create the memoryset from
            column_names: If the provided dataset or data loader returns unnamed tuples, this
                argument must be provided to specify the names of the columns.
            kwargs: Additional parameters for creating the memoryset. See
                [`create`][orca_sdk.LabeledMemoryset.create] attributes for details.


        Returns:
            Handle to the new memoryset in the OrcaCloud
        """
        datasource = Datasource.from_pytorch(
            f"{name}_datasource", torch_data, column_names=column_names, if_exists=kwargs.get("if_exists", "error")
        )
        return cls.create(name, datasource, **kwargs)

    @classmethod
    def from_list(cls, name: str, data: list[dict], **kwargs: Any) -> LabeledMemoryset:
        """
        Create a new memoryset from a list of dictionaries in the OrcaCloud

        This will automatically create a [`Datasource`][orca_sdk.Datasource] with the same name
        appended with `_datasource` and use that as the datasource for the memoryset.

        All properties that are not specified to be used as `value_column`, `label_column`, or
        `source_id_column` will be stored as metadata in the memoryset.

        Params:
            name: Name for the new memoryset (must be unique)
            data: List of dictionaries to create the memoryset from
            kwargs: Additional parameters for creating the memoryset. See
                [`create`][orca_sdk.LabeledMemoryset.create] attributes for details.

        Returns:
            Handle to the new memoryset in the OrcaCloud

        Examples:
            >>> LabeledMemoryset.from_list("my_memoryset", [
            ...     {"value": "hello", "label": 0, "tag": "tag1"},
            ...     {"value": "world", "label": 1, "tag": "tag2"},
            ... ])
        """
        datasource = Datasource.from_list(f"{name}_datasource", data, if_exists=kwargs.get("if_exists", "error"))
        return cls.create(name, datasource, **kwargs)

    @classmethod
    def from_dict(cls, name: str, data: dict, **kwargs: Any) -> LabeledMemoryset:
        """
        Create a new memoryset from a dictionary of columns in the OrcaCloud

        This will automatically create a [`Datasource`][orca_sdk.Datasource] with the same name
        appended with `_datasource` and use that as the datasource for the memoryset.

        All columns from the datasource that are not specified in the `value_column`,
        `label_column`, or `source_id_column` will be stored as metadata in the memoryset.

        Params:
            name: Name for the new memoryset (must be unique)
            data: Dictionary of columns to create the memoryset from
            kwargs: Additional parameters for creating the memoryset. See
                [`create`][orca_sdk.LabeledMemoryset.create] attributes for details.

        Returns:
            Handle to the new memoryset in the OrcaCloud

        Examples:
            >>> LabeledMemoryset.from_dict("my_memoryset", {
            ...     "value": ["hello", "world"],
            ...     "label": [0, 1],
            ...     "tag": ["tag1", "tag2"],
            ... })
        """
        datasource = Datasource.from_dict(f"{name}_datasource", data, if_exists=kwargs.get("if_exists", "error"))
        return cls.create(name, datasource, **kwargs)

    @classmethod
    def from_pandas(cls, name: str, dataframe: pd.DataFrame, **kwargs: Any) -> LabeledMemoryset:
        """
        Create a new memoryset from a pandas [`DataFrame`][pandas.DataFrame] in the OrcaCloud

        This will automatically create a [`Datasource`][orca_sdk.Datasource] with the same name
        appended with `_datasource` and use that as the datasource for the memoryset.

        All columns that are not specified to be used as `value_column`, `label_column`, or
        `source_id_column` will be stored as metadata in the memoryset.

        Params:
            name: Name for the new memoryset (must be unique)
            dataframe: Dataframe to create the memoryset from
            kwargs: Additional parameters for creating the memoryset. See
                [`create`][orca_sdk.LabeledMemoryset.create] attributes for details.

        Returns:
            Handle to the new memoryset in the OrcaCloud
        """
        datasource = Datasource.from_pandas(f"{name}_datasource", dataframe, if_exists=kwargs.get("if_exists", "error"))
        return cls.create(name, datasource, **kwargs)

    @classmethod
    def from_arrow(cls, name: str, pyarrow_table: pa.Table, **kwargs: Any) -> LabeledMemoryset:
        """
        Create a new memoryset from a PyArrow [`Table`][pyarrow.Table] in the OrcaCloud

        This will automatically create a [`Datasource`][orca_sdk.Datasource] with the same name
        appended with `_datasource` and use that as the datasource for the memoryset.

        All columns that are not specified to be used as `value_column`, `label_column`, or
        `source_id_column` will be stored as metadata in the memoryset.

        Params:
            name: Name for the new memoryset (must be unique)
            pyarrow_table: PyArrow table to create the memoryset from
            kwargs: Additional parameters for creating the memoryset. See
                [`create`][orca_sdk.LabeledMemoryset.create] attributes for details.

        Returns:
            Handle to the new memoryset in the OrcaCloud
        """
        datasource = Datasource.from_arrow(
            f"{name}_datasource", pyarrow_table, if_exists=kwargs.get("if_exists", "error")
        )
        return cls.create(name, datasource, **kwargs)

    @classmethod
    def from_disk(cls, name: str, file_path: str | PathLike, **kwargs: Any) -> LabeledMemoryset:
        """
        Create a new memoryset from a file on disk in the OrcaCloud

        This will automatically create a [`Datasource`][orca_sdk.Datasource] with the same name
        appended with `_datasource` and use that as the datasource for the memoryset.

        All columns from the datasource that are not specified in the `value_column`,
        `label_column`, or `source_id_column` will be stored as metadata in the memoryset.

        Params:
            name: Name for the new memoryset (must be unique)
            file_path: Path to the file on disk to create the memoryset from. The file type will
                be inferred from the file extension. The following file types are supported:

                - .pkl: [`Pickle`][pickle] files containing lists of dictionaries or dictionaries of columns
                - .json/.jsonl: [`JSON`][json] and [`JSON`] Lines files
                - .csv: [`CSV`][csv] files
                - .parquet: [`Parquet`][pyarrow.parquet.ParquetFile] files
                - dataset directory: Directory containing a saved HuggingFace [`Dataset`][datasets.Dataset]
            kwargs: Additional parameters for creating the memoryset. See
                [`create`][orca_sdk.LabeledMemoryset.create] attributes for details.

        Returns:
            Handle to the new memoryset in the OrcaCloud
        """
        datasource = Datasource.from_disk(f"{name}_datasource", file_path, if_exists=kwargs.get("if_exists", "error"))
        return cls.create(name, datasource, **kwargs)

    @classmethod
    def open(cls, name: str) -> LabeledMemoryset:
        """
        Get a handle to a memoryset in the OrcaCloud

        Params:
            name: Name or unique identifier of the memoryset

        Returns:
            Handle to the existing memoryset in the OrcaCloud

        Raises:
            LookupError: If the memoryset does not exist
        """
        metadata = get_memoryset(name)
        return cls(metadata)

    @classmethod
    def exists(cls, name_or_id: str) -> bool:
        """
        Check if a memoryset exists in the OrcaCloud

        Params:
            name_or_id: Name or id of the memoryset

        Returns:
            True if the memoryset exists, False otherwise
        """
        try:
            cls.open(name_or_id)
            return True
        except LookupError:
            return False

    @classmethod
    def all(cls) -> list[LabeledMemoryset]:
        """
        Get a list of handles to all memorysets in the OrcaCloud

        Returns:
            List of handles to all memorysets in the OrcaCloud
        """
        return [cls(metadata) for metadata in list_memorysets()]

    @classmethod
    def drop(cls, name_or_id: str, if_not_exists: DropMode = "error"):
        """
        Delete a memoryset from the OrcaCloud

        Params:
            name_or_id: Name or id of the memoryset
            if_not_exists: What to do if the memoryset does not exist, defaults to `"error"`.
                Other options are `"ignore"` to do nothing if the memoryset does not exist.

        Raises:
            LookupError: If the memoryset does not exist and if_not_exists is `"error"`
        """
        try:
            delete_memoryset(name_or_id)
            logging.info(f"Deleted memoryset {name_or_id}")
        except LookupError:
            if if_not_exists == "error":
                raise

    def update_metadata(self, *, description: str | None = UNSET, label_names: list[str] | None = None):
        """
        Update the metadata of the memoryset

        Params:
            description: Value to set for the description, defaults to `[UNSET]` if not provided.
            label_names: Value to replace existing label names with, defaults to None if not provided.
        """
        update_memoryset(self.id, body=LabeledMemorysetUpdate(description=description, label_names=label_names))
        self.refresh()

    def clone(
        self,
        name: str,
        *,
        embedding_model: PretrainedEmbeddingModel | FinetunedEmbeddingModel | None = None,
        max_seq_length_override: int | None = None,
        if_exists: CreateMode = "error",
    ) -> LabeledMemoryset:
        """
        Create a clone of the memoryset with a new name

        Params:
            name: Name for the new memoryset (must be unique)
            embedding_model: Optional new embedding model to use for re-embedding the memory values
            max_seq_length_override: Maximum sequence length of values in the memoryset, if the
                value is longer than this it will be truncated, will default to the model's max
                sequence length if not provided
            if_exists: What to do if a memoryset with the same name already exists, defaults to
                `"error"`. Other option is `"open"` to open the existing memoryset.

        Returns:
            Handle to the cloned memoryset in the OrcaCloud

        Examples:
            >>> memoryset = LabeledMemoryset.open("my_memoryset")
            >>> finetuned_embedding_model = PretrainedEmbeddingModel.GTE_BASE.finetune(
            ...     "gte_base_finetuned", my_memoryset
            ... )
            >>> new_memoryset = memoryset.clone(
            ...     "my_memoryset_finetuned", embedding_model=finetuned_embedding_model,
            ... )
        """
        if self.exists(name):
            if if_exists == "error":
                raise ValueError(f"Memoryset with name {name} already exists")
            elif if_exists == "open":
                existing = self.open(name)
                for attribute in {"embedding_model"}:
                    if locals()[attribute] is not None and locals()[attribute] != getattr(existing, attribute):
                        raise ValueError(f"Memoryset with name {name} already exists with a different {attribute}.")
                return existing

        metadata = clone_memoryset(
            self.id,
            body=CloneLabeledMemorysetRequest(
                name=name,
                pretrained_embedding_model_name=(
                    embedding_model._model_name if isinstance(embedding_model, PretrainedEmbeddingModel) else None
                ),
                finetuned_embedding_model_id=(
                    embedding_model.id if isinstance(embedding_model, FinetunedEmbeddingModel) else None
                ),
                max_seq_length_override=max_seq_length_override,
            ),
        )
        wait_for_task(metadata.insertion_task_id, description="Cloning memoryset")
        return LabeledMemoryset.open(metadata.id)

    def refresh(self, throttle: float = 0):
        """
        Refresh the information about the memoryset from the OrcaCloud

        Params:
            throttle: Minimum time in seconds between refreshes
        """
        current_time = datetime.now()
        # Skip refresh if last refresh was too recent
        if (current_time - self._last_refresh) < timedelta(seconds=throttle):
            return

        self.__dict__.update(LabeledMemoryset.open(self.id).__dict__)
        self._last_refresh = current_time

    def __len__(self) -> int:
        """Get the number of memories in the memoryset"""
        self.refresh(throttle=5)
        return self.length

    @overload
    def __getitem__(self, index: int | str) -> LabeledMemory:
        pass

    @overload
    def __getitem__(self, index: slice) -> list[LabeledMemory]:
        pass

    def __getitem__(self, index: int | slice | str) -> LabeledMemory | list[LabeledMemory]:
        """
        Get memories from the memoryset by index or memory id

        Params:
            index: Index or memory to retrieve or slice of memories to retrieve or unique
                identifier of the memory to retrieve

        Returns:
            Memory or memories from the memoryset

        Raises:
            LookupError: If the id is not found or the index is out of bounds

        Examples:
            Retrieve the first memory in the memoryset:
            >>> memoryset[0]
            LabeledMemory({ label: <positive: 1>, value: 'I am happy' })

            Retrieve the last memory in the memoryset:
            >>> memoryset[-1]
            LabeledMemory({ label: <negative: 0>, value: 'I am sad' })

            Retrieve a slice of memories in the memoryset:
            >>> memoryset[1:3]
            [
                LabeledMemory({ label: <positive: 1>, value: 'I am happy' }),
                LabeledMemory({ label: <negative: 0>, value: 'I am sad' }),
            ]

            Retrieve a memory by id:
            >>> memoryset["0195019a-5bc7-7afb-b902-5945ee1fb766"]
            LabeledMemory({ label: <positive: 1>, value: 'I am happy' })
        """
        if isinstance(index, int):
            return self.query(offset=len(self) + index if index < 0 else index, limit=1)[0]
        elif isinstance(index, str):
            return self.get(index)
        elif isinstance(index, slice):
            start = 0 if index.start is None else (len(self) + index.start) if index.start < 0 else index.start
            stop = len(self) if index.stop is None else (len(self) + index.stop) if index.stop < 0 else index.stop
            return self.query(offset=start, limit=stop - start)
        else:
            raise ValueError(f"Invalid index type: {type(index)}")

    @overload
    def search(self, query: str, *, count: int = 1) -> list[LabeledMemoryLookup]:
        pass

    @overload
    def search(self, query: list[str], *, count: int = 1) -> list[list[LabeledMemoryLookup]]:
        pass

    def search(
        self, query: str | list[str], *, count: int = 1
    ) -> list[LabeledMemoryLookup] | list[list[LabeledMemoryLookup]]:
        """
        Search for memories that are semantically similar to the query

        Params:
            query: Query to lookup memories in the memoryset, can be a single query or a list
            count: Number of memories to return for each query

        Returns:
            List of memories from the memoryset that match the query. If a single query is provided,
                the return value is a list containing a single list of memories. If a list of
                queries is provided, the return value is a list of lists of memories.

        Examples:
            Search for similar memories:
            >>> memoryset.search("I am happy", count=2)
            [
                LabeledMemoryLookup({ label: <positive: 1>, value: 'I am happy' }),
                LabeledMemoryLookup({ label: <positive: 1>, value: 'I am content' }),
            ]

            Search for similar memories for multiple queries:
            >>> memoryset.search(["I am happy", "I am sad"], count=1)
            [
                [
                    LabeledMemoryLookup({ label: <positive: 1>, value: 'I am happy' }),
                ],
                [
                    LabeledMemoryLookup({ label: <negative: 0>, value: 'I am sad' }),
                ],
            ]
        """
        response = memoryset_lookup_gpu(
            name_or_id=self.id,
            body=LookupRequest(
                query=query if isinstance(query, list) else [query],
                count=count,
            ),
        )
        lookups = [[LabeledMemoryLookup(self.id, lookup_response) for lookup_response in batch] for batch in response]
        return lookups if isinstance(query, list) else lookups[0]

    def query(
        self,
        offset: int = 0,
        limit: int = 100,
        filters: list[FilterItemTuple] = [],
        with_feedback_metrics: bool = False,
        sort: list[TelemetrySortItem] | None = None,
    ) -> list[LabeledMemory]:
        """
        Query the memoryset for memories that match the filters

        Params:
            offset: The offset of the first memory to return
            limit: The maximum number of memories to return
            filters: List of filters to apply to the query.
            with_feedback_metrics: Whether to include feedback metrics in the response

        Returns:
            List of memories from the memoryset that match the filters

        Examples:
            >>> memoryset.query(filters=[("label", "==", 0)], limit=2)
            [
                LabeledMemory({ label: <positive: 1>, value: "I am happy" }),
                LabeledMemory({ label: <negative: 0>, value: "I am sad" }),
            ]
        """
        parsed_filters = [
            _parse_filter_item_from_tuple(filter) if isinstance(filter, tuple) else filter for filter in filters
        ]

        if with_feedback_metrics:
            return [
                LabeledMemory(self.id, memory)
                for memory in list_memories_with_feedback(
                    body=TelemetryMemoriesRequest(
                        memoryset_id=self.id,
                        offset=offset,
                        limit=limit,
                        filters=parsed_filters,
                        sort=[_parse_sort_item_from_tuple(item) for item in sort] if sort else None,
                    ),
                ).items
            ]

        if any(isinstance(filter, TelemetryFilterItem) for filter in parsed_filters):
            raise ValueError("Feedback metrics are only supported when the with_feedback_metrics flag is set to True")

        if sort:
            logging.warning("Sorting is not supported when with_feedback_metrics is False. Sort value will be ignored.")

        return [
            LabeledMemory(self.id, memory)
            for memory in query_memoryset(
                self.id,
                body=ListMemoriesRequest(
                    offset=offset,
                    limit=limit,
                    filters=cast(list[FilterItem], parsed_filters),
                ),
            )
        ]

    def insert(self, items: Iterable[dict[str, Any]] | dict[str, Any]) -> None:
        """
        Insert memories into the memoryset

        Params:
            items: List of memories to insert into the memoryset. This should be a list of
                dictionaries with the following keys:

                - `value`: Value of the memory
                - `label`: Label of the memory
                - `source_id`: Optional unique ID of the memory in a system of reference
                - `...`: Any other metadata to store for the memory

        Examples:
            >>> memoryset.insert([
            ...     {"value": "I am happy", "label": 1, "source_id": "user_123", "tag": "happy"},
            ...     {"value": "I am sad", "label": 0, "source_id": "user_124", "tag": "sad"},
            ... ])
        """
        insert_memories_gpu(
            self.id,
            body=(
                [
                    _parse_memory_insert(memory)
                    for memory in (cast(list[dict[str, Any]], [items]) if isinstance(items, dict) else items)
                ]
            ),
        )
        self.refresh()

    @overload
    def get(self, memory_id: str) -> LabeledMemory:  # type: ignore -- this takes precedence
        pass

    @overload
    def get(self, memory_id: Iterable[str]) -> list[LabeledMemory]:
        pass

    def get(self, memory_id: str | Iterable[str]) -> LabeledMemory | list[LabeledMemory]:
        """
        Fetch a memory or memories from the memoryset

        Params:
            memory_id: Unique identifier of the memory or memories to fetch

        Returns:
            Memory or list of memories from the memoryset

        Raises:
            LookupError: If no memory with the given id is found

        Examples:
            Fetch a single memory:
            >>> memoryset.get("0195019a-5bc7-7afb-b902-5945ee1fb766")
            LabeledMemory({ label: <positive: 1>, value: 'I am happy' })

            Fetch multiple memories:
            >>> memoryset.get([
            ...     "0195019a-5bc7-7afb-b902-5945ee1fb766",
            ...     "019501a1-ea08-76b2-9f62-95e4800b4841",
            ... ])
            [
                LabeledMemory({ label: <positive: 1>, value: 'I am happy' }),
                LabeledMemory({ label: <negative: 0>, value: 'I am sad' }),
            ]
        """
        if isinstance(memory_id, str):
            return LabeledMemory(self.id, get_memory(self.id, memory_id))
        else:
            return [
                LabeledMemory(self.id, memory)
                for memory in get_memories(self.id, body=GetMemoriesRequest(memory_ids=list(memory_id)))
            ]

    @overload
    def update(self, updates: dict[str, Any]) -> LabeledMemory:
        pass

    @overload
    def update(self, updates: Iterable[dict[str, Any]]) -> list[LabeledMemory]:
        pass

    def update(self, updates: dict[str, Any] | Iterable[dict[str, Any]]) -> LabeledMemory | list[LabeledMemory]:
        """
        Update one or multiple memories in the memoryset

        Params:
            updates: List of updates to apply to the memories. Each update should be a dictionary
                with the following keys:

                - `memory_id`: Unique identifier of the memory to update (required)
                - `value`: Optional new value of the memory
                - `label`: Optional new label of the memory
                - `source_id`: Optional new source ID of the memory
                - `...`: Optional new values for metadata properties

        Returns:
            Updated memory or list of updated memories

        Examples:
            Update a single memory:
            >>> memoryset.update(
            ...     {
            ...         "memory_id": "019501a1-ea08-76b2-9f62-95e4800b4841",
            ...         "tag": "happy",
            ...     },
            ... )

            Update multiple memories:
            >>> memoryset.update(
            ...     {"memory_id": m.memory_id, "label": 2}
            ...     for m in memoryset.query(filters=[("tag", "==", "happy")])
            ... )
        """
        response = update_memories_gpu(
            self.id,
            body=[
                _parse_memory_update(update)
                for update in (cast(list[dict[str, Any]], [updates]) if isinstance(updates, dict) else updates)
            ],
        )
        updated_memories = [LabeledMemory(self.id, memory) for memory in response]
        return updated_memories[0] if isinstance(updates, dict) else updated_memories

    def delete(self, memory_id: str | Iterable[str]) -> None:
        """
        Delete memories from the memoryset

        Params:
            memory_id: unique identifiers of the memories to delete

        Examples:
            Delete a single memory:
            >>> memoryset.delete("0195019a-5bc7-7afb-b902-5945ee1fb766")

            Delete multiple memories:
            >>> memoryset.delete([
            ...     "0195019a-5bc7-7afb-b902-5945ee1fb766",
            ...     "019501a1-ea08-76b2-9f62-95e4800b4841",
            ... )

        """
        memory_ids = [memory_id] if isinstance(memory_id, str) else list(memory_id)
        delete_memories(self.id, body=DeleteMemoriesRequest(memory_ids=memory_ids))
        logging.info(f"Deleted {len(memory_ids)} memories from memoryset.")
        self.refresh()

    def analyze(
        self, *analyses: Iterable[dict[str, Any] | str], lookup_count: int = 15, clear_metrics: bool = False
    ) -> dict:
        """
        Run analyses on the memoryset to find duplicates, clusters, mislabelings, and more

        The results of the analysis will be stored in the [`LabeledMemory.metrics`][orca_sdk.LabeledMemory]
        attribute of each memory in the memoryset. Overall memoryset metrics will be returned as a dictionary.

        Params:
            analyses: List of analysis to run on the memoryset, can either be just the name of an
                analysis or a dictionary with a name property and additional config. The available
                analyses are:

                - **`"duplicate"`**: Find potentially duplicate memories in the memoryset
                - **`"cluster"`**: Cluster the memories in the memoryset
                - **`"label"`**: Analyze the labels to find potential mislabelings
                - **`"neighbor"`**: Analyze the neighbors to populate anomaly scores
                - **`"projection"`**: Create a 2D projection of the embeddings for visualization

            lookup_count: Number of memories to lookup for each memory in the memoryset
            clear_metrics: Whether to clear any existing metrics from the memories before running the analysis

        Returns:
            dictionary with aggregate metrics for each analysis that was run

        Examples:
            Run label and duplicate analysis:
            >>> memoryset.analyze("label", {"name": "duplicate", "possible_duplicate_threshold": 0.99})
            { "duplicate": { "num_duplicates": 10 },
              "label": {
                "label_metrics": [{
                    "label": 0,
                    "label_name": "negative",
                    "average_lookup_score": 0.95,
                    "memory_count": 100,
                }, {
                    "label": 1,
                    "label_name": "positive",
                    "average_lookup_score": 0.90,
                    "memory_count": 100,
                }]
                "neighbor_prediction_accuracy": 0.95,
                "mean_neighbor_label_confidence": 0.95,
                "mean_neighbor_label_entropy": 0.95,
                "mean_neighbor_predicted_label_ambiguity": 0.95,
              }
            }

            Remove all exact duplicates:
            >>> memoryset.delete(
            ...     m.memory_id
            ...     for m in memoryset.query(
            ...         filters=[("metrics.is_duplicate", "==", True)]
            ...     )
            ... )

            Display label analysis to review potential mislabelings:
            >>> memoryset.display_label_analysis()
        """
        configs: dict[str, dict] = {}
        for analysis in analyses:
            if isinstance(analysis, str):
                configs[analysis] = {}
            else:
                name = analysis.pop("name")  # type: ignore
                configs[name] = analysis  # type: ignore

        analysis = analyze_memoryset(
            self.id,
            body=MemorysetAnalysisRequest(
                configs=MemorysetAnalysisConfigs.from_dict(configs),
                lookup_count=lookup_count,
                clear_metrics=clear_metrics,
            ),
        )
        wait_for_task(analysis.task_id, description="Analyzing duplicates")
        analysis = get_analysis(self.id, analysis.task_id)
        assert analysis.results is not None
        return analysis.results.to_dict()

    def display_label_analysis(self):
        """Display a UI to review and act upon the label analysis results"""
        from ._utils.analysis_ui import display_suggested_memory_relabels

        display_suggested_memory_relabels(self)

    def get_potential_duplicate_groups(self):
        """Group potential duplicates in the memoryset"""
        response = potential_duplicate_groups(self.name)
        return response

    @staticmethod
    def run_embedding_evaluation(
        datasource: Datasource,
        value_column: str = "value",
        label_column: str = "label",
        source_id_column: str | None = None,
        neighbor_count: int = 5,
        embedding_models: list[str] | None = None,
    ) -> dict:
        """
        This function runs an embedding evaluation on the datasource. The embedding evaluation will
        test the quality of embeddings for the datasource by computing metrics such as prediction accuracy.

        Params:
            datasource: The datasource to run the embedding evaluation on
            value_column: Name of the column in the datasource that contains the memory values
            label_column: Name of the column in the datasource that contains the memory labels,
                these must be contiguous integers starting from 0
            source_id_column: Optional name of the column in the datasource that contains the ids in
                the system of reference
            neighbor_count: The number of neighbors to select for prediction
            embedding_models: Optional list of embedding model keys to evaluate, if not provided all
                available embedding models will be used

        Returns:
            A dictionary containing the results of the embedding evaluation
        """

        if embedding_models is not None:
            embedding_model_enums = [PretrainedEmbeddingModelName(model) for model in embedding_models]
        else:
            embedding_model_enums = None

        request = EmbeddingEvaluationRequest(
            value_column=value_column,
            label_column=label_column,
            source_id_column=source_id_column,
            neighbor_count=neighbor_count,
            embedding_models=embedding_model_enums,
        )

        response = create_embedding_evaluation(name_or_id=datasource.id, body=request)
        wait_for_task(response.task_id, description="Running embedding evaluation")

        response = get_embedding_evaluation(datasource.id, response.task_id)
        assert response.result is not None
        return response.result.to_dict()
