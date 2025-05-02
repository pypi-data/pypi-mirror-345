from __future__ import annotations

import logging
from datetime import datetime, timezone
from enum import Enum
from typing import Callable, Literal, cast, overload

import numpy as np
import torch
from datasets import Dataset
from numpy.typing import NDArray
from pydantic import BaseModel
from sklearn.metrics import accuracy_score, auc, f1_score, roc_auc_score
from torch import Tensor, nn
from tqdm.auto import trange
from transformers import (
    AutoConfig,
    AutoModelForImageClassification,
    AutoModelForSequenceClassification,
    PretrainedConfig,
)
from transformers.modeling_outputs import SequenceClassifierOutput
from uuid_utils.compat import uuid4

from ..memoryset import InputType, InputTypeList, LabeledMemoryset
from ..torch_layers import (
    BalancedMemoryMixtureOfExpertsClassificationHead,
    FeedForwardClassificationHead,
    MemoryMixtureOfExpertsClassificationHead,
    NearestMemoriesClassificationHead,
)
from ..utils import (
    OnLogCallback,
    OnProgressCallback,
    calculate_pr_curve,
    calculate_roc_curve,
    dir_context,
    parse_dataset,
)
from .base_model import MemoryAugmentedModel
from .model_finetuning import RACTrainingArguments, finetune
from .prediction_types import LabelPredictionMemoryLookup, LabelPredictionWithMemories


class ClassificationEvaluationResult(BaseModel):
    f1_score: float
    """F1 score of the predictions"""

    accuracy: float
    """Accuracy of the predictions"""

    loss: float
    """Cross-entropy loss of the logits"""

    class PrecisionRecallCurve(BaseModel):
        thresholds: list[float]
        precisions: list[float]
        recalls: list[float]
        auc: float

        def __repr__(self) -> str:
            return (
                "PrecisionRecallCurve(\n"
                f"    thresholds={self.thresholds[0]:.4f}...{self.thresholds[-1]:.4f},\n"
                f"    precisions={self.precisions[0]:.4f}...{self.precisions[-1]:.4f},\n"
                f"    recalls={self.recalls[0]:.4f}...{self.recalls[-1]:.4f},\n"
                f"    auc={self.auc:.4f}\n"
            )

    precision_recall_curve: PrecisionRecallCurve | None
    """Precision-recall curve (only for binary classification)"""

    class ROCCurve(BaseModel):
        thresholds: list[float]
        false_positive_rates: list[float]
        true_positive_rates: list[float]
        auc: float

        def __repr__(self) -> str:
            return (
                "ROCCurve(\n"
                f"    thresholds={self.thresholds[0]:.4f}...{self.thresholds[-1]:.4f},\n"
                f"    false_positive_rates={self.false_positive_rates[0]:.4f}...{self.false_positive_rates[-1]:.4f},\n"
                f"    true_positive_rates={self.true_positive_rates[0]:.4f}...{self.true_positive_rates[-1]:.4f},\n"
                f"    auc={self.auc:.4f}\n"
            )

    roc_curve: ROCCurve | None
    """ROC curve (only for binary classification)"""

    def __repr__(self) -> str:
        return (
            "ClassificationEvaluationResult(\n"
            f"    f1_score={self.f1_score:.4f},\n"
            f"    accuracy={self.accuracy:.4f},\n"
            f"    loss={self.loss:.4f},\n"
            f"    precision_recall_curve={self.precision_recall_curve},\n"
            f"    roc_curve={self.roc_curve}\n"
            ")"
        )

    @staticmethod
    def calculate_metrics(
        *,
        logits_array: NDArray[np.float32],
        targets_array: NDArray[np.int64],
        predictions_array: NDArray[np.int64],
        total_loss: float,
    ) -> ClassificationEvaluationResult:
        # Compute metrics
        f1 = float(f1_score(targets_array, predictions_array, average="weighted"))
        accuracy = float(accuracy_score(targets_array, predictions_array))

        # Only compute ROC AUC and PR AUC for binary classification
        unique_classes = np.unique(targets_array)

        pr_curve = None
        roc_curve = None

        if len(unique_classes) == 2:
            try:
                precisions, recalls, pr_thresholds = calculate_pr_curve(targets_array, logits_array)
                pr_auc = float(auc(recalls, precisions))

                pr_curve = ClassificationEvaluationResult.PrecisionRecallCurve(
                    precisions=list(precisions), recalls=list(recalls), thresholds=list(pr_thresholds), auc=pr_auc
                )

                fpr, tpr, roc_thresholds = calculate_roc_curve(targets_array, logits_array)
                roc_auc = float(roc_auc_score(targets_array, logits_array[:, 1]))

                roc_curve = ClassificationEvaluationResult.ROCCurve(
                    false_positive_rates=list(fpr),
                    true_positive_rates=list(tpr),
                    thresholds=list(roc_thresholds),
                    auc=roc_auc,
                )
            except ValueError as e:
                logging.warning(f"Error calculating PR and ROC curves: {e}")

        total_samples = len(targets_array)

        return ClassificationEvaluationResult(
            f1_score=f1,
            accuracy=accuracy,
            loss=total_loss / total_samples,
            precision_recall_curve=pr_curve,
            roc_curve=roc_curve,
        )


class RACHeadType(str, Enum):
    KNN = "KNN"
    MMOE = "MMOE"
    FF = "FF"
    BMMOE = "BMMOE"


class RACModelConfig(PretrainedConfig):
    model_type = "rac-model"

    head_type: RACHeadType
    num_classes: int | None
    memoryset_uri: str | None
    memoryset: LabeledMemoryset
    memory_lookup_count: int | None
    weigh_memories: bool | None
    min_memory_weight: float | None
    num_layers: int | None
    dropout_prob: float | None

    def __init__(
        self,
        memoryset_uri: str | None = None,
        memory_lookup_count: int | None = None,
        head_type: RACHeadType | Literal["MMOE", "BMMOE", "KNN", "FF"] = RACHeadType.MMOE,
        num_classes: int | None = None,
        weigh_memories: bool | None = None,
        min_memory_weight: float | None = None,
        num_layers: int | None = None,
        dropout_prob: float | None = None,
        **kwargs,
    ):
        """
        Initialize the config

        Note:
            While all args of a pretrained config must be optional, `memoryset_uri` must be specified.

        Args:
            memoryset_uri: URI of the memoryset to use, this is required
            memory_lookup_count: Number of memories to lookup for each input,
                by default the system uses a simple heuristic to choose a number of memories that works well in most cases
            head_type: Type of classification head to use
            num_classes: Number of classes to predict, will be inferred from memoryset if not specified
            weigh_memories: Optional parameter for KNN head, whether to weigh memories by their lookup score
            min_memory_weight: Optional parameter for KNN head, minimum memory weight under which memories are ignored
            num_layers: Optional parameter for FF head, number of layers in the feed forward network
            dropout_prob: Optional parameter for FF head, dropout probability
        """
        # We cannot require memoryset_uri here, because this class must be initializable without
        # passing any parameters for the PretrainedConfig.save_pretrained method to work, so instead
        # we throw an error in the RetrievalAugmentedClassifier initializer if it is missing
        self.memoryset_uri = memoryset_uri
        self.memory_lookup_count = memory_lookup_count
        self.head_type = head_type if isinstance(head_type, RACHeadType) else RACHeadType(head_type)
        self.num_classes = num_classes
        self.weigh_memories = weigh_memories
        self.min_memory_weight = min_memory_weight
        self.num_layers = num_layers
        self.dropout_prob = dropout_prob
        super().__init__(**kwargs)


class RACModel(MemoryAugmentedModel[LabeledMemoryset]):
    config_class = RACModelConfig
    base_model_prefix = "rac"
    memory_lookup_count: int

    def _init_head(self):
        # TODO: break this up into three subclasses that inherit from RACModel and have their own con
        match self.config.head_type:
            case RACHeadType.MMOE:
                self.memory_lookup_count = self.config.memory_lookup_count or min(round(self.num_classes * 1.5) * 3, 50)
                self.head = MemoryMixtureOfExpertsClassificationHead(
                    num_classes=self.num_classes,
                    embedding_dim=self.embedding_dim,
                )
            case RACHeadType.BMMOE:
                self.memory_lookup_count = self.config.memory_lookup_count or min(round(self.num_classes * 1.5) * 3, 50)
                self.head = BalancedMemoryMixtureOfExpertsClassificationHead(
                    num_classes=self.num_classes,
                    embedding_dim=self.embedding_dim,
                )
            case RACHeadType.KNN:
                self.memory_lookup_count = self.config.memory_lookup_count or min(round(self.num_classes * 1.5) * 3, 50)
                self.head = NearestMemoriesClassificationHead(
                    num_classes=self.num_classes,
                    weigh_memories=self.config.weigh_memories,
                    min_memory_weight=self.config.min_memory_weight,
                )
            case RACHeadType.FF:
                self.memory_lookup_count = 0
                self.head = FeedForwardClassificationHead(
                    num_classes=self.num_classes,
                    embedding_dim=self.embedding_dim,
                    num_layers=self.config.num_layers,
                )
            case _:
                raise ValueError(f"Unsupported head type: {self.config.head_type}")

    @overload
    def __init__(self, config: RACModelConfig):
        pass

    @overload
    def __init__(
        self,
        *,
        memoryset: LabeledMemoryset | str,
        memory_lookup_count: int | None = None,
        head_type: RACHeadType | Literal["MMOE", "BMMOE", "KNN", "FF"] = RACHeadType.MMOE,
        num_classes: int | None = None,
        weigh_memories: bool = False,
        min_memory_weight: float | None = None,
        num_layers: int | None = None,
        dropout_prob: float | None = None,
    ):
        pass

    def __init__(
        self,
        config: RACModelConfig | None = None,
        *,
        memoryset: LabeledMemoryset | str | None = None,
        memory_lookup_count: int | None = None,
        head_type: RACHeadType | Literal["MMOE", "BMMOE", "KNN", "FF"] = RACHeadType.MMOE,
        num_classes: int | None = None,
        weigh_memories: bool = False,
        min_memory_weight: float | None = None,
        num_layers: int | None = None,
        dropout_prob: float | None = None,
    ):
        if config is None:
            assert memoryset is not None
            if isinstance(memoryset, LabeledMemoryset):
                self.memoryset = memoryset
            else:
                self.memoryset = LabeledMemoryset.connect(memoryset)
            config = RACModelConfig(
                memoryset_uri=self.memoryset.uri,
                memory_lookup_count=memory_lookup_count,
                head_type=head_type,
                num_classes=num_classes,
                weigh_memories=weigh_memories,
                min_memory_weight=min_memory_weight,
                num_layers=num_layers,
                dropout_prob=dropout_prob,
            )
        else:
            assert (
                memoryset is not None
                or memory_lookup_count is not None
                or head_type is not None
                or num_classes is not None
                or weigh_memories is not None
                or min_memory_weight is not None
                or num_layers is not None
                or dropout_prob is not None
            ), "Either config or kwargs can be provided, not both"
            if not config.memoryset_uri:
                # all configs must have defaults in a PretrainedConfig, but this one is required
                raise ValueError("memoryset_uri must be specified in config")
            self.memoryset = LabeledMemoryset.connect(config.memoryset_uri)
        super().__init__(config)
        self.embedding_dim = self.memoryset.embedding_model.embedding_dim
        if config.num_classes is None:
            logging.warning("num_classes not specified in config, using number of classes in memoryset")
            self.num_classes = self.memoryset.num_classes
        else:
            self.num_classes = config.num_classes
        self._init_head()
        self.criterion = nn.CrossEntropyLoss() if config.num_labels > 1 else nn.MSELoss()

    @property
    def num_trainable_parameters(self) -> int:
        """Number of trainable parameters in the model"""
        return self.num_parameters(only_trainable=True)

    def reset(self):
        """
        Reset the model weights to their initial state
        """
        self._init_head()

    def attach(self, memoryset: LabeledMemoryset | str):
        """
        Attach a memoryset to the model

        Args:
            memoryset: The memoryset to attach to the model or a URI to a memoryset
        """
        self.memoryset = memoryset if isinstance(memoryset, LabeledMemoryset) else LabeledMemoryset.connect(memoryset)

    def forward(
        self,
        input_embeddings: Tensor | None = None,
        memories_labels: Tensor | None = None,
        memories_embeddings: Tensor | None = None,
        memories_weights: Tensor | None = None,
        labels: Tensor | None = None,
    ) -> SequenceClassifierOutput:
        logits = self.head(input_embeddings, memories_labels, memories_embeddings, memories_weights)
        loss = self.criterion(logits, labels) if labels is not None else None
        return SequenceClassifierOutput(loss=loss, logits=logits)

    def finetune(
        self,
        checkpoint_dir: str | None = None,
        train_dataset: Dataset | None = None,
        eval_dataset: Dataset | None = None,
        value_column: str = "value",
        label_column: str = "label",
        training_args: RACTrainingArguments = RACTrainingArguments(),
        on_progress: OnProgressCallback | None = None,
        on_log: OnLogCallback | None = None,
    ):
        """
        Finetune the model on a given dataset

        Args:
            checkpoint_dir: The directory to save the checkpoint to, if this is `None` no checkpoint will be saved
            train_dataset: The data to finetune on, if this is `None` the memoryset will be used
            eval_dataset: The data to evaluate the finetuned model on, if this is `None` no evaluations will be performed
            value_column: The column in the dataset that contains the input values
            label_column: The column in the dataset that contains the expected labels
            training_args: The training arguments to use for the finetuning
            on_progress: Callback to report progress
        """
        if not train_dataset:
            train_dataset = self.memoryset.to_dataset()
        else:
            train_dataset = parse_dataset(train_dataset, value_column=value_column, label_column=label_column)
        if eval_dataset:
            eval_dataset = parse_dataset(eval_dataset, value_column=value_column, label_column=label_column)

        finetune(
            self,
            checkpoint_dir=checkpoint_dir,
            train_dataset=train_dataset,
            eval_dataset=eval_dataset,
            training_args=training_args,
            on_progress=on_progress,
            on_log=on_log,
        )

    def evaluate(
        self,
        dataset: Dataset,
        value_column: str = "value",
        label_column: str = "label",
        batch_size: int = 32,
        on_progress: OnProgressCallback | None = None,
        on_predict: Callable[[list[LabelPredictionWithMemories]], None] | None = None,
    ) -> ClassificationEvaluationResult:
        """
        Evaluate the model on a given dataset

        Args:
            dataset: The data to evaluate the model on
            value_column: The column in the dataset that contains the input values
            label_column: The column in the dataset that contains the expected labels
            batch_size: The batch size to use for evaluation
            on_progress: Optional callback to report progress
            on_predict: Optional callback to save telemetry for a batch of predictions

        Returns:
            The evaluation result
        """
        dataset = parse_dataset(dataset, value_column=value_column, label_column=label_column)

        # Track total loss and predictions for computing metrics
        total_loss = 0.0
        all_predictions: list[int] = []
        all_targets: list[int] = []
        all_logits: list[Tensor] = []
        total_samples = 0

        # Process dataset in batches
        if on_progress is not None:
            on_progress(0, len(dataset))
        for i in trange(0, len(dataset), batch_size, disable=on_progress is not None):
            batch = dataset[i : i + batch_size]
            batch_size_actual = len(batch["value"])

            # Get predictions for batch
            predictions = self.predict(batch["value"], use_lookup_cache=True, expected_label=batch["label"])
            if not isinstance(predictions, list):
                predictions = [predictions]

            # Process predictions if callback provided
            if on_predict:
                on_predict(predictions)

            # Extract predictions and targets
            batch_logits = torch.tensor(np.array([p.logits for p in predictions]), device=self.device)
            batch_targets = torch.tensor(batch["label"], device=self.device)

            # Compute loss for batch using logits
            batch_loss = self.criterion(batch_logits, batch_targets).item()

            # Get predicted labels from logits for metrics
            batch_predictions = [p.label for p in predictions]

            # Accumulate results
            total_loss += batch_loss * batch_size_actual
            all_predictions.extend(batch_predictions)
            all_logits.extend(batch_logits)
            all_targets.extend(batch["label"])
            total_samples += batch_size_actual

            if on_progress:
                on_progress(total_samples, len(dataset))

        # Convert to numpy arrays for metric computation
        predictions_array = np.array(all_predictions)
        targets_array = np.array(all_targets)
        logits_array = torch.stack(all_logits).cpu().numpy()

        return ClassificationEvaluationResult.calculate_metrics(
            logits_array=logits_array,
            targets_array=targets_array,
            predictions_array=predictions_array,
            total_loss=total_loss,
        )

    @overload
    def predict(
        self,
        value: InputType,
        use_lookup_cache: bool = True,
        expected_label: int | None = None,
    ) -> LabelPredictionWithMemories:
        pass

    @overload
    def predict(
        self,
        value: InputTypeList,
        use_lookup_cache: bool = True,
        expected_label: list[int] | None = None,
    ) -> list[LabelPredictionWithMemories]:
        pass

    @torch.no_grad()
    def predict(
        self,
        value: InputType | InputTypeList,
        use_lookup_cache: bool = True,
        expected_label: int | list[int] | None = None,
    ) -> LabelPredictionWithMemories | list[LabelPredictionWithMemories]:
        """
        Predict the label for a given input

        Args:
            value: The input to predict the label for
            use_lookup_cache: Whether to use the lookup cache

        Returns:
            Either a single prediction or a list of predictions depending on the input type
        """
        timestamp = datetime.now(timezone.utc)
        if expected_label is not None:
            expected_label = expected_label if isinstance(expected_label, list) else [expected_label]

        lookup_res = self.memoryset.lookup(
            [value] if not isinstance(value, list) else value,
            count=self.memory_lookup_count,
            return_type="columns",
            use_cache=use_lookup_cache,
        )
        logits = self.forward(
            input_embeddings=torch.tensor(lookup_res["input_embeddings"]).to(self.device),
            memories_labels=torch.tensor(lookup_res["memories_labels"]).to(self.device),
            memories_embeddings=torch.tensor(lookup_res["memories_embeddings"]).to(self.device),
            memories_weights=torch.tensor(lookup_res["memories_lookup_scores"]).to(self.device),
        ).logits
        label_predictions = torch.argmax(logits, dim=-1)

        results: list[LabelPredictionWithMemories] = []
        for i, prediction in enumerate(label_predictions):
            prediction_id = uuid4()
            predicted_label = int(prediction.item())
            anomaly_score = self.estimate_anomaly_score(lookup_res, i)
            result_memory_lookups = [
                LabelPredictionMemoryLookup(
                    prediction_id=prediction_id,
                    value=lookup_res["memories_values"][i][j],
                    embedding=lookup_res["memories_embeddings"][i][j],
                    label=lookup_res["memories_labels"][i][j],
                    label_name=lookup_res["memories_label_names"][i][j],
                    memory_id=lookup_res["memories_ids"][i][j],
                    memory_version=lookup_res["memories_versions"][i][j],
                    source_id=lookup_res["memories_source_ids"][i][j],
                    metadata=lookup_res["memories_metadata"][i][j],
                    metrics=lookup_res["memories_metrics"][i][j],
                    created_at=lookup_res["memories_created_ats"][i][j],
                    updated_at=lookup_res["memories_updated_ats"][i][j],
                    lookup_score=lookup_res["memories_lookup_scores"][i][j],
                    # does not run for feed forward heads since they use memory_lookup_count = 0
                    attention_weight=cast(Tensor, self.head.last_memories_attention_weights).tolist()[i][j],
                )
                for j in range(self.memory_lookup_count)
            ]
            result = LabelPredictionWithMemories(
                prediction_id=prediction_id,
                label=predicted_label,
                label_name=self.memoryset.get_label_name(predicted_label),
                expected_label=expected_label[i] if expected_label is not None else None,
                expected_label_name=(
                    self.memoryset.get_label_name(expected_label[i]) if expected_label is not None else None
                ),
                confidence=float(logits[i][predicted_label].item()),
                timestamp=timestamp,
                input_value=value[i] if isinstance(value, list) else value,
                input_embedding=lookup_res["input_embeddings"][i],
                logits=logits.to("cpu").numpy()[i],
                memories=result_memory_lookups,
                anomaly_score=anomaly_score,
            )
            results.append(result)

        if not isinstance(value, list):
            return results[0]
        return results


AutoConfig.register("rac-model", RACModelConfig)
AutoModelForSequenceClassification.register(RACModelConfig, RACModel)
AutoModelForImageClassification.register(RACModelConfig, RACModel)
