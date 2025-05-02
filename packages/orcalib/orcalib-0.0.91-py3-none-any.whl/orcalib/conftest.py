import sys
from io import StringIO
from tempfile import TemporaryDirectory
from typing import Generator, Literal
from unittest.mock import patch
from uuid import uuid4

import pytest
from datasets import ClassLabel, Dataset, DatasetDict
from pydantic_ai import models
from pydantic_ai.agent import Agent
from pydantic_ai.models.test import TestModel

from .embedding import EmbeddingModel
from .memoryset import LabeledMemoryset, ScoredMemoryset
from .utils import delete_dir, get_fs

# disable LLM calls in tests
models.ALLOW_MODEL_REQUESTS = False


@pytest.fixture()
def mock_llm():
    def mock_get_model(self, *args, **kwargs):
        if self._override_model is not None:
            return self._override_model.value
        return TestModel()

    with patch.object(Agent, "_get_model", new=mock_get_model):
        yield


@pytest.fixture
def stdout_capture() -> Generator[StringIO, None, None]:
    old_stdout = sys.stdout
    new_stdout = StringIO()
    sys.stdout = new_stdout
    yield new_stdout
    sys.stdout = old_stdout


@pytest.fixture
def temp_dir() -> Generator[str, None, None]:
    with TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture(params=["local", "blob"])
def location(request) -> Generator[str, None, None]:
    if request.param == "local":
        with TemporaryDirectory() as temp_dir:
            yield temp_dir
    elif request.param == "blob":
        local_bucket_path = f"local://orcalib-tests/{uuid4().hex[:8]}"
        fs = get_fs(local_bucket_path)
        fs.mkdir(local_bucket_path)
        yield local_bucket_path
        delete_dir(local_bucket_path)


@pytest.fixture(params=["local", "blob", "none"])
def location_or_none(request) -> Generator[str | None, None, None]:
    if request.param == "none":
        yield None
    elif request.param == "local":
        with TemporaryDirectory() as temp_dir:
            yield temp_dir
    elif request.param == "blob":
        local_bucket_path = f"local://orcalib-tests-{uuid4().hex[:8]}"
        fs = get_fs(local_bucket_path)
        fs.mkdir(local_bucket_path)
        yield local_bucket_path
        delete_dir(local_bucket_path)


@pytest.fixture
def label_names() -> list[Literal["positive", "negative"]]:
    return ["positive", "negative"]


@pytest.fixture
def dataset(label_names) -> Dataset:
    return Dataset.from_dict(
        {
            "text": [
                "I'm over the moon with how things turned out!",
                "This is the happiest I've felt in a long time.",
                "My heart feels so full and content.",
                "Everything feels perfect right now, I couldn't ask for more.",
                "I'm just so grateful for all the little things today.",
                "I feel like I'm floating on air after that news!",
                "The sun is shining, and life feels amazing.",
                "I can't stop smiling; everything is just falling into place.",
                "I feel so blessed to have these wonderful people in my life.",
                "This moment is everything I dreamed it would be.",
                "It's like all my dreams are finally coming true.",
                "I couldn't be happier with how things are going.",
                "There's a warmth in my heart that I can't describe.",
                "I feel truly alive and connected to everything around me.",
                "This accomplishment means the world to me.",
                "It's amazing to feel so supported and loved.",
                "I am so fed up with dealing with this over and over.",
                "Why does it always feel like I'm hitting a brick wall?",
                "I'm getting really tired of this never-ending cycle.",
                "It's so frustrating when things just never go my way.",
                "I can't believe I'm still dealing with this nonsense.",
                "Every small setback is just adding to my frustration.",
                "I'm done putting up with these constant roadblocks.",
                "It feels like everything is working against me lately.",
                "I feel trapped by all these obstacles I can't control.",
                "Nothing I do seems to make a difference at this point.",
                "I'm at my wits' end with all of this chaos.",
                "I can't stand how unfair this situation is becoming.",
                "It feels like I'm pouring energy into a black hole.",
                "I'm exhausted from dealing with this repeated hassle.",
                "Why does it feel like every step forward is two steps back?",
                "I'm so frustrated that I can't seem to make progress.",
            ],
            "label": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        }
    ).cast_column("label", ClassLabel(names=label_names))


@pytest.fixture
def dataset_dict(dataset) -> DatasetDict:
    return dataset.train_test_split(test_size=8, seed=42, stratify_by_column="label")


@pytest.fixture
def empty_memoryset() -> LabeledMemoryset:
    return LabeledMemoryset(
        f"memory:#test_{uuid4().hex[:8]}",
        embedding_model=EmbeddingModel.GTE_BASE,
    )


@pytest.fixture
def memoryset(empty_memoryset, dataset_dict) -> LabeledMemoryset:
    empty_memoryset.insert(dataset_dict["train"], value_column="text")
    return empty_memoryset


# TODO: just add a score column to the dataset and use that
@pytest.fixture
def scored_dataset_dict() -> DatasetDict:
    dataset = Dataset.from_dict(
        {
            "text": [
                "I'm over the moon with how things turned out!",
                "This is the happiest I've felt in a long time.",
                "My heart feels so full and content.",
                "Everything feels perfect right now, I couldn't ask for more.",
                "I'm just so grateful for all the little things today.",
                "I feel like I'm floating on air after that news!",
                "The sun is shining, and life feels amazing.",
                "I can't stop smiling; everything is just falling into place.",
                "I feel so blessed to have these wonderful people in my life.",
                "This moment is everything I dreamed it would be.",
                "It's like all my dreams are finally coming true.",
                "I couldn't be happier with how things are going.",
                "There's a warmth in my heart that I can't describe.",
                "I feel truly alive and connected to everything around me.",
                "This accomplishment means the world to me.",
                "It's amazing to feel so supported and loved.",
                "Today has been absolutely incredible!",
                "I'm beaming with joy and excitement.",
                "Everything is falling into place perfectly.",
                "I feel on top of the world right now!",
                "This success is beyond my wildest dreams.",
                "My heart is bursting with happiness.",
                "I'm surrounded by such amazing energy.",
                "This victory feels absolutely incredible.",
                "I'm walking on sunshine today!",
                "Everything just feels right in the world.",
                "I'm filled with such deep gratitude.",
                "This moment is absolutely perfect.",
                "I feel unstoppable and energized.",
                "My spirits are soaring high today.",
                "This achievement is truly remarkable.",
                "I'm radiating with pure happiness.",
                "Life couldn't be more beautiful.",
                "I'm experiencing pure bliss right now.",
                "This day has exceeded all expectations.",
                "I feel completely fulfilled and content.",
                "Everything is aligning perfectly.",
                "I'm overwhelmed with positive emotions.",
                "This success feels absolutely amazing.",
                "I'm floating on cloud nine!",
                "My heart is overflowing with joy.",
                "This moment is absolutely magical.",
                "I feel incredibly blessed and fortunate.",
                "Everything is working out beautifully.",
                "I'm filled with endless optimism.",
                "This achievement is truly special.",
                "I'm beaming with pride and joy.",
                "Life is showing its most beautiful side.",
                "I'm experiencing peak happiness.",
                "This day is absolutely perfect.",
                "I feel completely at peace.",
                "Everything is exactly as it should be.",
                "I'm surrounded by pure positivity.",
                "This success is deeply satisfying.",
                "I'm glowing with happiness.",
                "My heart is full of light.",
            ],
            "score": [
                0.99,
                0.98,
                0.97,
                0.96,
                0.95,
                0.94,
                0.93,
                0.92,
                0.91,
                0.90,
                0.89,
                0.88,
                0.87,
                0.86,
                0.85,
                0.84,
                0.83,
                0.82,
                0.81,
                0.80,
                0.79,
                0.78,
                0.77,
                0.76,
                0.75,
                0.74,
                0.73,
                0.72,
                0.71,
                0.70,
                0.69,
                0.68,
                0.67,
                0.66,
                0.65,
                0.64,
                0.63,
                0.62,
                0.61,
                0.60,
                0.59,
                0.58,
                0.57,
                0.56,
                0.55,
                0.54,
                0.53,
                0.52,
                0.51,
                0.50,
                0.49,
                0.48,
                0.47,
                0.46,
                0.45,
                0.44,
            ],
        }
    )
    return dataset.train_test_split(test_size=8, seed=42)


@pytest.fixture
def empty_scored_memoryset() -> ScoredMemoryset:
    return ScoredMemoryset(
        f"memory:#test_scored_{uuid4().hex[:8]}",
        embedding_model=EmbeddingModel.GTE_BASE,
    )


@pytest.fixture
def scored_memoryset(empty_scored_memoryset, scored_dataset_dict) -> ScoredMemoryset:
    empty_scored_memoryset.insert(scored_dataset_dict["train"], value_column="text", score_column="score")
    return empty_scored_memoryset
