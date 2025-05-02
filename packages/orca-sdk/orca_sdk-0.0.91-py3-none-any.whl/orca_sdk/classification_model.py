from __future__ import annotations

import logging
from contextlib import contextmanager
from datetime import datetime
from typing import Any, Generator, Iterable, Literal, cast, overload
from uuid import UUID

from ._generated_api_client.api import (
    create_evaluation,
    create_model,
    delete_model,
    get_evaluation,
    get_model,
    list_models,
    list_predictions,
    predict_gpu,
    record_prediction_feedback,
    update_model,
)
from ._generated_api_client.models import (
    CreateRACModelRequest,
    EvaluationRequest,
    ListPredictionsRequest,
)
from ._generated_api_client.models import (
    PredictionSortItemItemType0 as PredictionSortColumns,
)
from ._generated_api_client.models import (
    PredictionSortItemItemType1 as PredictionSortDirection,
)
from ._generated_api_client.models import (
    RACHeadType,
    RACModelMetadata,
    RACModelUpdate,
)
from ._generated_api_client.models.prediction_request import PredictionRequest
from ._utils.common import UNSET, CreateMode, DropMode
from ._utils.task import wait_for_task
from .datasource import Datasource
from .memoryset import LabeledMemoryset
from .telemetry import LabelPrediction, _parse_feedback


class ClassificationModel:
    """
    A handle to a classification model in OrcaCloud

    Attributes:
        id: Unique identifier for the model
        name: Unique name of the model
        description: Optional description of the model
        memoryset: Memoryset that the model uses
        head_type: Classification head type of the model
        num_classes: Number of distinct classes the model can predict
        memory_lookup_count: Number of memories the model uses for each prediction
        weigh_memories: If using a KNN head, whether the model weighs memories by their lookup score
        min_memory_weight: If using a KNN head, minimum lookup score memories have to be over to not be ignored
        created_at: When the model was created
    """

    id: str
    name: str
    description: str | None
    memoryset: LabeledMemoryset
    head_type: RACHeadType
    num_classes: int
    memory_lookup_count: int
    weigh_memories: bool | None
    min_memory_weight: float | None
    version: int
    created_at: datetime

    def __init__(self, metadata: RACModelMetadata):
        # for internal use only, do not document
        self.id = metadata.id
        self.name = metadata.name
        self.description = metadata.description
        self.memoryset = LabeledMemoryset.open(metadata.memoryset_id)
        self.head_type = metadata.head_type
        self.num_classes = metadata.num_classes
        self.memory_lookup_count = metadata.memory_lookup_count
        self.weigh_memories = metadata.weigh_memories
        self.min_memory_weight = metadata.min_memory_weight
        self.version = metadata.version
        self.created_at = metadata.created_at

        self._memoryset_override_id: str | None = None
        self._last_prediction: LabelPrediction | None = None
        self._last_prediction_was_batch: bool = False

    def __eq__(self, other) -> bool:
        return isinstance(other, ClassificationModel) and self.id == other.id

    def __repr__(self):
        return (
            "ClassificationModel({\n"
            f"    name: '{self.name}',\n"
            f"    head_type: {self.head_type},\n"
            f"    num_classes: {self.num_classes},\n"
            f"    memory_lookup_count: {self.memory_lookup_count},\n"
            f"    memoryset: LabeledMemoryset.open('{self.memoryset.name}'),\n"
            "})"
        )

    @property
    def last_prediction(self) -> LabelPrediction:
        """
        Last prediction made by the model

        Note:
            If the last prediction was part of a batch prediction, the last prediction from the
            batch is returned. If no prediction has been made yet, a [`LookupError`][LookupError]
            is raised.
        """
        if self._last_prediction_was_batch:
            logging.warning(
                "Last prediction was part of a batch prediction, returning the last prediction from the batch"
            )
        if self._last_prediction is None:
            raise LookupError("No prediction has been made yet")
        return self._last_prediction

    @classmethod
    def create(
        cls,
        name: str,
        memoryset: LabeledMemoryset,
        head_type: Literal["BMMOE", "FF", "KNN", "MMOE"] = "KNN",
        *,
        description: str | None = None,
        num_classes: int | None = None,
        memory_lookup_count: int | None = None,
        weigh_memories: bool = True,
        min_memory_weight: float | None = None,
        if_exists: CreateMode = "error",
    ) -> ClassificationModel:
        """
        Create a new classification model

        Params:
            name: Name for the new model (must be unique)
            memoryset: Memoryset to attach the model to
            head_type: Type of model head to use
            num_classes: Number of classes this model can predict, will be inferred from memoryset if not specified
            memory_lookup_count: Number of memories to lookup for each prediction,
                by default the system uses a simple heuristic to choose a number of memories that works well in most cases
            weigh_memories: If using a KNN head, whether the model weighs memories by their lookup score
            min_memory_weight: If using a KNN head, minimum lookup score memories have to be over to not be ignored
            if_exists: What to do if a model with the same name already exists, defaults to
                `"error"`. Other option is `"open"` to open the existing model.
            description: Optional description for the model, this will be used in agentic flows,
                so make sure it is concise and describes the purpose of your model.

        Returns:
            Handle to the new model in the OrcaCloud

        Raises:
            ValueError: If the model already exists and if_exists is `"error"` or if it is
                `"open"` and the existing model has different attributes.

        Examples:
            Create a new model using default options:
            >>> model = ClassificationModel.create(
            ...    "my_model",
            ...    LabeledMemoryset.open("my_memoryset"),
            ... )

            Create a new model with non-default model head and options:
            >>> model = ClassificationModel.create(
            ...     name="my_model",
            ...     memoryset=LabeledMemoryset.open("my_memoryset"),
            ...     head_type=RACHeadType.MMOE,
            ...     num_classes=5,
            ...     memory_lookup_count=20,
            ... )
        """
        if cls.exists(name):
            if if_exists == "error":
                raise ValueError(f"Model with name {name} already exists")
            elif if_exists == "open":
                existing = cls.open(name)
                for attribute in {"head_type", "memory_lookup_count", "num_classes", "min_memory_weight"}:
                    local_attribute = locals()[attribute]
                    existing_attribute = getattr(existing, attribute)
                    if local_attribute is not None and local_attribute != existing_attribute:
                        raise ValueError(f"Model with name {name} already exists with different {attribute}")

                # special case for memoryset
                if existing.memoryset.id != memoryset.id:
                    raise ValueError(f"Model with name {name} already exists with different memoryset")

                return existing

        metadata = create_model(
            body=CreateRACModelRequest(
                name=name,
                memoryset_id=memoryset.id,
                head_type=RACHeadType(head_type),
                memory_lookup_count=memory_lookup_count,
                num_classes=num_classes,
                weigh_memories=weigh_memories,
                min_memory_weight=min_memory_weight,
                description=description,
            ),
        )
        return cls(metadata)

    @classmethod
    def open(cls, name: str) -> ClassificationModel:
        """
        Get a handle to a classification model in the OrcaCloud

        Params:
            name: Name or unique identifier of the classification model

        Returns:
            Handle to the existing classification model in the OrcaCloud

        Raises:
            LookupError: If the classification model does not exist
        """
        return cls(get_model(name))

    @classmethod
    def exists(cls, name_or_id: str) -> bool:
        """
        Check if a classification model exists in the OrcaCloud

        Params:
            name_or_id: Name or id of the classification model

        Returns:
            `True` if the classification model exists, `False` otherwise
        """
        try:
            cls.open(name_or_id)
            return True
        except LookupError:
            return False

    @classmethod
    def all(cls) -> list[ClassificationModel]:
        """
        Get a list of handles to all classification models in the OrcaCloud

        Returns:
            List of handles to all classification models in the OrcaCloud
        """
        return [cls(metadata) for metadata in list_models()]

    @classmethod
    def drop(cls, name_or_id: str, if_not_exists: DropMode = "error"):
        """
        Delete a classification model from the OrcaCloud

        Warning:
            This will delete the model and all associated data, including predictions, evaluations, and feedback.

        Params:
            name_or_id: Name or id of the classification model
            if_not_exists: What to do if the classification model does not exist, defaults to `"error"`.
                Other option is `"ignore"` to do nothing if the classification model does not exist.

        Raises:
            LookupError: If the classification model does not exist and if_not_exists is `"error"`
        """
        try:
            delete_model(name_or_id)
            logging.info(f"Deleted model {name_or_id}")
        except LookupError:
            if if_not_exists == "error":
                raise

    def refresh(self):
        """Refresh the model data from the OrcaCloud"""
        self.__dict__.update(ClassificationModel.open(self.name).__dict__)

    def update_metadata(self, *, description: str | None = UNSET) -> None:
        """
        Update editable classification model metadata properties.

        Params:
            description: Value to set for the description, defaults to `[UNSET]` if not provided.

        Examples:
            Update the description:
            >>> model.update(description="New description")

            Remove description:
            >>> model.update(description=None)
        """
        update_model(self.id, body=RACModelUpdate(description=description))
        self.refresh()

    @overload
    def predict(
        self,
        value: list[str],
        expected_labels: list[int] | None = None,
        tags: set[str] = set(),
        disable_telemetry: bool = False,
    ) -> list[LabelPrediction]:
        pass

    @overload
    def predict(
        self,
        value: str,
        expected_labels: int | None = None,
        tags: set[str] = set(),
        disable_telemetry: bool = False,
    ) -> LabelPrediction:
        pass

    def predict(
        self,
        value: list[str] | str,
        expected_labels: list[int] | int | None = None,
        tags: set[str] = set(),
        disable_telemetry: bool = False,
    ) -> list[LabelPrediction] | LabelPrediction:
        """
        Predict label(s) for the given input value(s) grounded in similar memories

        Params:
            value: Value(s) to get predict the labels of
            expected_labels: Expected label(s) for the given input to record for model evaluation
            tags: Tags to add to the prediction(s)
            disable_telemetry: Whether to disable telemetry for the prediction(s)

        Returns:
            Label prediction or list of label predictions

        Examples:
            Predict the label for a single value:
            >>> prediction = model.predict("I am happy", tags={"test"})
            LabelPrediction({label: <positive: 1>, confidence: 0.95, anomaly_score: 0.1, input_value: 'I am happy' })

            Predict the labels for a list of values:
            >>> predictions = model.predict(["I am happy", "I am sad"], expected_labels=[1, 0])
            [
                LabelPrediction({label: <positive: 1>, confidence: 0.95, anomaly_score: 0.1, input_value: 'I am happy'}),
                LabelPrediction({label: <negative: 0>, confidence: 0.05, anomaly_score: 0.1, input_value: 'I am sad'}),
            ]
        """

        response = predict_gpu(
            self.id,
            body=PredictionRequest(
                input_values=value if isinstance(value, list) else [value],
                memoryset_override_id=self._memoryset_override_id,
                expected_labels=(
                    expected_labels
                    if isinstance(expected_labels, list)
                    else [expected_labels] if expected_labels is not None else None
                ),
                tags=list(tags),
                disable_telemetry=disable_telemetry,
            ),
        )

        if not disable_telemetry and any(p.prediction_id is None for p in response):
            raise RuntimeError("Failed to save prediction to database.")

        predictions = [
            LabelPrediction(
                prediction_id=prediction.prediction_id,
                label=prediction.label,
                label_name=prediction.label_name,
                confidence=prediction.confidence,
                anomaly_score=prediction.anomaly_score,
                memoryset=self.memoryset,
                model=self,
            )
            for prediction in response
        ]
        self._last_prediction_was_batch = isinstance(value, list)
        self._last_prediction = predictions[-1]
        return predictions if isinstance(value, list) else predictions[0]

    def predictions(
        self,
        limit: int = 100,
        offset: int = 0,
        tag: str | None = None,
        sort: list[tuple[PredictionSortColumns, PredictionSortDirection]] = [],
        expected_label_match: bool | None = None,
    ) -> list[LabelPrediction]:
        """
        Get a list of predictions made by this model

        Params:
            limit: Optional maximum number of predictions to return
            offset: Optional offset of the first prediction to return
            tag: Optional tag to filter predictions by
            sort: Optional list of columns and directions to sort the predictions by.
                Predictions can be sorted by `timestamp` or `confidence`.
            expected_label_match: Optional filter to only include predictions where the expected
                label does (`True`) or doesn't (`False`) match the predicted label

        Returns:
            List of label predictions

        Examples:
            Get the last 3 predictions:
            >>> predictions = model.predictions(limit=3, sort=[("timestamp", "desc")])
            [
                LabeledPrediction({label: <positive: 1>, confidence: 0.95, anomaly_score: 0.1, input_value: 'I am happy'}),
                LabeledPrediction({label: <negative: 0>, confidence: 0.05, anomaly_score: 0.1, input_value: 'I am sad'}),
                LabeledPrediction({label: <positive: 1>, confidence: 0.90, anomaly_score: 0.1, input_value: 'I am ecstatic'}),
            ]


            Get second most confident prediction:
            >>> predictions = model.predictions(sort=[("confidence", "desc")], offset=1, limit=1)
            [LabeledPrediction({label: <positive: 1>, confidence: 0.90, anomaly_score: 0.1, input_value: 'I am having a good day'})]

            Get predictions where the expected label doesn't match the predicted label:
            >>> predictions = model.predictions(expected_label_match=False)
            [LabeledPrediction({label: <positive: 1>, confidence: 0.95, anomaly_score: 0.1, input_value: 'I am happy', expected_label: 0})]
        """
        predictions = list_predictions(
            body=ListPredictionsRequest(
                model_id=self.id,
                limit=limit,
                offset=offset,
                sort=cast(list[list[PredictionSortColumns | PredictionSortDirection]], sort),
                tag=tag,
                expected_label_match=expected_label_match,
            ),
        )
        return [
            LabelPrediction(
                prediction_id=prediction.prediction_id,
                label=prediction.label,
                label_name=prediction.label_name,
                confidence=prediction.confidence,
                anomaly_score=prediction.anomaly_score,
                memoryset=self.memoryset,
                model=self,
                telemetry=prediction,
            )
            for prediction in predictions
        ]

    def evaluate(
        self,
        datasource: Datasource,
        value_column: str = "value",
        label_column: str = "label",
        record_predictions: bool = False,
        tags: set[str] | None = None,
    ) -> dict[str, Any]:
        """
        Evaluate the classification model on a given datasource

        Params:
            datasource: Datasource to evaluate the model on
            value_column: Name of the column that contains the input values to the model
            label_column: Name of the column containing the expected labels
            record_predictions: Whether to record [`LabelPrediction`][orca_sdk.telemetry.LabelPrediction]s for analysis
            tags: Optional tags to add to the recorded [`LabelPrediction`][orca_sdk.telemetry.LabelPrediction]s

        Returns:
            Dictionary with evaluation metrics

        Examples:
            >>> model.evaluate(datasource, value_column="text", label_column="airline_sentiment")
            { "f1_score": 0.85, "roc_auc": 0.85, "pr_auc": 0.85, "accuracy": 0.85, "loss": 0.35, ... }
        """
        response = create_evaluation(
            self.id,
            body=EvaluationRequest(
                datasource_id=datasource.id,
                datasource_label_column=label_column,
                datasource_value_column=value_column,
                memoryset_override_id=self._memoryset_override_id,
                record_telemetry=record_predictions,
                telemetry_tags=list(tags) if tags else None,
            ),
        )
        wait_for_task(response.task_id, description="Running evaluation")
        response = get_evaluation(self.id, UUID(response.task_id))
        assert response.result is not None
        return response.result.to_dict()

    def finetune(self, datasource: Datasource):
        #  do not document until implemented
        raise NotImplementedError("Finetuning is not supported yet")

    @contextmanager
    def use_memoryset(self, memoryset_override: LabeledMemoryset) -> Generator[None, None, None]:
        """
        Temporarily override the memoryset used by the model for predictions

        Params:
            memoryset_override: Memoryset to override the default memoryset with

        Examples:
            >>> with model.use_memoryset(LabeledMemoryset.open("my_other_memoryset")):
            ...     predictions = model.predict("I am happy")
        """
        self._memoryset_override_id = memoryset_override.id
        yield
        self._memoryset_override_id = None

    @overload
    def record_feedback(self, feedback: dict[str, Any]) -> None:
        pass

    @overload
    def record_feedback(self, feedback: Iterable[dict[str, Any]]) -> None:
        pass

    def record_feedback(self, feedback: Iterable[dict[str, Any]] | dict[str, Any]):
        """
        Record feedback for a list of predictions.

        We support recording feedback in several categories for each prediction. A
        [`FeedbackCategory`][orca_sdk.telemetry.FeedbackCategory] is created automatically,
        the first time feedback with a new name is recorded. Categories are global across models.
        The value type of the category is inferred from the first recorded value. Subsequent
        feedback for the same category must be of the same type.

        Params:
            feedback: Feedback to record, this should be dictionaries with the following keys:

                - `category`: Name of the category under which to record the feedback.
                - `value`: Feedback value to record, should be `True` for positive feedback and
                    `False` for negative feedback or a [`float`][float] between `-1.0` and `+1.0`
                    where negative values indicate negative feedback and positive values indicate
                    positive feedback.
                - `comment`: Optional comment to record with the feedback.

        Examples:
            Record whether predictions were correct or incorrect:
            >>> model.record_feedback({
            ...     "prediction": p.prediction_id,
            ...     "category": "correct",
            ...     "value": p.label == p.expected_label,
            ... } for p in predictions)

            Record star rating as normalized continuous score between `-1.0` and `+1.0`:
            >>> model.record_feedback({
            ...     "prediction": "123e4567-e89b-12d3-a456-426614174000",
            ...     "category": "rating",
            ...     "value": -0.5,
            ...     "comment": "2 stars"
            ... })

        Raises:
            ValueError: If the value does not match previous value types for the category, or is a
                [`float`][float] that is not between `-1.0` and `+1.0`.
        """
        record_prediction_feedback(
            body=[
                _parse_feedback(f) for f in (cast(list[dict], [feedback]) if isinstance(feedback, dict) else feedback)
            ],
        )
