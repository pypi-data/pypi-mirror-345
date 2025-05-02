from uuid import uuid4

import pytest
from datasets.arrow_dataset import Dataset

from .classification_model import ClassificationModel
from .datasource import Datasource
from .embedding_model import PretrainedEmbeddingModel
from .memoryset import LabeledMemoryset


def test_create_model(model: ClassificationModel, memoryset: LabeledMemoryset):
    assert model is not None
    assert model.name == "test_model"
    assert model.memoryset == memoryset
    assert model.num_classes == 2
    assert model.memory_lookup_count == 3


def test_create_model_already_exists_error(memoryset, model: ClassificationModel):
    with pytest.raises(ValueError):
        ClassificationModel.create("test_model", memoryset)
    with pytest.raises(ValueError):
        ClassificationModel.create("test_model", memoryset, if_exists="error")


def test_create_model_already_exists_return(memoryset, model: ClassificationModel):
    with pytest.raises(ValueError):
        ClassificationModel.create("test_model", memoryset, if_exists="open", head_type="MMOE")

    with pytest.raises(ValueError):
        ClassificationModel.create("test_model", memoryset, if_exists="open", memory_lookup_count=37)

    with pytest.raises(ValueError):
        ClassificationModel.create("test_model", memoryset, if_exists="open", num_classes=19)

    with pytest.raises(ValueError):
        ClassificationModel.create("test_model", memoryset, if_exists="open", min_memory_weight=0.77)

    new_model = ClassificationModel.create("test_model", memoryset, if_exists="open")
    assert new_model is not None
    assert new_model.name == "test_model"
    assert new_model.memoryset == memoryset
    assert new_model.num_classes == 2
    assert new_model.memory_lookup_count == 3


def test_create_model_unauthenticated(unauthenticated, memoryset: LabeledMemoryset):
    with pytest.raises(ValueError, match="Invalid API key"):
        ClassificationModel.create("test_model", memoryset)


def test_get_model(model: ClassificationModel):
    fetched_model = ClassificationModel.open(model.name)
    assert fetched_model is not None
    assert fetched_model.id == model.id
    assert fetched_model.name == model.name
    assert fetched_model.num_classes == 2
    assert fetched_model.memory_lookup_count == 3
    assert fetched_model == model


def test_get_model_unauthenticated(unauthenticated):
    with pytest.raises(ValueError, match="Invalid API key"):
        ClassificationModel.open("test_model")


def test_get_model_invalid_input():
    with pytest.raises(ValueError, match="Invalid input"):
        ClassificationModel.open("not valid id")


def test_get_model_not_found():
    with pytest.raises(LookupError):
        ClassificationModel.open(str(uuid4()))


def test_get_model_unauthorized(unauthorized, model: ClassificationModel):
    with pytest.raises(LookupError):
        ClassificationModel.open(model.name)


def test_list_models(model: ClassificationModel):
    models = ClassificationModel.all()
    assert len(models) > 0
    assert any(model.name == model.name for model in models)


def test_list_models_unauthenticated(unauthenticated):
    with pytest.raises(ValueError, match="Invalid API key"):
        ClassificationModel.all()


def test_list_models_unauthorized(unauthorized, model: ClassificationModel):
    assert ClassificationModel.all() == []


def test_update_model(model: ClassificationModel):
    model.update_metadata(description="New description")
    assert model.description == "New description"


def test_update_model_no_description(model: ClassificationModel):
    assert model.description is not None
    model.update_metadata(description=None)
    assert model.description is None


def test_delete_model(memoryset: LabeledMemoryset):
    ClassificationModel.create("model_to_delete", LabeledMemoryset.open(memoryset.name))
    assert ClassificationModel.open("model_to_delete")
    ClassificationModel.drop("model_to_delete")
    with pytest.raises(LookupError):
        ClassificationModel.open("model_to_delete")


def test_delete_model_unauthenticated(unauthenticated, model: ClassificationModel):
    with pytest.raises(ValueError, match="Invalid API key"):
        ClassificationModel.drop(model.name)


def test_delete_model_not_found():
    with pytest.raises(LookupError):
        ClassificationModel.drop(str(uuid4()))
    # ignores error if specified
    ClassificationModel.drop(str(uuid4()), if_not_exists="ignore")


def test_delete_model_unauthorized(unauthorized, model: ClassificationModel):
    with pytest.raises(LookupError):
        ClassificationModel.drop(model.name)


def test_delete_memoryset_before_model_constraint_violation(hf_dataset):
    memoryset = LabeledMemoryset.from_hf_dataset("test_memoryset_delete_before_model", hf_dataset, value_column="text")
    ClassificationModel.create("test_model_delete_before_memoryset", memoryset)
    with pytest.raises(RuntimeError):
        LabeledMemoryset.drop(memoryset.id)


def test_evaluate(model):
    eval_datasource = Datasource.from_list(
        "eval_datasource",
        [
            {"text": "chicken noodle soup is the best", "label": 1},
            {"text": "cats are cute", "label": 0},
            {"text": "soup is great for the winter", "label": 0},
            {"text": "i love cats", "label": 1},
        ],
    )
    result = model.evaluate(eval_datasource, value_column="text")
    assert result is not None
    assert isinstance(result, dict)
    assert isinstance(result["accuracy"], float)
    assert isinstance(result["f1_score"], float)
    assert isinstance(result["loss"], float)
    assert len(result["precision_recall_curve"]["thresholds"]) == 4
    assert len(result["precision_recall_curve"]["precisions"]) == 4
    assert len(result["precision_recall_curve"]["recalls"]) == 4
    assert len(result["roc_curve"]["thresholds"]) == 4
    assert len(result["roc_curve"]["false_positive_rates"]) == 4
    assert len(result["roc_curve"]["true_positive_rates"]) == 4


def test_evaluate_with_telemetry(model):
    samples = [
        {"text": "chicken noodle soup is the best", "label": 1},
        {"text": "cats are cute", "label": 0},
    ]
    eval_datasource = Datasource.from_list("eval_datasource_2", samples)
    result = model.evaluate(eval_datasource, value_column="text", record_predictions=True, tags={"test"})
    assert result is not None
    predictions = model.predictions(tag="test")
    assert len(predictions) == 2
    assert all(p.tags == {"test"} for p in predictions)
    assert all(p.expected_label == s["label"] for p, s in zip(predictions, samples))


def test_predict(model: ClassificationModel, label_names: list[str]):
    predictions = model.predict(["Do you love soup?", "Are cats cute?"])
    assert len(predictions) == 2
    assert predictions[0].prediction_id is not None
    assert predictions[1].prediction_id is not None
    assert predictions[0].label == 0
    assert predictions[0].label_name == label_names[0]
    assert 0 <= predictions[0].confidence <= 1
    assert predictions[1].label == 1
    assert predictions[1].label_name == label_names[1]
    assert 0 <= predictions[1].confidence <= 1


def test_predict_disable_telemetry(model: ClassificationModel, label_names: list[str]):
    predictions = model.predict(["Do you love soup?", "Are cats cute?"], disable_telemetry=True)
    assert len(predictions) == 2
    assert predictions[0].prediction_id is None
    assert predictions[1].prediction_id is None
    assert predictions[0].label == 0
    assert predictions[0].label_name == label_names[0]
    assert 0 <= predictions[0].confidence <= 1
    assert predictions[1].label == 1
    assert predictions[1].label_name == label_names[1]
    assert 0 <= predictions[1].confidence <= 1


def test_predict_unauthenticated(unauthenticated, model: ClassificationModel):
    with pytest.raises(ValueError, match="Invalid API key"):
        model.predict(["Do you love soup?", "Are cats cute?"])


def test_predict_unauthorized(unauthorized, model: ClassificationModel):
    with pytest.raises(LookupError):
        model.predict(["Do you love soup?", "Are cats cute?"])


def test_predict_constraint_violation(memoryset: LabeledMemoryset):
    model = ClassificationModel.create(
        "test_model_lookup_count_too_high", memoryset, num_classes=2, memory_lookup_count=memoryset.length + 2
    )
    with pytest.raises(RuntimeError):
        model.predict("test")


def test_record_prediction_feedback(model: ClassificationModel):
    predictions = model.predict(["Do you love soup?", "Are cats cute?"])
    expected_labels = [0, 1]
    model.record_feedback(
        {
            "prediction_id": p.prediction_id,
            "category": "correct",
            "value": p.label == expected_label,
        }
        for expected_label, p in zip(expected_labels, predictions)
    )


def test_record_prediction_feedback_missing_category(model: ClassificationModel):
    prediction = model.predict("Do you love soup?")
    with pytest.raises(ValueError):
        model.record_feedback({"prediction_id": prediction.prediction_id, "value": True})


def test_record_prediction_feedback_invalid_value(model: ClassificationModel):
    prediction = model.predict("Do you love soup?")
    with pytest.raises(ValueError, match=r"Invalid input.*"):
        model.record_feedback({"prediction_id": prediction.prediction_id, "category": "correct", "value": "invalid"})


def test_record_prediction_feedback_invalid_prediction_id(model: ClassificationModel):
    with pytest.raises(ValueError, match=r"Invalid input.*"):
        model.record_feedback({"prediction_id": "invalid", "category": "correct", "value": True})


def test_predict_with_memoryset_override(model: ClassificationModel, hf_dataset: Dataset):
    inverted_labeled_memoryset = LabeledMemoryset.from_hf_dataset(
        "test_memoryset_inverted_labels",
        hf_dataset.map(lambda x: {"label": 1 if x["label"] == 0 else 0}),
        value_column="text",
        embedding_model=PretrainedEmbeddingModel.GTE_BASE,
    )
    with model.use_memoryset(inverted_labeled_memoryset):
        predictions = model.predict(["Do you love soup?", "Are cats cute?"])
        assert predictions[0].label == 1
        assert predictions[1].label == 0

    predictions = model.predict(["Do you love soup?", "Are cats cute?"])
    assert predictions[0].label == 0
    assert predictions[1].label == 1


def test_predict_with_expected_labels(model: ClassificationModel):
    prediction = model.predict("Do you love soup?", expected_labels=1)
    assert prediction.expected_label == 1


def test_predict_with_expected_labels_invalid_input(model: ClassificationModel):
    # invalid number of expected labels for batch prediction
    with pytest.raises(ValueError, match=r"Invalid input.*"):
        model.predict(["Do you love soup?", "Are cats cute?"], expected_labels=[0])
    # invalid label value
    with pytest.raises(ValueError):
        model.predict("Do you love soup?", expected_labels=5)


def test_last_prediction_with_batch(model: ClassificationModel):
    predictions = model.predict(["Do you love soup?", "Are cats cute?"])
    assert model.last_prediction is not None
    assert model.last_prediction.prediction_id == predictions[-1].prediction_id
    assert model.last_prediction.input_value == "Are cats cute?"
    assert model._last_prediction_was_batch is True


def test_last_prediction_with_single(model: ClassificationModel):
    # Test that last_prediction is updated correctly with single prediction
    prediction = model.predict("Do you love soup?")
    assert model.last_prediction is not None
    assert model.last_prediction.prediction_id == prediction.prediction_id
    assert model.last_prediction.input_value == "Do you love soup?"
    assert model._last_prediction_was_batch is False
