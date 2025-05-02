from __future__ import annotations

import logging
import tempfile
from datetime import datetime
from os import PathLike
from pathlib import Path
from typing import cast

import pandas as pd
import pyarrow as pa
from datasets import Dataset
from torch.utils.data import DataLoader as TorchDataLoader
from torch.utils.data import Dataset as TorchDataset

from ._generated_api_client.api import (
    delete_datasource,
    get_datasource,
    list_datasources,
)
from ._generated_api_client.api.datasource.create_datasource_datasource_post import (
    _parse_response as parse_create_response,
)
from ._generated_api_client.client import get_client
from ._generated_api_client.models import ColumnType, DatasourceMetadata
from ._utils.common import CreateMode, DropMode
from ._utils.data_parsing import hf_dataset_from_disk, hf_dataset_from_torch


class Datasource:
    """
    A Handle to a datasource in the OrcaCloud

    A Datasource is a collection of data saved to the OrcaCloud that can be used to create a [`Memoryset`][orca_sdk.LabeledMemoryset].
    It can be created from a Hugging Face Dataset, a PyTorch DataLoader or Dataset, a list of dictionaries, a dictionary of columns, a pandas DataFrame, a pyarrow Table, or a local file.

    Attributes:
        id: Unique identifier for the datasource
        name: Unique name of the datasource
        description: Optional description of the datasource
        length: Number of rows in the datasource
        created_at: When the datasource was created
        columns: Dictionary of column names and types
    """

    id: str
    name: str
    description: str | None
    length: int
    created_at: datetime
    updated_at: datetime
    columns: dict[str, str]

    def __init__(self, metadata: DatasourceMetadata):
        # for internal use only, do not document
        self.id = metadata.id
        self.name = metadata.name
        self.length = metadata.length
        self.created_at = metadata.created_at
        self.updated_at = metadata.updated_at
        self.description = metadata.description
        self.columns = {
            column.name: (
                f"enum({', '.join(f'{option!r}' for option in column.enum_options) if column.enum_options else ''})"
                if column.type == ColumnType.ENUM
                else "str" if column.type == ColumnType.STRING else column.type.value.lower()
            )
            for column in metadata.columns
        }

    def __eq__(self, other) -> bool:
        return isinstance(other, Datasource) and self.id == other.id

    def __repr__(self) -> str:
        return (
            "Datasource({\n"
            + f"    name: '{self.name}',\n"
            + f"    length: {self.length},\n"
            + "    columns: {{\n        "
            + "\n        ".join([f"{k}: {v}" for k, v in self.columns.items()])
            + "\n    }}\n"
            + "})"
        )

    @classmethod
    def from_hf_dataset(
        cls, name: str, dataset: Dataset, if_exists: CreateMode = "error", description: str | None = None
    ) -> Datasource:
        """
        Create a new datasource from a Hugging Face Dataset

        Params:
            name: Required name for the new datasource (must be unique)
            dataset: The Hugging Face Dataset to create the datasource from
            if_exists: What to do if a datasource with the same name already exists, defaults to
                `"error"`. Other option is `"open"` to open the existing datasource.
            description: Optional description for the datasource

        Returns:
            A handle to the new datasource in the OrcaCloud

        Raises:
            ValueError: If the datasource already exists and if_exists is `"error"`
        """
        client = get_client()

        if cls.exists(name):
            if if_exists == "error":
                raise ValueError(f"Dataset with name {name} already exists")
            elif if_exists == "open":
                return cls.open(name)

        with tempfile.TemporaryDirectory() as tmp_dir:
            dataset.save_to_disk(tmp_dir)
            files = []
            for file_path in Path(tmp_dir).iterdir():
                buffered_reader = open(file_path, "rb")
                files.append(("files", buffered_reader))

            # Do not use Generated client for this endpoint b/c it does not handle files properly
            metadata = parse_create_response(
                response=client.get_httpx_client().request(
                    method="post",
                    url="/datasource/",
                    files=files,
                    data={"name": name, "description": description},
                )
            )
            return cls(metadata=metadata)

    @classmethod
    def from_pytorch(
        cls,
        name: str,
        torch_data: TorchDataLoader | TorchDataset,
        column_names: list[str] | None = None,
        if_exists: CreateMode = "error",
        description: str | None = None,
    ) -> Datasource:
        """
        Create a new datasource from a PyTorch DataLoader or Dataset

        Params:
            name: Required name for the new datasource (must be unique)
            torch_data: The PyTorch DataLoader or Dataset to create the datasource from
            column_names: If the provided dataset or data loader returns unnamed tuples, this
                argument must be provided to specify the names of the columns.
            if_exists: What to do if a datasource with the same name already exists, defaults to
                `"error"`. Other option is `"open"` to open the existing datasource.
            description: Optional description for the datasource

        Returns:
            A handle to the new datasource in the OrcaCloud

        Raises:
            ValueError: If the datasource already exists and if_exists is `"error"`
        """
        hf_dataset = hf_dataset_from_torch(torch_data, column_names=column_names)
        return cls.from_hf_dataset(name, hf_dataset, if_exists=if_exists, description=description)

    @classmethod
    def from_list(
        cls, name: str, data: list[dict], if_exists: CreateMode = "error", description: str | None = None
    ) -> Datasource:
        """
        Create a new datasource from a list of dictionaries

        Params:
            name: Required name for the new datasource (must be unique)
            data: The list of dictionaries to create the datasource from
            if_exists: What to do if a datasource with the same name already exists, defaults to
                `"error"`. Other option is `"open"` to open the existing datasource.
            description: Optional description for the datasource

        Returns:
            A handle to the new datasource in the OrcaCloud

        Raises:
            ValueError: If the datasource already exists and if_exists is `"error"`

        Examples:
            >>> Datasource.from_list("my_datasource", [{"text": "Hello, world!", "label": 1}, {"text": "Goodbye", "label": 0}])
        """
        hf_dataset = Dataset.from_list(data)
        return cls.from_hf_dataset(name, hf_dataset, if_exists=if_exists, description=description)

    @classmethod
    def from_dict(
        cls, name: str, data: dict, if_exists: CreateMode = "error", description: str | None = None
    ) -> Datasource:
        """
        Create a new datasource from a dictionary of columns

        Params:
            name: Required name for the new datasource (must be unique)
            data: The dictionary of columns to create the datasource from
            if_exists: What to do if a datasource with the same name already exists, defaults to
                `"error"`. Other option is `"open"` to open the existing datasource.
            description: Optional description for the datasource

        Returns:
            A handle to the new datasource in the OrcaCloud

        Raises:
            ValueError: If the datasource already exists and if_exists is `"error"`

        Examples:
            >>> Datasource.from_dict("my_datasource", {"text": ["Hello, world!", "Goodbye"], "label": [1, 0]})
        """
        hf_dataset = Dataset.from_dict(data)
        return cls.from_hf_dataset(name, hf_dataset, if_exists=if_exists, description=description)

    @classmethod
    def from_pandas(
        cls, name: str, dataframe: pd.DataFrame, if_exists: CreateMode = "error", description: str | None = None
    ) -> Datasource:
        """
        Create a new datasource from a pandas DataFrame

        Params:
            name: Required name for the new datasource (must be unique)
            dataframe: The pandas DataFrame to create the datasource from
            if_exists: What to do if a datasource with the same name already exists, defaults to
                `"error"`. Other option is `"open"` to open the existing datasource.
            description: Optional description for the datasource

        Returns:
            A handle to the new datasource in the OrcaCloud

        Raises:
            ValueError: If the datasource already exists and if_exists is `"error"`
        """
        hf_dataset = Dataset.from_pandas(dataframe)
        return cls.from_hf_dataset(name, hf_dataset, if_exists=if_exists, description=description)

    @classmethod
    def from_arrow(
        cls, name: str, pyarrow_table: pa.Table, if_exists: CreateMode = "error", description: str | None = None
    ) -> Datasource:
        """
        Create a new datasource from a pyarrow Table

        Params:
            name: Required name for the new datasource (must be unique)
            pyarrow_table: The pyarrow Table to create the datasource from
            if_exists: What to do if a datasource with the same name already exists, defaults to
                `"error"`. Other option is `"open"` to open the existing datasource.
            description: Optional description for the datasource

        Returns:
            A handle to the new datasource in the OrcaCloud

        Raises:
            ValueError: If the datasource already exists and if_exists is `"error"`
        """
        hf_dataset = Dataset(pyarrow_table)
        return cls.from_hf_dataset(name, hf_dataset, if_exists=if_exists, description=description)

    @classmethod
    def from_disk(
        cls, name: str, file_path: str | PathLike, if_exists: CreateMode = "error", description: str | None = None
    ) -> Datasource:
        """
        Create a new datasource from a local file

        Params:
            name: Required name for the new datasource (must be unique)
            file_path: Path to the file on disk to create the datasource from. The file type will
                be inferred from the file extension. The following file types are supported:

                - .pkl: [`Pickle`][pickle] files containing lists of dictionaries or dictionaries of columns
                - .json/.jsonl: [`JSON`][json] and [`JSON`] Lines files
                - .csv: [`CSV`][csv] files
                - .parquet: [`Parquet`][pyarrow.parquet.ParquetFile] files
                - dataset directory: Directory containing a saved HuggingFace [`Dataset`][datasets.Dataset]

            if_exists: What to do if a datasource with the same name already exists, defaults to
                `"error"`. Other option is `"open"` to open the existing datasource.
            description: Optional description for the datasource

        Returns:
            A handle to the new datasource in the OrcaCloud

        Raises:
            ValueError: If the datasource already exists and if_exists is `"error"`
        """
        hf_dataset = hf_dataset_from_disk(file_path)
        return cls.from_hf_dataset(name, cast(Dataset, hf_dataset), if_exists=if_exists, description=description)

    @classmethod
    def open(cls, name: str) -> Datasource:
        """
        Get a handle to a datasource by name or id in the OrcaCloud

        Params:
            name: The name or unique identifier of the datasource to get

        Returns:
            A handle to the existing datasource in the OrcaCloud

        Raises:
            LookupError: If the datasource does not exist
        """
        return cls(get_datasource(name))

    @classmethod
    def exists(cls, name_or_id: str) -> bool:
        """
        Check if a datasource exists in the OrcaCloud

        Params:
            name_or_id: The name or id of the datasource to check

        Returns:
            `True` if the datasource exists, `False` otherwise
        """
        try:
            cls.open(name_or_id)
            return True
        except LookupError:
            return False

    @classmethod
    def all(cls) -> list[Datasource]:
        """
        List all datasource handles in the OrcaCloud

        Returns:
            A list of all datasource handles in the OrcaCloud
        """
        return [cls(metadata) for metadata in list_datasources()]

    @classmethod
    def drop(cls, name_or_id: str, if_not_exists: DropMode = "error") -> None:
        """
        Delete a datasource from the OrcaCloud

        Params:
            name_or_id: The name or id of the datasource to delete
            if_not_exists: What to do if the datasource does not exist, defaults to
                `"error"`. Other options are `"ignore"` to do nothing.

        Raises:
            LookupError: If the datasource does not exist and if_not_exists is `"error"`
        """
        try:
            delete_datasource(name_or_id)
            logging.info(f"Deleted datasource {name_or_id}")
        except LookupError:
            if if_not_exists == "error":
                raise

    def __len__(self) -> int:
        return self.length
