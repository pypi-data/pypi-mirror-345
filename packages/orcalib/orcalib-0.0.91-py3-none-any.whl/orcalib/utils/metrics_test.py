from typing import Literal

import numpy as np
import pytest

from .metrics import (
    EvalPrediction,
    calculate_pr_curve,
    calculate_roc_curve,
    classification_scores,
    compute_classifier_metrics,
    softmax,
)


def test_binary_metrics():
    y_true = np.array([0, 1, 1, 0, 1])
    y_score = np.array([0.1, 0.9, 0.8, 0.3, 0.2])

    metrics = classification_scores(y_true, y_score)

    assert metrics["accuracy"] == 0.8
    assert metrics["f1_score"] == 0.8
    assert metrics["roc_auc"] is not None
    assert metrics["roc_auc"] > 0.8
    assert metrics["roc_auc"] < 1.0
    assert metrics["pr_auc"] is not None
    assert metrics["pr_auc"] > 0.8
    assert metrics["pr_auc"] < 1.0
    assert metrics["log_loss"] is not None
    assert metrics["log_loss"] > 0.0


def test_multiclass_metrics_with_2_classes():
    y_true = np.array([0, 1, 1, 0, 1])
    y_score = np.array([[0.9, 0.1], [0.1, 0.9], [0.2, 0.8], [0.7, 0.3], [0.8, 0.2]])

    metrics = classification_scores(y_true, y_score)

    assert metrics["accuracy"] == 0.8
    assert metrics["f1_score"] == 0.8
    assert metrics["roc_auc"] is not None
    assert metrics["roc_auc"] > 0.8
    assert metrics["roc_auc"] < 1.0
    assert metrics["pr_auc"] is not None
    assert metrics["pr_auc"] > 0.8
    assert metrics["pr_auc"] < 1.0
    assert metrics["log_loss"] is not None
    assert metrics["log_loss"] > 0.0


@pytest.mark.parametrize(
    "average, multiclass",
    [("micro", "ovr"), ("macro", "ovr"), ("weighted", "ovr"), ("micro", "ovo"), ("macro", "ovo"), ("weighted", "ovo")],
)
def test_multiclass_metrics_with_3_classes(
    average: Literal["micro", "macro", "weighted"], multiclass: Literal["ovr", "ovo"]
):
    y_true = np.array([0, 1, 1, 0, 2])
    y_score = np.array([[0.9, 0.1, 0.0], [0.1, 0.9, 0.0], [0.2, 0.8, 0.0], [0.7, 0.3, 0.0], [0.0, 0.0, 1.0]])

    metrics = classification_scores(y_true, y_score, average=average, multi_class=multiclass)

    assert metrics["accuracy"] == 1.0
    assert metrics["f1_score"] == 1.0
    assert metrics["roc_auc"] is not None
    assert metrics["roc_auc"] > 0.8
    assert metrics["pr_auc"] is None
    assert metrics["log_loss"] is not None
    assert metrics["log_loss"] > 0.0


def test_does_not_modify_logits_unless_necessary():
    logits = np.array([[0.1, 0.9], [0.2, 0.8], [0.7, 0.3], [0.8, 0.2]])
    references = np.array([0, 1, 0, 1])
    metrics = compute_classifier_metrics(EvalPrediction(logits, references))
    assert metrics["log_loss"] == classification_scores(references, logits)["log_loss"]


def test_normalizes_logits_if_necessary():
    logits = np.array([[1.2, 3.9], [1.2, 5.8], [1.2, 2.7], [1.2, 1.3]])
    references = np.array([0, 1, 0, 1])
    metrics = compute_classifier_metrics(EvalPrediction(logits, references))
    assert (
        metrics["log_loss"] == classification_scores(references, logits / logits.sum(axis=1, keepdims=True))["log_loss"]
    )


def test_softmaxes_logits_if_necessary():
    logits = np.array([[-1.2, 3.9], [1.2, -5.8], [1.2, 2.7], [1.2, 1.3]])
    references = np.array([0, 1, 0, 1])
    metrics = compute_classifier_metrics(EvalPrediction(logits, references))
    assert metrics["log_loss"] == classification_scores(references, softmax(logits))["log_loss"]


def test_precision_recall_curve():
    y_true = np.array([0, 1, 1, 0, 1])
    y_score = np.array([0.1, 0.9, 0.8, 0.6, 0.2])

    precision, recall, thresholds = calculate_pr_curve(y_true, y_score)
    assert precision is not None
    assert recall is not None
    assert thresholds is not None

    assert len(precision) == len(recall) == len(thresholds) == 6
    assert precision[0] == 0.6
    assert recall[0] == 1.0
    assert precision[-1] == 1.0
    assert recall[-1] == 0.0

    # test that thresholds are sorted
    assert np.all(np.diff(thresholds) >= 0)


def test_roc_curve():
    y_true = np.array([0, 1, 1, 0, 1])
    y_score = np.array([0.1, 0.9, 0.8, 0.6, 0.2])

    fpr, tpr, thresholds = calculate_roc_curve(y_true, y_score)
    assert fpr is not None
    assert tpr is not None
    assert thresholds is not None

    assert len(fpr) == len(tpr) == len(thresholds) == 6
    assert fpr[0] == 1.0
    assert tpr[0] == 1.0
    assert fpr[-1] == 0.0
    assert tpr[-1] == 0.0

    # test that thresholds are sorted
    assert np.all(np.diff(thresholds) >= 0)


def test_precision_recall_curve_max_length():
    y_true = np.array([0, 1, 1, 0, 1])
    y_score = np.array([0.1, 0.9, 0.8, 0.6, 0.2])

    precision, recall, thresholds = calculate_pr_curve(y_true, y_score, max_length=5)
    assert len(precision) == len(recall) == len(thresholds) == 5

    assert precision[0] == 0.6
    assert recall[0] == 1.0
    assert precision[-1] == 1.0
    assert recall[-1] == 0.0

    # test that thresholds are sorted
    assert np.all(np.diff(thresholds) >= 0)


def test_roc_curve_max_length():
    y_true = np.array([0, 1, 1, 0, 1])
    y_score = np.array([0.1, 0.9, 0.8, 0.6, 0.2])

    fpr, tpr, thresholds = calculate_roc_curve(y_true, y_score, max_length=5)
    assert len(fpr) == len(tpr) == len(thresholds) == 5
    assert fpr[0] == 1.0
    assert tpr[0] == 1.0
    assert fpr[-1] == 0.0
    assert tpr[-1] == 0.0

    # test that thresholds are sorted
    assert np.all(np.diff(thresholds) >= 0)
