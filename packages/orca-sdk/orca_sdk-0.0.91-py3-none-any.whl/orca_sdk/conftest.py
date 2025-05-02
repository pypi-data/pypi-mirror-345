import logging
import os
from typing import Generator
from uuid import uuid4

import pytest
from datasets import ClassLabel, Dataset, Features, Value

from ._utils.auth import _create_api_key, _delete_org
from .classification_model import ClassificationModel
from .credentials import OrcaCredentials
from .datasource import Datasource
from .embedding_model import PretrainedEmbeddingModel
from .memoryset import LabeledMemoryset

logging.basicConfig(level=logging.INFO)

os.environ["ORCA_API_URL"] = os.environ.get("ORCA_API_URL", "http://localhost:1584/")


def _create_org_id():
    # UUID start to identify test data (0xtest...)
    return "10e50000-0000-4000-a000-" + str(uuid4())[24:]


@pytest.fixture(scope="session")
def org_id():
    return _create_org_id()


@pytest.fixture(autouse=True, scope="session")
def api_key(org_id) -> Generator[str, None, None]:
    api_key = _create_api_key(org_id=org_id, name="orca_sdk_test")
    OrcaCredentials.set_api_key(api_key, check_validity=True)
    yield api_key
    _delete_org(org_id)


@pytest.fixture(autouse=True)
def authenticated(api_key):
    OrcaCredentials.set_api_key(api_key, check_validity=False)


@pytest.fixture()
def unauthenticated(api_key):
    OrcaCredentials.set_api_key(str(uuid4()), check_validity=False)
    yield
    # Need to reset the api key to the original api key so following tests don't fail
    OrcaCredentials.set_api_key(api_key, check_validity=False)


@pytest.fixture()
def other_org_id():
    return _create_org_id()


@pytest.fixture()
def unauthorized(api_key, other_org_id):
    different_api_key = _create_api_key(org_id=other_org_id, name="orca_sdk_test_other_org")
    OrcaCredentials.set_api_key(different_api_key, check_validity=False)
    yield
    OrcaCredentials.set_api_key(api_key, check_validity=False)
    _delete_org(other_org_id)


@pytest.fixture(scope="session")
def label_names():
    return ["soup", "cats"]


SAMPLE_DATA = [
    {"text": "i love soup", "label": 0, "key": "val1", "score": 0.1, "source_id": "s1"},
    {"text": "cats are cute", "label": 1, "key": "val2", "score": 0.2, "source_id": "s2"},
    {"text": "soup is good", "label": 0, "key": "val3", "score": 0.3, "source_id": "s3"},
    {"text": "i love cats", "label": 1, "key": "val4", "score": 0.4, "source_id": "s4"},
    {"text": "everyone loves cats", "label": 1, "key": "val5", "score": 0.5, "source_id": "s5"},
    {"text": "soup is great for the winter", "label": 0, "key": "val6", "score": 0.6, "source_id": "s6"},
    {"text": "hot soup on a rainy day!", "label": 0, "key": "val7", "score": 0.7, "source_id": "s7"},
    {"text": "cats sleep all day", "label": 1, "key": "val8", "score": 0.8, "source_id": "s8"},
    {"text": "homemade soup recipes", "label": 0, "key": "val9", "score": 0.9, "source_id": "s9"},
    {"text": "cats purr when happy", "label": 1, "key": "val10", "score": 1.0, "source_id": "s10"},
    {"text": "chicken noodle soup is classic", "label": 0, "key": "val11", "score": 1.1, "source_id": "s11"},
    {"text": "kittens are baby cats", "label": 1, "key": "val12", "score": 1.2, "source_id": "s12"},
    {"text": "soup can be served cold too", "label": 0, "key": "val13", "score": 1.3, "source_id": "s13"},
    {"text": "cats have nine lives", "label": 1, "key": "val14", "score": 1.4, "source_id": "s14"},
    {"text": "tomato soup with grilled cheese", "label": 0, "key": "val15", "score": 1.5, "source_id": "s15"},
    {"text": "cats are independent animals", "label": 1, "key": "val16", "score": 1.6, "source_id": "s16"},
]


@pytest.fixture(scope="session")
def hf_dataset(label_names):
    return Dataset.from_list(
        SAMPLE_DATA,
        features=Features(
            {
                "text": Value("string"),
                "label": ClassLabel(names=label_names),
                "key": Value("string"),
                "score": Value("float"),
                "source_id": Value("string"),
            }
        ),
    )


@pytest.fixture(scope="session")
def datasource(hf_dataset) -> Datasource:
    return Datasource.from_hf_dataset("test_datasource", hf_dataset)


@pytest.fixture(scope="session")
def memoryset(datasource) -> LabeledMemoryset:
    return LabeledMemoryset.create(
        "test_memoryset",
        datasource=datasource,
        embedding_model=PretrainedEmbeddingModel.GTE_BASE,
        value_column="text",
        source_id_column="source_id",
        max_seq_length_override=32,
    )


@pytest.fixture(scope="session")
def model(memoryset) -> ClassificationModel:
    return ClassificationModel.create(
        "test_model", memoryset, num_classes=2, memory_lookup_count=3, description="test_description"
    )
