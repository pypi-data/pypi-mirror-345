import logging
from uuid import uuid4
import numpy as np
import pytest
from datasets import load_dataset, Dataset, DatasetDict, ClassLabel
from typing import Generator, cast
from orcalib.concepts.concept_layer import (
    ConceptMap,
    object_to_pickle_str,
    subsample_dataset,
    unpickle_from_str,
)
from orcalib.embedding.embedding_models import EmbeddingModel, PretrainedEmbeddingModelName
from orcalib.memoryset.memoryset import LabeledMemoryset


@pytest.fixture(scope="module")
def ag_news() -> Generator[LabeledMemoryset, None, None]:
    class_names = ["World", "Sports", "Business", "Sci/Tech"]
    dataset = (
        cast(DatasetDict, load_dataset("ag_news"))
        .select_columns(["text", "label"])
        .cast_column("label", ClassLabel(names=class_names))
        .shuffle(seed=42)
    )

    dataset["train"] = subsample_dataset(
        dataset["train"],  # type: ignore
        max_rows=500,  # Limit to 500 rows for testing
        stratify_by_column="label",  # Stratify by label to maintain class distribution
        seed=42,  # Seed for reproducibility
    )

    memoryset = LabeledMemoryset(
        f"memory:#memoryset_test_{uuid4().hex[:8]}",
        embedding_model=EmbeddingModel.GTE_SMALL,
        label_names=class_names,
    )

    memoryset.insert(dataset["train"], value_column="text")

    try:
        yield memoryset
    finally:
        memoryset.drop(memoryset.uri)


@pytest.fixture(scope="module")
def concept_map(ag_news: LabeledMemoryset) -> Generator[ConceptMap, None, None]:
    """
    Fixture to build and provide a ConceptMap for testing.
    """
    concept_map = ConceptMap.build(memoryset=ag_news, max_sample_rows=20_000)
    yield concept_map


def test_concept_map_builder(concept_map: ConceptMap) -> None:
    """
    Test the ConceptMapBuilder with the AG News dataset.
    """
    results = concept_map.predict(
        [
            "Apple releases its new iPhone model",
            "The stock market crashed today",
            "The local football team won their game",
            "NASA announces a new mission to Mars",
            "The economy is recovering after the recession",
        ]
    )

    print(results)
    pass


def test_reduce_dataset() -> None:
    """
    Test the reduce_dataset function to ensure it reduces the dataset correctly.
    """
    dataset = Dataset.from_dict({"text": ["sample"] * 100, "label": [0] * 100}).cast_column(
        "label", ClassLabel(names=["sample"])
    )
    reduced = subsample_dataset(dataset, max_rows=50, stratify_by_column="label", seed=42)
    assert len(reduced) == 50, "Dataset was not reduced to the correct size."


def test_object_to_pickle_str_and_unpickle_from_str() -> None:
    """
    Test the object_to_pickle_str and unpickle_from_str functions for serialization and deserialization.
    """
    original_object = {"key": "value", "number": 42}
    serialized = object_to_pickle_str(original_object)
    deserialized = unpickle_from_str(serialized, dict)
    assert deserialized == original_object, "Deserialized object does not match the original."


def test_concept_map_initialization(concept_map: ConceptMap) -> None:
    """
    Test the initialization of the ConceptMap class.
    """
    assert concept_map.fit_hdbscan is not None, "HDBSCAN model was not initialized."
    assert concept_map.fit_umap is not None, "UMAP model was not initialized."
    assert len(concept_map.cluster_by_id) > 0, "No clusters were identified."


def test_classify_with_soft_clustering(concept_map: ConceptMap) -> None:
    """
    Test the classify_with_soft_clustering method of ConceptMap.
    """
    samples = [
        "Apple releases its new iPhone model",
        "The stock market crashed today",
    ]
    predictions = concept_map.predict(samples)

    assert len(predictions) == len(samples), "Number of predictions does not match number of samples."


def test_is_noise(concept_map: ConceptMap) -> None:
    """
    Test the is_noise method of ConceptMap.
    """
    samples = [
        # Gibberish
        "%$#@$%!#@",
        "asd filjkasndlkcnZC?ZXCV labsdhasd",
        # Random phrases
        "There were shadows where the light forgot to land, and nobody seemed to mind or notice anymore.",
        "Every corner of the morning felt heavier than the night, like waiting for something that never learned how to arrive.",
        "They kept talking about the weather, but it wasn’t really about the weather at all, just a way to fill the quiet.",
        "Moments like these drift past the window, carrying thoughts that never bother to settle anywhere meaningful.",
        "The room smelled faintly of old decisions and unopened letters, lingering like guests who missed their chance to leave.",
        # News articles
        "Apple releases its new iPhone model",
        "The stock market crashed today",
        "The local football team won their game",
        "NASA announces a new mission to Mars",
        "The economy is recovering after the recession",
    ]

    samples = [
        f"Determine the category of the following news article or mark is as noise: {sample}" for sample in samples
    ]
    noise_flags = concept_map.is_noise(samples)
    predictions = concept_map.predict(samples)
    logging.info(f"Noise flags: {noise_flags}")
    logging.info(f"Labels: {[pred.label for pred in predictions]}")
    logging.info(f"Confidence: {[pred.probability for pred in predictions]}")

    # NOTE: Uncomment the following lines to help in debugging
    # class_icons = ["🌎", "🏀", "💰", "🧬"]
    # noise_icon = "🚨"

    # labeled = [ f"{class_icons[p.label]} {sample}" if p.label is not None and p.label != -1 else f"{noise_icon} {sample}" for sample, p in zip(samples, predictions)]
    # logging.info("\n".join(labeled))

    assert len(noise_flags) == len(samples), "Number of noise flags does not match number of samples."
    assert all(isinstance(flag, np.bool) for flag in noise_flags), "Noise flags are not boolean values."
    # TODO: Verify that the noise samples are being flagged as noise. This isn't happening currently.
