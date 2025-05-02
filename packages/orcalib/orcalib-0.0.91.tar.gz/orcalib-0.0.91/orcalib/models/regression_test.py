import os
from datetime import datetime
from uuid import UUID

import numpy as np
import torch

from ..utils import is_using_blob_storage, list_dir
from .prediction_types import ScorePredictionWithMemories
from .regression import (
    MemoryMixtureOfExpertsRegressionHead,
    RARModel,
    RegressionEvaluationResult,
)


def test_initialize_model(scored_memoryset):
    # When a model is initialized with a memoryset
    model = RARModel(memoryset=scored_memoryset, head_type="MMOE")
    # Then the model is initialized without errors
    assert model is not None
    # And the memoryset is attached to the model
    assert model.memoryset is scored_memoryset
    # And it has the correct head
    assert isinstance(model.head, MemoryMixtureOfExpertsRegressionHead)
    # And a reasonable memory lookup count is set
    assert model.memory_lookup_count == 10
    # And the forward method returns a valid output
    batch_size = 2
    memories_scores = torch.tensor([[0.5] * 10, [0.8] * 10])
    assert memories_scores.shape == (batch_size, model.memory_lookup_count)
    input_embeddings = torch.rand(batch_size, model.memoryset.embedding_model.embedding_dim)
    memories_embeddings = torch.rand(
        batch_size, model.memory_lookup_count, model.memoryset.embedding_model.embedding_dim
    )
    expected_scores = torch.tensor([0.6, 0.7])
    assert expected_scores.shape == (batch_size,)
    output = model(
        input_embeddings=input_embeddings,
        memories_scores=memories_scores,
        memories_embeddings=memories_embeddings,
        memories_weights=None,
        labels=expected_scores,
    )
    assert output is not None
    assert output.loss is not None
    assert output.logits is not None
    assert output.logits.shape == (batch_size,)  # Single score output


def test_save_and_load_model(location, scored_memoryset):
    # Given a RAC model
    model = RARModel(memoryset=scored_memoryset, head_type="MMOE")
    # When the model is saved
    model.save_pretrained(location)
    # Then the remote bucket should contain the model files
    if is_using_blob_storage(location):
        model_files = list_dir(location)
        assert len(model_files) > 0
        assert f"{location}/config.json" in model_files
    else:
        model_files = os.listdir(location)
        assert len(model_files) > 0
        assert "config.json" in model_files
    # When the model is loaded back up
    reloaded_model = RARModel.from_pretrained(location)
    # Then the model is loaded without errors
    assert reloaded_model is not None
    # And the memoryset is correctly attached
    assert reloaded_model.memoryset.uri == scored_memoryset.uri
    assert len(reloaded_model.memoryset) == len(scored_memoryset)
    # And the config is loaded correctly
    assert isinstance(reloaded_model.head, MemoryMixtureOfExpertsRegressionHead)


def test_evaluate_model(scored_memoryset, scored_dataset_dict):
    # Given a RAR model
    model = RARModel(memoryset=scored_memoryset, head_type="MMOE")
    # And a progress callback
    progress_calls = []
    progress_callback = lambda step, total: progress_calls.append((step, total))  # noqa: E731
    # When the model is evaluated
    result = model.evaluate(
        scored_dataset_dict["test"].rename_column("score", "label"),
        value_column="text",
        score_column="label",
        on_progress=progress_callback,
        batch_size=len(scored_dataset_dict["test"]) // 2,
    )
    # Then a result is returned
    assert isinstance(result, RegressionEvaluationResult)
    # And the result contains all the metrics
    assert result.mse >= 0  # MSE is always non-negative
    assert result.rmse >= 0  # RMSE is always non-negative
    assert result.mae >= 0  # MAE is always non-negative
    assert isinstance(result.r2, float)  # R2 can be negative for poor fits
    assert isinstance(result.explained_variance, float)
    assert isinstance(result.loss, float)
    # And the progress callback is called
    assert len(progress_calls) == 3
    assert progress_calls[0] == (0, len(scored_dataset_dict["test"]))
    assert progress_calls[1] == (len(scored_dataset_dict["test"]) // 2, len(scored_dataset_dict["test"]))
    assert progress_calls[2] == (len(scored_dataset_dict["test"]), len(scored_dataset_dict["test"]))


def test_predict_model(scored_memoryset, scored_dataset_dict):
    # Given a RAR model
    model = RARModel(memoryset=scored_memoryset)
    # When predict is called with a single text
    prediction = model.predict(scored_dataset_dict["test"]["text"][0])
    # Then a single prediction is returned
    assert prediction is not None
    assert isinstance(prediction, ScorePredictionWithMemories)
    # And the prediction contains a score
    assert isinstance(prediction.score, float)
    # And the prediction contains a confidence
    assert 0 <= prediction.confidence <= 1
    # And the prediction contains an anomaly score
    assert prediction.anomaly_score is not None
    # And the input embedding is a numpy array
    assert isinstance(prediction.input_embedding, np.ndarray)
    assert prediction.input_embedding.shape == (model.memoryset.embedding_model.embedding_dim,)
    assert prediction.input_embedding.dtype == np.float32
    # And a prediction id is returned
    prediction_id = prediction.prediction_id
    assert isinstance(prediction_id, UUID)
    # And a timestamp is returned
    assert isinstance(prediction.timestamp, datetime)
    # And the memory lookups
    assert isinstance(prediction.memories, list)
    assert len(prediction.memories) == model.memory_lookup_count
    # And the memory lookups contain the attention weights
    assert prediction.memories[0].attention_weight is not None
    assert isinstance(prediction.memories[0].attention_weight, float)
    # And the memory lookups contain the prediction id
    assert prediction.memories[0].prediction_id == prediction_id


def test_predict_batch_model(scored_memoryset, scored_dataset_dict):
    # Given a RAR model
    model = RARModel(memoryset=scored_memoryset)
    # When predict is called with a batch of texts
    predictions = model.predict(scored_dataset_dict["test"]["text"][:2])
    # Then a list of predictions is returned
    assert isinstance(predictions, list)
    assert len(predictions) == 2
    # And each prediction is of the correct type
    assert all(isinstance(prediction, ScorePredictionWithMemories) for prediction in predictions)
    # And each prediction has the correct number of memories
    assert all(len(prediction.memories) == model.memory_lookup_count for prediction in predictions)
    # And each prediction has valid scores and confidences
    assert all(isinstance(prediction.score, float) for prediction in predictions)
    assert all(0 <= prediction.confidence <= 1 for prediction in predictions)


def test_confidence_estimation_model(scored_memoryset):
    # Given a RAR model
    model = RARModel(memoryset=scored_memoryset)

    # Test case 1: Focused attention on similar scores
    focused_weights = [0.8, 0.1, 0.1]
    similar_scores = [0.5, 0.51, 0.49]
    high_confidence = model._estimate_confidence(focused_weights, similar_scores)

    # Test case 2: Spread out attention on varied scores
    spread_weights = [0.4, 0.3, 0.3]
    varied_scores = [0.1, 0.5, 0.9]
    low_confidence = model._estimate_confidence(spread_weights, varied_scores)

    # Then the confidence should be higher for focused attention on similar scores
    assert high_confidence > low_confidence
    # And both confidences should be between 0 and 1
    assert 0 <= high_confidence <= 1
    assert 0 <= low_confidence <= 1
