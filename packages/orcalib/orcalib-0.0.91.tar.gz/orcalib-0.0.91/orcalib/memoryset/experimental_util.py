from __future__ import annotations

import logging
from typing import Counter, cast

import numpy as np
import plotly.express as px
from datasets import Dataset
from tqdm.auto import tqdm

from ..utils.dataset import parse_dataset
from .experimental_memory_analysis import (
    calculate_interiority,
    calculate_isolation,
    calculate_support,
)
from .memoryset import LabeledMemoryset


def analyze_memoryset(
    memoryset: LabeledMemoryset,
    interiority_radius: float = 0.5,
    support_radius: float = 0.5,
    isolation_num_neighbors: int = 20,
) -> dict:
    """
    Analyze the memoryset and return a dictionary of metrics.

    Parameters:
    - memoryset (LabeledMemoryset): The memory set to analyze

    Returns:
    - dict: A dictionary of metrics including:
        - memory_count: Total number of memories in the memoryset
        - unique_label_count: Number of unique labels in the memoryset
        - label_counts: Dictionary of label counts
        - scores: Dictionary of interiority, isolation, and support scores
        - avg_interiority: Average interiority score across all memories
        - avg_isolation: Average isolation score across all memories
        - avg_support: Average support score across all memories
        - quantile_interiority: 25th, 50th, and 75th percentile of interiority scores
        - quantile_isolation: 25th, 50th, and 75th percentile of isolation scores
        - quantile_support: 25th, 50th, and 75th percentile of support scores
        - memory_data: List of dict (1 per memory): text, label, interiority, isolation, and support scores
    """
    memories = memoryset.to_list()

    memory_data = []
    scores = []
    label_counts = {}
    for memory in tqdm(memoryset, desc="Analyzing memoryset", unit=" memories", leave=True):  # type: ignore
        interiority = calculate_interiority(memory.embedding, radius=interiority_radius, memories=memories)
        isolation = calculate_isolation(memory.embedding, memories=memories, num_neighbors=isolation_num_neighbors)
        support = calculate_support(memory.embedding, memory.label, radius=support_radius, memories=memories)
        scores.append(
            [
                interiority,
                isolation,
                support,
            ]
        )
        label = memory.label
        if label not in label_counts:
            label_counts[label] = 0
        label_counts[label] += 1
        memory_data.append(
            {
                "text": memory.value,
                "label": memory.label,
                "interiority": interiority,
                "isolation": isolation,
                "support": support,
            }
        )

    # Unpack the results
    interiority_scores, isolation_scores, support_scores = zip(*scores)

    avg_interiority = np.mean(interiority_scores)
    avg_isolation = np.mean(isolation_scores)
    avg_support = np.mean(support_scores)
    quantile_interiority = np.quantile(interiority_scores, [0.25, 0.5, 0.75])
    quantile_isolation = np.quantile(isolation_scores, [0.25, 0.5, 0.75])
    quantile_support = np.quantile(support_scores, [0.25, 0.5, 0.75])

    return {
        "memory_count": len(memoryset),
        "unique_label_count": len(label_counts),
        "label_counts": label_counts,
        "avg_isolation": avg_isolation,
        "avg_interiority": avg_interiority,
        "avg_support": avg_support,
        "scores": {
            "interiority": interiority_scores,
            "isolation": isolation_scores,
            "support": support_scores,
        },
        "quantile_isolation": quantile_isolation,
        "quantile_interiority": quantile_interiority,
        "quantile_support": quantile_support,
        "memory_data": memory_data,
    }


def insert_useful_memories(
    memoryset: LabeledMemoryset,
    dataset: Dataset,
    lookup_count: int = 15,
    batch_size: int = 32,
    value_column: str = "value",
    label_column: str = "label",
    source_id_column: str | None = None,
    other_columns_as_metadata: bool = True,
    compute_embeddings: bool = True,
    min_confidence: float = 0.85,
) -> int:
    """
    Inserts useful memories into a memoryset by evaluating their impact on prediction accuracy.

    This function iterates through a dataset and selectively adds rows to the memoryset if doing so
    improves the model's accuracy. It ensures that the memoryset has enough initial memories for
    lookup operations and uses a confidence threshold to determine whether a memory is useful.

    Args:
        memoryset: The memoryset to which useful memories will be added.
        dataset: Data to insert into the memoryset.
        lookup_count: The number of nearest neighbors to retrieve during memory lookup. Defaults to 15.
        batch_size: The batch size for memory insertion operations. Defaults to 32.
        value_column: The column name in the dataset containing memory values. Defaults to "value".
        label_column: The column name in the dataset containing memory labels. Defaults to "label".
        source_id_column: The column name in the dataset containing source IDs, or None if not applicable. Defaults to None.
        other_columns_as_metadata: Whether to treat other columns in the dataset as metadata. Defaults to True.
        compute_embeddings: Whether to compute embeddings for the inserted memories. Defaults to True.
        min_confidence: The minimum confidence threshold for a memory to be considered useful. Defaults to 0.85.

    Returns:
        The number of memories successfully inserted into the memoryset.

    Notes:
        - This method currently supports only text-based memories.
        - It is experimental and subject to change in future versions.
    """
    insert_count = 0  # The number of rows we've actually inserted
    total_data_count = len(dataset)
    assert total_data_count > 0, "No data provided"

    # Parse the dataset
    dataset = parse_dataset(
        dataset,
        value_column=value_column,
        label_column=label_column,
        source_id_column=source_id_column,
        other_columns_as_metadata=other_columns_as_metadata,
    )

    # We need at least lookup_count memories in the memoryset in order to do any predictions.
    # If we don't have enough memories we'll add lookup_count elements to the memoryset.
    missing_mem_count = max(0, lookup_count - len(memoryset))
    if missing_mem_count:
        if len(dataset) <= missing_mem_count:
            logging.info(
                f"Memoryset needs a minimum of {missing_mem_count} memories for lookup, but only contains {len(memoryset)}."
                f"{total_data_count}. Adding all {total_data_count} instances to the memoryset."
            )
            memoryset.insert(
                dataset,
                batch_size=batch_size,
                compute_embeddings=compute_embeddings,
                show_progress_bar=False,
            )
            return total_data_count

        logging.info(f"Adding {missing_mem_count} memories to reach minimum required count: {lookup_count}")

        memoryset.insert(
            dataset.select(range(missing_mem_count)),
            batch_size=batch_size,
            compute_embeddings=compute_embeddings,
            show_progress_bar=False,
        )
        insert_count = missing_mem_count
        dataset = dataset.select(range(missing_mem_count, len(dataset)))

    assert len(dataset) > 0, "No data left to add to memoryset. This shouldn't be possible!"

    # Now we can start predicting and adding only the useful memories
    for row in tqdm(dataset, total=total_data_count - missing_mem_count):
        row = cast(dict, row)
        lookups = memoryset.lookup(row["value"], count=lookup_count)
        counter = Counter([memory.label for memory in lookups])
        # get the count for row["label"] if it exists in the counter, otherwise default to 0
        confidence = counter[row["value"]] / lookup_count if lookup_count > 0 else 0
        if confidence < min_confidence:
            memoryset.insert(
                [row],
                compute_embeddings=compute_embeddings,
                show_progress_bar=False,
                other_columns_as_metadata=other_columns_as_metadata,
            )
            insert_count += 1

    return insert_count


def visualize_memoryset(
    analysis_result_a: dict, a_label: str | None, analysis_result_b: dict | None = None, b_label: str | None = None
):
    """
    Visualize the analysis results of one or two memorysets.

    Parameters:
    - analysis_result_a (dict): The analysis result of the first memoryset
    - a_label (str | None): The label for the first memoryset
    - analysis_result_b (dict | None): The analysis result of the second memoryset
    - b_label (str | None): The label for the second memoryset

    Returns:
        - None

    Note:
    - The analysis result should be the dictionary returned by the analyze_memoryset function.
    - If only one memoryset is provided, the function will create a box and whisker plot.
    - If two memorysets are provided, the function will create a grouped box and whisker plot.
    """

    if analysis_result_b is not None:
        # Prepare data for the 2 memoryset view
        a_label = "A" if a_label is None else a_label
        b_label = "B" if b_label is None else b_label
        a_len = len(analysis_result_a["scores"]["interiority"])
        b_len = len(analysis_result_b["scores"]["interiority"])
        data = {
            "Scores": analysis_result_a["scores"]["interiority"]
            + analysis_result_b["scores"]["interiority"]
            + analysis_result_a["scores"]["isolation"]
            + analysis_result_b["scores"]["isolation"]
            + analysis_result_a["scores"]["support"]
            + analysis_result_b["scores"]["support"],
            "Category": (
                ["Interiority"] * a_len
                + ["Interiority"] * b_len
                + ["Isolation"] * a_len
                + ["Isolation"] * b_len
                + ["Support"] * a_len
                + ["Support"] * b_len
            ),
            "Memoryset": (
                [a_label] * a_len
                + [b_label] * b_len
                + [a_label] * a_len
                + [b_label] * b_len
                + [a_label] * a_len
                + [b_label] * b_len
            ),
        }
    else:
        # Prepare data for single box and whisker plot
        data = {
            "Scores": analysis_result_a["scores"]["interiority"]
            + analysis_result_a["scores"]["isolation"]
            + analysis_result_a["scores"]["support"],
            "Category": (
                ["Interiority"] * len(analysis_result_a["scores"]["interiority"])
                + ["Isolation"] * len(analysis_result_a["scores"]["isolation"])
                + ["Support"] * len(analysis_result_a["scores"]["support"])
            ),
            "Memoryset": (
                [a_label] * len(analysis_result_a["scores"]["interiority"])
                + [a_label] * len(analysis_result_a["scores"]["isolation"])
                + [a_label] * len(analysis_result_a["scores"]["support"])
            ),
        }

    # Create box and whisker plot
    if a_label != "A" and b_label != "B" and b_label is not None:
        title = f"Memoryset Analysis Results: {a_label} vs {b_label}"
    else:
        title = "Memoryset Analysis Results"
    fig = px.box(data_frame=data, x="Category", y="Scores", color="Memoryset", title=title)
    fig.update_yaxes(title_text="Scores")
    fig.show()
