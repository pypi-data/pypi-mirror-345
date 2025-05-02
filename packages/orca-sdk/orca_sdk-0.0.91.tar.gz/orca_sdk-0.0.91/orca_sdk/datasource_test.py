from uuid import uuid4

import pytest

from ._generated_api_client.models import EmbeddingEvaluationResponse, TaskStatus
from .datasource import Datasource


def test_create_datasource(datasource, hf_dataset):
    assert datasource is not None
    assert datasource.name == "test_datasource"
    assert datasource.length == len(hf_dataset)


def test_create_datasource_unauthenticated(unauthenticated, hf_dataset):
    with pytest.raises(ValueError, match="Invalid API key"):
        Datasource.from_hf_dataset("test_datasource", hf_dataset)


def test_create_datasource_already_exists_error(hf_dataset, datasource):
    with pytest.raises(ValueError):
        Datasource.from_hf_dataset("test_datasource", hf_dataset, if_exists="error")


def test_create_datasource_already_exists_return(hf_dataset, datasource):
    returned_dataset = Datasource.from_hf_dataset("test_datasource", hf_dataset, if_exists="open")
    assert returned_dataset is not None
    assert returned_dataset.name == "test_datasource"
    assert returned_dataset.length == len(hf_dataset)


def test_open_datasource(datasource):
    fetched_datasource = Datasource.open(datasource.name)
    assert fetched_datasource is not None
    assert fetched_datasource.name == datasource.name
    assert fetched_datasource.length == len(datasource)


def test_open_datasource_unauthenticated(datasource, unauthenticated):
    with pytest.raises(ValueError, match="Invalid API key"):
        Datasource.open("test_datasource")


def test_open_datasource_invalid_input():
    with pytest.raises(ValueError, match=r"Invalid input:.*"):
        Datasource.open("not valid id")


def test_open_datasource_not_found():
    with pytest.raises(LookupError):
        Datasource.open(str(uuid4()))


def test_open_datasource_unauthorized(datasource, unauthorized):
    with pytest.raises(LookupError):
        Datasource.open(datasource.id)


def test_all_datasources(datasource):
    datasources = Datasource.all()
    assert len(datasources) > 0
    assert any(datasource.name == datasource.name for datasource in datasources)


def test_all_datasources_unauthenticated(unauthenticated):
    with pytest.raises(ValueError, match="Invalid API key"):
        Datasource.all()


def test_drop_datasource(hf_dataset):
    Datasource.from_hf_dataset("datasource_to_delete", hf_dataset)
    assert Datasource.exists("datasource_to_delete")
    Datasource.drop("datasource_to_delete")
    assert not Datasource.exists("datasource_to_delete")


def test_drop_datasource_unauthenticated(datasource, unauthenticated):
    with pytest.raises(ValueError, match="Invalid API key"):
        Datasource.drop(datasource.id)


def test_drop_datasource_not_found():
    with pytest.raises(LookupError):
        Datasource.drop(str(uuid4()))
    # ignores error if specified
    Datasource.drop(str(uuid4()), if_not_exists="ignore")


def test_drop_datasource_unauthorized(datasource, unauthorized):
    with pytest.raises(LookupError):
        Datasource.drop(datasource.id)


def test_drop_datasource_invalid_input():
    with pytest.raises(ValueError, match=r"Invalid input:.*"):
        Datasource.drop("not valid id")
