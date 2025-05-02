import pytest
from datasets import Dataset

from .embedding_evaluation import EmbeddingEvaluation


@pytest.fixture()
def test_datasource():
    list_data = [
        {"text": "This sentence is about cats", "label": 1},
        {"text": "This sentence is about dogs", "label": 2},
        {"text": "This sentence is about cats", "label": 1},
        {"text": "This sentence is about dogs", "label": 2},
        {"text": 'This is another sentence about "cats"', "label": 1},
        {"text": 'This is another sentence about "dogs"', "label": 2},
        {"text": "This is yet another sentence about 'cats'", "label": 1},
        {"text": "This is yet another sentence about 'dogs'", "label": 2},
    ]

    return Dataset.from_list(list_data)


def test_embedding_evaluation(test_datasource):
    result = EmbeddingEvaluation.run(
        dataset=test_datasource,
        run_name="memory:#test_embedding_evaluation",
        label_names=["empty", "cats", "dogs"],
        value_column="text",
        label_column="label",
        neighbor_count=3,
    )
    assert result is not None

    assert result.evaluation_results is not None
    assert len(result.evaluation_results) == 2

    assert result.evaluation_results[0].embedding_model_name == "GTE_BASE"
    assert result.evaluation_results[0].embedding_model_path == "OrcaDB/gte-base-en-v1.5"

    assert result.evaluation_results[1].embedding_model_name == "CDE_SMALL"
    assert result.evaluation_results[1].embedding_model_path == "OrcaDB/cde-small-v1"

    for i in range(len(result.evaluation_results)):
        assert result.evaluation_results[i].analysis_result.neighbor_prediction_accuracy >= 0.0
        assert result.evaluation_results[i].analysis_result.mean_neighbor_label_confidence >= 0.0
        assert result.evaluation_results[i].analysis_result.mean_neighbor_label_entropy >= 0.0
        assert result.evaluation_results[i].analysis_result.mean_neighbor_predicted_label_ambiguity >= 0.0
