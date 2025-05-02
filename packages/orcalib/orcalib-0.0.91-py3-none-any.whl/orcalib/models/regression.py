from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Callable, cast, overload

import numpy as np
import torch
from datasets import Dataset
from numpy.typing import NDArray
from pydantic import BaseModel
from sklearn.metrics import (
    explained_variance_score,
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)
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

from ..memoryset import (
    InputType,
    InputTypeList,
    ScoredMemoryLookupColumnResult,
    ScoredMemoryset,
)
from ..torch_layers import MemoryMixtureOfExpertsRegressionHead
from ..utils import OnProgressCallback, parse_dataset
from .base_model import MemoryAugmentedModel
from .prediction_types import ScorePredictionMemoryLookup, ScorePredictionWithMemories


class RegressionEvaluationResult(BaseModel):
    """Evaluation metrics for regression predictions."""

    mse: float
    """Mean squared error of the predictions"""

    rmse: float
    """Root mean squared error of the predictions"""

    mae: float
    """Mean absolute error of the predictions"""

    r2: float
    """R-squared score (coefficient of determination) of the predictions"""

    explained_variance: float
    """Explained variance score of the predictions"""

    loss: float
    """Mean squared error loss of the predictions"""

    def __repr__(self) -> str:
        return f"RegressionEvaluationResult({', '.join([f'{k}={v:.4f}' for k, v in self.__dict__.items() if v is not None])})"


class RARHeadType(str, Enum):
    MMOE = "MMOE"


class RARModelConfig(PretrainedConfig):
    model_type = "rar-model"

    head_type: RARHeadType
    memoryset_uri: str | None
    memoryset: ScoredMemoryset
    memory_lookup_count: int | None
    weigh_memories: bool | None
    min_memory_weight: float | None
    num_layers: int | None
    dropout_prob: float | None

    def __init__(
        self,
        memoryset_uri: str | None = None,
        memory_lookup_count: int | None = None,
        head_type: RARHeadType | str = RARHeadType.MMOE,
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
            memory_lookup_count: Number of memories to lookup for each input, defaults to 10
            head_type: Type of regression head to use
            weigh_memories: Optional parameter for KNN head, whether to weigh memories by their lookup score
            min_memory_weight: Optional parameter for KNN head, minimum memory weight under which memories are ignored
            num_layers: Optional parameter for FF head, number of layers in the feed forward network
            dropout_prob: Optional parameter for FF head, dropout probability
        """
        # We cannot require memoryset_uri here, because this class must be initializable without
        # passing any parameters for the PretrainedConfig.save_pretrained method to work, so instead
        # we throw an error in the RetrievalAugmentedRegressor initializer if it is missing
        self.memoryset_uri = memoryset_uri
        self.memory_lookup_count = memory_lookup_count
        self.head_type = head_type if isinstance(head_type, RARHeadType) else RARHeadType(head_type)
        self.weigh_memories = weigh_memories
        self.min_memory_weight = min_memory_weight
        self.num_layers = num_layers
        self.dropout_prob = dropout_prob
        super().__init__(**kwargs)


class RARModel(MemoryAugmentedModel[ScoredMemoryset]):
    """A retrieval augmented regression model that uses a memoryset to make predictions."""

    config_class = RARModelConfig
    base_model_prefix = "rar"
    memory_lookup_count: int

    def _init_head(self):
        match self.config.head_type:
            case RARHeadType.MMOE:
                self.memory_lookup_count = self.config.memory_lookup_count or 10
                self.head = MemoryMixtureOfExpertsRegressionHead(
                    embedding_dim=self.embedding_dim,
                )
            case _:
                raise ValueError(f"Unsupported head type: {self.config.head_type}")

    @overload
    def __init__(self, config: RARModelConfig):
        pass

    @overload
    def __init__(
        self,
        *,
        memoryset: ScoredMemoryset | str,
        memory_lookup_count: int | None = None,
        head_type: RARHeadType | str = RARHeadType.MMOE,
        weigh_memories: bool = False,
        min_memory_weight: float | None = None,
        num_layers: int | None = None,
        dropout_prob: float | None = None,
    ):
        pass

    def __init__(
        self,
        config: RARModelConfig | None = None,
        *,
        memoryset: ScoredMemoryset | str | None = None,
        memory_lookup_count: int | None = None,
        head_type: RARHeadType | str = RARHeadType.MMOE,
        weigh_memories: bool = False,
        min_memory_weight: float | None = None,
        num_layers: int | None = None,
        dropout_prob: float | None = None,
    ):
        if config is None:
            assert memoryset is not None
            if isinstance(memoryset, ScoredMemoryset):
                self.memoryset = memoryset
            else:
                self.memoryset = ScoredMemoryset.connect(memoryset)
            config = RARModelConfig(
                memoryset_uri=self.memoryset.uri,
                memory_lookup_count=memory_lookup_count,
                head_type=head_type,
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
                or weigh_memories is not None
                or min_memory_weight is not None
                or num_layers is not None
                or dropout_prob is not None
            ), "Either config or kwargs can be provided, not both"
            if not config.memoryset_uri:
                # all configs must have defaults in a PretrainedConfig, but this one is required
                raise ValueError("memoryset_uri must be specified in config")
            self.memoryset = ScoredMemoryset.connect(config.memoryset_uri)
        super().__init__(config)
        self.embedding_dim = self.memoryset.embedding_model.embedding_dim
        self._init_head()
        self.criterion = nn.MSELoss()

    @property
    def num_trainable_parameters(self) -> int:
        """Number of trainable parameters in the model"""
        return self.num_parameters(only_trainable=True)

    def reset(self):
        """Reset the model weights to their initial state"""
        self._init_head()

    def attach(self, memoryset: ScoredMemoryset | str):
        """
        Attach a memoryset to the model

        Args:
            memoryset: The memoryset to attach to the model or a URI to a memoryset
        """
        self.memoryset = memoryset if isinstance(memoryset, ScoredMemoryset) else ScoredMemoryset.connect(memoryset)

    def forward(
        self,
        input_embeddings: Tensor | None = None,
        memories_scores: Tensor | None = None,
        memories_embeddings: Tensor | None = None,
        memories_weights: Tensor | None = None,
        labels: Tensor | None = None,
    ) -> SequenceClassifierOutput:
        logits = self.head(input_embeddings, memories_scores, memories_embeddings, memories_weights)
        loss = self.criterion(logits, labels) if labels is not None else None
        return SequenceClassifierOutput(loss=loss, logits=logits)

    def _estimate_confidence(
        self,
        attention_weights: list[float] | NDArray[np.float32],
        memory_scores: list[float] | NDArray[np.float32],
    ) -> float:
        """
        Estimate the confidence of a regression prediction based on attention weights and memory scores.

        The confidence is computed using:
        1. Attention entropy: How focused vs spread out the attention is
        2. Score variance: How much the scores of attended memories vary

        Args:
            attention_weights: The attention weights for each memory
            memory_scores: The scores of each memory

        Returns:
            A confidence score between 0 and 1
        """
        from scipy.stats import entropy

        # Convert to numpy arrays if needed
        attention_weights = np.array(attention_weights, dtype=np.float32)
        memory_scores = np.array(memory_scores, dtype=np.float32)

        # Normalize attention weights to sum to 1
        attention_weights = attention_weights / np.sum(attention_weights)

        # Compute attention entropy (normalized to [0, 1])
        max_entropy = np.log(len(attention_weights))
        attention_entropy = entropy(attention_weights) / max_entropy if max_entropy > 0 else 0
        attention_focus = 1 - attention_entropy  # Higher focus = more confident

        # Compute weighted standard deviation of scores
        weighted_mean = np.sum(attention_weights * memory_scores)
        weighted_var = np.sum(attention_weights * (memory_scores - weighted_mean) ** 2)
        weighted_std = np.sqrt(weighted_var)

        # Scale std to [0, 1] using a soft threshold
        # We use 2 * weighted_mean as a reference - if std is larger than this, confidence goes to 0
        score_consistency = 1 / (1 + (weighted_std / (abs(weighted_mean) + 1e-6)))

        # Combine the two factors with more weight on score consistency
        confidence = 0.3 * attention_focus + 0.7 * score_consistency

        return float(confidence)

    @overload
    def predict(
        self, value: InputType, use_lookup_cache: bool = True, expected_score: float | None = None
    ) -> ScorePredictionWithMemories:
        pass

    @overload
    def predict(
        self, value: InputTypeList, use_lookup_cache: bool = True, expected_score: list[float] | None = None
    ) -> list[ScorePredictionWithMemories]:
        pass

    @torch.no_grad()
    def predict(
        self,
        value: InputType | InputTypeList,
        use_lookup_cache: bool = True,
        expected_score: float | list[float] | None = None,
    ) -> ScorePredictionWithMemories | list[ScorePredictionWithMemories]:
        """
        Predict the score for a given input

        Args:
            value: The input to predict the score for
            use_lookup_cache: Whether to use the lookup cache

        Returns:
            Either a single prediction or a list of predictions depending on the input type
        """
        timestamp = datetime.now(timezone.utc)
        if expected_score is not None:
            expected_score = expected_score if isinstance(expected_score, list) else [expected_score]

        lookup_res = cast(
            "ScoredMemoryLookupColumnResult",
            self.memoryset.lookup(
                [value] if not isinstance(value, list) else value,
                count=self.memory_lookup_count,
                return_type="columns",
                use_cache=use_lookup_cache,
            ),
        )
        logits = self.forward(
            input_embeddings=torch.tensor(lookup_res["input_embeddings"]).to(self.device),
            memories_scores=torch.tensor(lookup_res["memories_scores"]).to(self.device),
            memories_embeddings=torch.tensor(lookup_res["memories_embeddings"]).to(self.device),
            memories_weights=torch.tensor(lookup_res["memories_lookup_scores"]).to(self.device),
        ).logits
        predictions = logits

        results: list[ScorePredictionWithMemories] = []
        for i, prediction in enumerate(predictions):
            assert self.head.last_memories_attention_weights is not None
            prediction_id = uuid4()
            predicted_score = float(prediction.item())
            attention_weights = self.head.last_memories_attention_weights.tolist()[i]
            memory_scores = lookup_res["memories_scores"][i]

            confidence = self._estimate_confidence(attention_weights, memory_scores)
            anomaly_score = self.estimate_anomaly_score(lookup_res, i)

            result_memory_lookups = [
                ScorePredictionMemoryLookup(
                    prediction_id=prediction_id,
                    value=lookup_res["memories_values"][i][j],
                    embedding=lookup_res["memories_embeddings"][i][j],
                    score=lookup_res["memories_scores"][i][j],
                    memory_id=lookup_res["memories_ids"][i][j],
                    memory_version=lookup_res["memories_versions"][i][j],
                    source_id=lookup_res["memories_source_ids"][i][j],
                    metadata=lookup_res["memories_metadata"][i][j],
                    metrics=lookup_res["memories_metrics"][i][j],
                    created_at=lookup_res["memories_created_ats"][i][j],
                    updated_at=lookup_res["memories_updated_ats"][i][j],
                    lookup_score=lookup_res["memories_lookup_scores"][i][j],
                    attention_weight=attention_weights[j],
                )
                for j in range(self.memory_lookup_count)
            ]
            result = ScorePredictionWithMemories(
                prediction_id=prediction_id,
                score=predicted_score,
                confidence=confidence,
                timestamp=timestamp,
                input_value=value[i] if isinstance(value, list) else value,
                input_embedding=lookup_res["input_embeddings"][i],
                expected_score=expected_score[i] if expected_score is not None else None,
                memories=result_memory_lookups,
                anomaly_score=anomaly_score,
            )
            results.append(result)

        if not isinstance(value, list):
            return results[0]
        return results

    def evaluate(
        self,
        dataset: Dataset,
        value_column: str = "value",
        score_column: str = "score",
        batch_size: int = 32,
        on_progress: OnProgressCallback | None = None,
        on_predict: Callable[[list[ScorePredictionWithMemories]], None] | None = None,
    ) -> RegressionEvaluationResult:
        """
        Evaluate the model on a given dataset

        Args:
            dataset: The data to evaluate the model on
            value_column: The column in the dataset that contains the input values
            score_column: The column in the dataset that contains the expected scores
            batch_size: The batch size to use for evaluation
            on_progress: Optional callback to report progress
            on_predict: Optional callback to save telemetry for a batch of predictions

        Returns:
            The evaluation result with regression metrics
        """
        dataset = parse_dataset(dataset, value_column=value_column, score_column=score_column)

        # Track total loss and predictions for computing metrics
        total_loss = 0.0
        all_predictions: list[float] = []
        all_targets: list[float] = []
        total_samples = 0

        # Process dataset in batches
        if on_progress is not None:
            on_progress(0, len(dataset))
        for i in trange(0, len(dataset), batch_size, disable=on_progress is not None):
            batch = dataset[i : i + batch_size]
            batch_size_actual = len(batch["value"])

            # Get predictions for batch
            predictions = self.predict(batch["value"], use_lookup_cache=True, expected_score=batch["score"])
            if not isinstance(predictions, list):
                predictions = [predictions]

            # Extract scores and targets
            batch_predictions = [p.score for p in predictions]
            batch_targets = batch["score"]

            # Compute loss for batch
            batch_loss = self.criterion(
                torch.tensor(batch_predictions, device=self.device),
                torch.tensor(batch_targets, device=self.device),
            ).item()

            # Accumulate results
            total_loss += batch_loss * batch_size_actual
            all_predictions.extend(batch_predictions)
            all_targets.extend(batch_targets)
            total_samples += batch_size_actual

            if on_progress:
                on_progress(total_samples, len(dataset))

            if on_predict:
                on_predict(predictions)

        # Convert to numpy arrays for metric computation
        predictions_array = np.array(all_predictions)
        targets_array = np.array(all_targets)

        # Compute MSE and RMSE
        mse = float(mean_squared_error(targets_array, predictions_array))
        rmse = float(np.sqrt(mse))

        # Compute other metrics
        mae = float(mean_absolute_error(targets_array, predictions_array))
        r2 = float(r2_score(targets_array, predictions_array))
        explained_var = float(explained_variance_score(targets_array, predictions_array))

        return RegressionEvaluationResult(
            mse=mse,
            rmse=rmse,
            mae=mae,
            r2=r2,
            explained_variance=explained_var,
            loss=total_loss / total_samples,
        )


AutoConfig.register("rar-model", RARModelConfig)
AutoModelForSequenceClassification.register(RARModelConfig, RARModel)
AutoModelForImageClassification.register(RARModelConfig, RARModel)
