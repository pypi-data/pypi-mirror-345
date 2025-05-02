import random
from uuid import uuid4

import pytest
from datasets.arrow_dataset import Dataset

from .classification_model import ClassificationModel
from .datasource import Datasource
from .embedding_model import PretrainedEmbeddingModel
from .memoryset import LabeledMemoryset, TaskStatus


def test_create_memoryset(memoryset: LabeledMemoryset, hf_dataset: Dataset, label_names: list[str]):
    assert memoryset is not None
    assert memoryset.name == "test_memoryset"
    assert memoryset.embedding_model == PretrainedEmbeddingModel.GTE_BASE
    assert memoryset.label_names == label_names
    assert memoryset.insertion_status == TaskStatus.COMPLETED
    assert isinstance(memoryset.length, int)
    assert memoryset.length == len(hf_dataset)


def test_create_memoryset_unauthenticated(unauthenticated, datasource):
    with pytest.raises(ValueError, match="Invalid API key"):
        LabeledMemoryset.create("test_memoryset", datasource)


def test_create_memoryset_invalid_input(datasource):
    # invalid name
    with pytest.raises(ValueError, match=r"Invalid input:.*"):
        LabeledMemoryset.create("test memoryset", datasource)
    # invalid datasource
    datasource.id = str(uuid4())
    with pytest.raises(ValueError, match=r"Invalid input:.*"):
        LabeledMemoryset.create("test_memoryset_invalid_datasource", datasource)


def test_create_memoryset_already_exists_error(hf_dataset, label_names, memoryset):
    with pytest.raises(ValueError):
        LabeledMemoryset.from_hf_dataset("test_memoryset", hf_dataset, label_names=label_names, value_column="text")
    with pytest.raises(ValueError):
        LabeledMemoryset.from_hf_dataset(
            "test_memoryset", hf_dataset, label_names=label_names, value_column="text", if_exists="error"
        )


def test_create_memoryset_already_exists_open(hf_dataset, label_names, memoryset):
    # invalid label names
    with pytest.raises(ValueError):
        LabeledMemoryset.from_hf_dataset(
            memoryset.name,
            hf_dataset,
            label_names=["turtles", "frogs"],
            value_column="text",
            if_exists="open",
        )
    # different embedding model
    with pytest.raises(ValueError):
        LabeledMemoryset.from_hf_dataset(
            memoryset.name,
            hf_dataset,
            label_names=label_names,
            embedding_model=PretrainedEmbeddingModel.DISTILBERT,
            if_exists="open",
        )
    opened_memoryset = LabeledMemoryset.from_hf_dataset(
        memoryset.name,
        hf_dataset,
        embedding_model=PretrainedEmbeddingModel.GTE_BASE,
        if_exists="open",
    )
    assert opened_memoryset is not None
    assert opened_memoryset.name == memoryset.name
    assert opened_memoryset.length == len(hf_dataset)


def test_open_memoryset(memoryset, hf_dataset):
    fetched_memoryset = LabeledMemoryset.open(memoryset.name)
    assert fetched_memoryset is not None
    assert fetched_memoryset.name == memoryset.name
    assert fetched_memoryset.length == len(hf_dataset)


def test_open_memoryset_unauthenticated(unauthenticated, memoryset):
    with pytest.raises(ValueError, match="Invalid API key"):
        LabeledMemoryset.open(memoryset.name)


def test_open_memoryset_not_found():
    with pytest.raises(LookupError):
        LabeledMemoryset.open(str(uuid4()))


def test_open_memoryset_invalid_input():
    with pytest.raises(ValueError, match=r"Invalid input:.*"):
        LabeledMemoryset.open("not valid id")


def test_open_memoryset_unauthorized(unauthorized, memoryset):
    with pytest.raises(LookupError):
        LabeledMemoryset.open(memoryset.name)


def test_all_memorysets(memoryset):
    memorysets = LabeledMemoryset.all()
    assert len(memorysets) > 0
    assert any(memoryset.name == memoryset.name for memoryset in memorysets)


def test_all_memorysets_unauthenticated(unauthenticated):
    with pytest.raises(ValueError, match="Invalid API key"):
        LabeledMemoryset.all()


def test_all_memorysets_unauthorized(unauthorized, memoryset):
    assert memoryset not in LabeledMemoryset.all()


def test_drop_memoryset(hf_dataset):
    memoryset = LabeledMemoryset.from_hf_dataset(
        "test_memoryset_delete",
        hf_dataset.select(range(1)),
        value_column="text",
    )
    assert LabeledMemoryset.exists(memoryset.name)
    LabeledMemoryset.drop(memoryset.name)
    assert not LabeledMemoryset.exists(memoryset.name)


def test_drop_memoryset_unauthenticated(unauthenticated, memoryset):
    with pytest.raises(ValueError, match="Invalid API key"):
        LabeledMemoryset.drop(memoryset.name)


def test_drop_memoryset_not_found(memoryset):
    with pytest.raises(LookupError):
        LabeledMemoryset.drop(str(uuid4()))
    # ignores error if specified
    LabeledMemoryset.drop(str(uuid4()), if_not_exists="ignore")


def test_drop_memoryset_unauthorized(unauthorized, memoryset):
    with pytest.raises(LookupError):
        LabeledMemoryset.drop(memoryset.name)


def test_update_memoryset_metadata(memoryset: LabeledMemoryset):
    memoryset.update_metadata(description="New description")
    assert memoryset.description == "New description"


def test_update_memoryset_no_description(memoryset: LabeledMemoryset):
    assert memoryset.description is not None
    memoryset.update_metadata(description=None)
    assert memoryset.description is None


def test_search(memoryset: LabeledMemoryset):
    memory_lookups = memoryset.search(["i love soup", "cats are cute"])
    assert len(memory_lookups) == 2
    assert len(memory_lookups[0]) == 1
    assert len(memory_lookups[1]) == 1
    assert memory_lookups[0][0].label == 0
    assert memory_lookups[1][0].label == 1


def test_search_count(memoryset: LabeledMemoryset):
    memory_lookups = memoryset.search("i love soup", count=3)
    assert len(memory_lookups) == 3
    assert memory_lookups[0].label == 0
    assert memory_lookups[1].label == 0
    assert memory_lookups[2].label == 0


def test_get_memory_at_index(memoryset: LabeledMemoryset, hf_dataset: Dataset, label_names: list[str]):
    memory = memoryset[0]
    assert memory.value == hf_dataset[0]["text"]
    assert memory.label == hf_dataset[0]["label"]
    assert memory.label_name == label_names[hf_dataset[0]["label"]]
    assert memory.source_id == hf_dataset[0]["source_id"]
    assert memory.score == hf_dataset[0]["score"]
    assert memory.key == hf_dataset[0]["key"]
    last_memory = memoryset[-1]
    assert last_memory.value == hf_dataset[-1]["text"]
    assert last_memory.label == hf_dataset[-1]["label"]


def test_get_range_of_memories(memoryset: LabeledMemoryset, hf_dataset: Dataset):
    memories = memoryset[1:3]
    assert len(memories) == 2
    assert memories[0].value == hf_dataset["text"][1]
    assert memories[1].value == hf_dataset["text"][2]


def test_get_memory_by_id(memoryset: LabeledMemoryset, hf_dataset: Dataset):
    memory = memoryset.get(memoryset[0].memory_id)
    assert memory.value == hf_dataset[0]["text"]
    assert memory == memoryset[memory.memory_id]


def test_get_memories_by_id(memoryset: LabeledMemoryset, hf_dataset: Dataset):
    memories = memoryset.get([memoryset[0].memory_id, memoryset[1].memory_id])
    assert len(memories) == 2
    assert memories[0].value == hf_dataset[0]["text"]
    assert memories[1].value == hf_dataset[1]["text"]


def test_query_memoryset(memoryset: LabeledMemoryset):
    memories = memoryset.query(filters=[("label", "==", 1)])
    assert len(memories) == 8
    assert all(memory.label == 1 for memory in memories)
    assert len(memoryset.query(limit=2)) == 2
    assert len(memoryset.query(filters=[("metadata.key", "==", "val1")])) == 1


def test_query_memoryset_with_feedback_metrics(model: ClassificationModel):
    prediction = model.predict("Do you love soup?")
    feedback_name = f"correct_{random.randint(0, 1000000)}"
    prediction.record_feedback(category=feedback_name, value=prediction.label == 0)
    memories = prediction.memoryset.query(filters=[("label", "==", 0)], with_feedback_metrics=True)

    # Get the memory_ids that were actually used in the prediction
    used_memory_ids = {memory.memory_id for memory in prediction.memory_lookups}

    assert len(memories) == 8
    assert all(memory.label == 0 for memory in memories)
    for memory in memories:
        assert memory.feedback_metrics is not None
        if memory.memory_id in used_memory_ids:
            assert feedback_name in memory.feedback_metrics
            assert memory.feedback_metrics[feedback_name]["avg"] == 1.0
            assert memory.feedback_metrics[feedback_name]["count"] == 1
        else:
            assert feedback_name not in memory.feedback_metrics or memory.feedback_metrics[feedback_name]["count"] == 0
        assert isinstance(memory.lookup_count, int)


def test_query_memoryset_with_feedback_metrics_filter(model: ClassificationModel):
    prediction = model.predict("Do you love soup?")
    prediction.record_feedback(category="accurate", value=prediction.label == 0)
    memories = prediction.memoryset.query(
        filters=[("feedback_metrics.accurate.avg", ">", 0.5)], with_feedback_metrics=True
    )
    assert len(memories) == 3
    assert all(memory.label == 0 for memory in memories)
    for memory in memories:
        assert memory.feedback_metrics is not None
        assert memory.feedback_metrics["accurate"] is not None
        assert memory.feedback_metrics["accurate"]["avg"] == 1.0
        assert memory.feedback_metrics["accurate"]["count"] == 1


def test_query_memoryset_with_feedback_metrics_sort(model: ClassificationModel):
    prediction = model.predict("Do you love soup?")
    prediction.record_feedback(category="positive", value=1.0)
    prediction2 = model.predict("Do you like cats?")
    prediction2.record_feedback(category="positive", value=-1.0)

    memories = prediction.memoryset.query(
        filters=[("feedback_metrics.positive.avg", ">=", -1.0)],
        sort=[("feedback_metrics.positive.avg", "desc")],
        with_feedback_metrics=True,
    )
    assert (
        len(memories) == 6
    )  # there are only 6 out of 16 memories that have a positive feedback metric. Look at SAMPLE_DATA in conftest.py
    assert memories[0].feedback_metrics["positive"]["avg"] == 1.0
    assert memories[-1].feedback_metrics["positive"]["avg"] == -1.0


def test_insert_memories(memoryset: LabeledMemoryset):
    memoryset.refresh()
    prev_length = memoryset.length
    memoryset.insert(
        [
            dict(value="tomato soup is my favorite", label=0),
            dict(value="cats are fun to play with", label=1),
        ]
    )
    assert memoryset.length == prev_length + 2
    memoryset.insert(dict(value="tomato soup is my favorite", label=0, key="test", source_id="test"))
    assert memoryset.length == prev_length + 3
    last_memory = memoryset[-1]
    assert last_memory.value == "tomato soup is my favorite"
    assert last_memory.label == 0
    assert last_memory.metadata
    assert last_memory.metadata["key"] == "test"
    assert last_memory.source_id == "test"


def test_update_memory(memoryset: LabeledMemoryset, hf_dataset: Dataset):
    memory_id = memoryset[0].memory_id
    updated_memory = memoryset.update(dict(memory_id=memory_id, value="i love soup so much"))
    assert updated_memory.value == "i love soup so much"
    assert updated_memory.label == hf_dataset[0]["label"]
    assert memoryset.get(memory_id).value == "i love soup so much"


def test_update_memory_instance(memoryset: LabeledMemoryset, hf_dataset: Dataset):
    memory = memoryset[0]
    updated_memory = memory.update(value="i love soup even more")
    assert updated_memory is memory
    assert memory.value == "i love soup even more"
    assert memory.label == hf_dataset[0]["label"]


def test_update_memories(memoryset: LabeledMemoryset):
    memory_ids = [memory.memory_id for memory in memoryset[:2]]
    updated_memories = memoryset.update(
        [
            dict(memory_id=memory_ids[0], value="i love soup so much"),
            dict(memory_id=memory_ids[1], value="cats are so cute"),
        ]
    )
    assert updated_memories[0].value == "i love soup so much"
    assert updated_memories[1].value == "cats are so cute"


def test_delete_memory(memoryset: LabeledMemoryset):
    memoryset.refresh()
    prev_length = memoryset.length
    memory_id = memoryset[0].memory_id
    memoryset.delete(memory_id)
    with pytest.raises(LookupError):
        memoryset.get(memory_id)
    assert memoryset.length == prev_length - 1


def test_delete_memories(memoryset: LabeledMemoryset):
    prev_length = memoryset.length
    memoryset.delete([memoryset[0].memory_id, memoryset[1].memory_id])
    assert memoryset.length == prev_length - 2


def test_clone_memoryset(memoryset: LabeledMemoryset):
    cloned_memoryset = memoryset.clone("test_cloned_memoryset", embedding_model=PretrainedEmbeddingModel.DISTILBERT)
    assert cloned_memoryset is not None
    assert cloned_memoryset.name == "test_cloned_memoryset"
    assert cloned_memoryset.length == memoryset.length
    assert cloned_memoryset.embedding_model == PretrainedEmbeddingModel.DISTILBERT
    assert cloned_memoryset.insertion_status == TaskStatus.COMPLETED


def test_embedding_evaluation(hf_dataset):
    datasource = Datasource.from_hf_dataset("eval_datasource", hf_dataset, if_exists="open")
    response = LabeledMemoryset.run_embedding_evaluation(
        datasource, embedding_models=["CDE_SMALL"], neighbor_count=2, value_column="text"
    )
    assert response is not None
    assert isinstance(response, dict)
    assert response is not None
    assert isinstance(response["evaluation_results"], list)
    assert len(response["evaluation_results"]) == 1
    assert response["evaluation_results"][0] is not None
    assert response["evaluation_results"][0]["embedding_model_name"] == "CDE_SMALL"
    assert response["evaluation_results"][0]["embedding_model_path"] == "OrcaDB/cde-small-v1"
    Datasource.drop("eval_datasource")


@pytest.fixture(scope="function")
async def test_group_potential_duplicates(memoryset: LabeledMemoryset):
    memoryset.insert(
        [
            dict(value="raspberry soup Is my favorite", label=0),
            dict(value="Raspberry soup is MY favorite", label=0),
            dict(value="rAspberry soup is my favorite", label=0),
            dict(value="raSpberry SOuP is my favorite", label=0),
            dict(value="rasPberry SOuP is my favorite", label=0),
            dict(value="bunny rabbit Is not my mom", label=1),
            dict(value="bunny rabbit is not MY mom", label=1),
            dict(value="bunny rabbit Is not my moM", label=1),
            dict(value="bunny rabbit is not my mom", label=1),
            dict(value="bunny rabbit is not my mom", label=1),
            dict(value="bunny rabbit is not My mom", label=1),
        ]
    )

    memoryset.analyze({"name": "duplicate", "possible_duplicate_threshold": 0.97})
    response = memoryset.get_potential_duplicate_groups()
    assert isinstance(response, list)
    assert sorted([len(res) for res in response]) == [5, 6]  # 5 favorite, 6 mom
