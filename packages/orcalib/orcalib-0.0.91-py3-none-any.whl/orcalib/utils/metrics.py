"""
This module contains metrics for usage with the Hugging Face Trainer.
"""

from typing import Literal, Tuple, TypedDict

import numpy as np
from numpy.typing import NDArray
from scipy.special import softmax
from sklearn.metrics import accuracy_score, auc, f1_score, log_loss
from sklearn.metrics import precision_recall_curve as sklearn_precision_recall_curve
from sklearn.metrics import roc_auc_score
from sklearn.metrics import roc_curve as sklearn_roc_curve
from transformers.trainer_utils import EvalPrediction


class ClassificationMetrics(TypedDict):
    accuracy: float
    f1_score: float
    roc_auc: float | None  # receiver operating characteristic area under the curve (if all classes are present)
    pr_auc: float | None  # precision-recall area under the curve (only for binary classification)
    log_loss: float  # cross-entropy loss for probabilities


def compute_classifier_metrics(eval_pred: EvalPrediction) -> ClassificationMetrics:
    """
    Compute standard metrics for classifier with Hugging Face Trainer.

    Args:
        eval_pred: The predictions containing logits and expected labels as given by the Trainer.

    Returns:
        A dictionary containing the accuracy, f1 score, and ROC AUC score.
    """
    logits, references = eval_pred
    if isinstance(logits, tuple):
        logits = logits[0]
    if not isinstance(logits, np.ndarray):
        raise ValueError("Logits must be a numpy array")
    if not isinstance(references, np.ndarray):
        raise ValueError(
            "Multiple label columns found, use the `label_names` training argument to specify which one to use"
        )

    if not (logits > 0).all():
        # convert logits to probabilities with softmax if necessary
        probabilities = softmax(logits)
    elif not np.allclose(logits.sum(-1, keepdims=True), 1.0):
        # convert logits to probabilities through normalization if necessary
        probabilities = logits / logits.sum(-1, keepdims=True)
    else:
        probabilities = logits

    return classification_scores(references, probabilities)


def classification_scores(
    references: NDArray[np.int64],
    probabilities: NDArray[np.float32],
    average: Literal["micro", "macro", "weighted", "binary"] | None = None,
    multi_class: Literal["ovr", "ovo"] = "ovr",
) -> ClassificationMetrics:
    if probabilities.ndim == 1:
        # convert 1D probabilities (binary) to 2D logits
        probabilities = np.column_stack([1 - probabilities, probabilities])
    elif probabilities.ndim == 2:
        if probabilities.shape[1] < 2:
            raise ValueError("Use a different metric function for regression tasks")
    else:
        raise ValueError("Probabilities must be 1 or 2 dimensional")

    predictions = np.argmax(probabilities, axis=-1)

    num_classes_references = len(set(references))
    num_classes_predictions = len(set(predictions))

    if average is None:
        average = "binary" if num_classes_references == 2 else "weighted"

    accuracy = accuracy_score(references, predictions)
    f1 = f1_score(references, predictions, average=average)
    loss = log_loss(references, probabilities)

    if num_classes_references == num_classes_predictions:
        # special case for binary classification: https://github.com/scikit-learn/scikit-learn/issues/20186
        if num_classes_references == 2:
            roc_auc = roc_auc_score(references, probabilities[:, 1])
            precisions, recalls, _ = calculate_pr_curve(references, probabilities[:, 1])
            pr_auc = auc(recalls, precisions)
        else:
            roc_auc = roc_auc_score(references, probabilities, multi_class=multi_class)
            pr_auc = None
    else:
        roc_auc = None
        pr_auc = None

    return {
        "accuracy": float(accuracy),
        "f1_score": float(f1),
        "roc_auc": float(roc_auc) if roc_auc is not None else None,
        "pr_auc": float(pr_auc) if pr_auc is not None else None,
        "log_loss": float(loss),
    }


def calculate_pr_curve(
    references: NDArray[np.int64],
    probabilities: NDArray[np.float32],
    max_length: int = 100,
) -> Tuple[NDArray[np.float32], NDArray[np.float32], NDArray[np.float32]]:
    if probabilities.ndim == 1:
        probabilities_slice = probabilities
    elif probabilities.ndim == 2:
        probabilities_slice = probabilities[:, 1]
    else:
        raise ValueError("Probabilities must be 1 or 2 dimensional")

    if len(probabilities_slice) != len(references):
        raise ValueError("Probabilities and references must have the same length")

    precisions, recalls, thresholds = sklearn_precision_recall_curve(references, probabilities_slice)

    # Convert all arrays to float32 immediately after getting them
    precisions = precisions.astype(np.float32)
    recalls = recalls.astype(np.float32)
    thresholds = thresholds.astype(np.float32)

    # Concatenate with 0 to include the lowest threshold
    thresholds = np.concatenate(([0], thresholds))

    # Sort by threshold
    sorted_indices = np.argsort(thresholds)
    thresholds = thresholds[sorted_indices]
    precisions = precisions[sorted_indices]
    recalls = recalls[sorted_indices]

    if len(precisions) > max_length:
        new_thresholds = np.linspace(0, 1, max_length, dtype=np.float32)
        new_precisions = np.interp(new_thresholds, thresholds, precisions)
        new_recalls = np.interp(new_thresholds, thresholds, recalls)
        thresholds = new_thresholds
        precisions = new_precisions
        recalls = new_recalls

    return precisions.astype(np.float32), recalls.astype(np.float32), thresholds.astype(np.float32)


def calculate_roc_curve(
    references: NDArray[np.int64],
    probabilities: NDArray[np.float32],
    max_length: int = 100,
) -> Tuple[NDArray[np.float32], NDArray[np.float32], NDArray[np.float32]]:
    if probabilities.ndim == 1:
        probabilities_slice = probabilities
    elif probabilities.ndim == 2:
        probabilities_slice = probabilities[:, 1]
    else:
        raise ValueError("Probabilities must be 1 or 2 dimensional")

    if len(probabilities_slice) != len(references):
        raise ValueError("Probabilities and references must have the same length")

    # Convert probabilities to float32 before calling sklearn_roc_curve
    probabilities_slice = probabilities_slice.astype(np.float32)
    fpr, tpr, thresholds = sklearn_roc_curve(references, probabilities_slice)

    # Convert all arrays to float32 immediately after getting them
    fpr = fpr.astype(np.float32)
    tpr = tpr.astype(np.float32)
    thresholds = thresholds.astype(np.float32)

    # We set the first threshold to 1.0 instead of inf for reasonable values in interpolation
    thresholds[0] = 1.0

    # Sort by threshold
    sorted_indices = np.argsort(thresholds)
    thresholds = thresholds[sorted_indices]
    fpr = fpr[sorted_indices]
    tpr = tpr[sorted_indices]

    if len(fpr) > max_length:
        new_thresholds = np.linspace(0, 1, max_length, dtype=np.float32)
        new_fpr = np.interp(new_thresholds, thresholds, fpr)
        new_tpr = np.interp(new_thresholds, thresholds, tpr)
        thresholds = new_thresholds
        fpr = new_fpr
        tpr = new_tpr

    return fpr.astype(np.float32), tpr.astype(np.float32), thresholds.astype(np.float32)
