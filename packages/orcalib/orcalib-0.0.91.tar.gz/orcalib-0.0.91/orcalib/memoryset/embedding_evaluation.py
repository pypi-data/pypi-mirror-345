# TODO: decouple this from memoryset and move it to embeddings submodule

import logging
from datetime import datetime

from datasets import Dataset
from pydantic import BaseModel
from tqdm.auto import tqdm

from ..embedding import EmbeddingModel, PretrainedEmbeddingModelName
from ..utils import OnProgressCallback, remove_duplicates, safely_call_on_progress
from .memoryset import LabeledMemoryset
from .memoryset_analyzer import AnalyzeNeighborLabelsResult, LabeledMemorysetAnalyzer


class EmbeddingEvaluationResult(BaseModel):
    class EmbeddingModelResult(BaseModel):
        embedding_model_name: str
        """The name of the embedding model"""
        embedding_model_path: str
        """The path of the embedding model"""
        analysis_result: AnalyzeNeighborLabelsResult
        """The analysis result for the embedding model"""
        memoryset_name: str | None = None
        """The name of the memoryset"""

    evaluation_results: list[EmbeddingModelResult] = []
    """The evaluation results for each embedding model"""

    def sort_by_neighbor_prediction_accuracy(self) -> None:
        """Sort the evaluation results by neighbor prediction accuracy"""
        self.evaluation_results.sort(key=lambda x: x.analysis_result.neighbor_prediction_accuracy, reverse=True)


class EmbeddingEvaluation:
    DEFAULT_EMBEDDING_MODELS = [PretrainedEmbeddingModelName.GTE_BASE, PretrainedEmbeddingModelName.CDE_SMALL]

    @staticmethod
    def run(
        dataset: Dataset,
        *,
        run_name: str | None,
        value_column: str = "value",
        label_column: str = "label",
        source_id_column: str | None = None,
        neighbor_count: int = 5,
        drop_memorysets: bool = True,
        show_progress_bar: bool = True,
        on_progress: OnProgressCallback | None = None,
        label_names: list[str] | None = None,
        embedding_models: list[PretrainedEmbeddingModelName] = DEFAULT_EMBEDDING_MODELS,
    ) -> EmbeddingEvaluationResult:
        if run_name is None:
            run_name = f"embedding_evaluation_{datetime.now().strftime('%Y_%m_%d_%H_%M_%S')}"

        analysis_results = {}
        memoryset_names = {}

        step = 0
        n = len(embedding_models) * 4 + 1

        safely_call_on_progress(on_progress, step, n)
        step += 1

        if value_column not in dataset.column_names:
            raise ValueError(f"Value column {value_column} not found in dataset")
        if label_column not in dataset.column_names:
            raise ValueError(f"Label column {label_column} not found in dataset")
        if source_id_column and source_id_column not in dataset.column_names:
            raise ValueError(f"Source ID column {source_id_column} not found in dataset")

        logging.info("Removing duplicates from dataset...")
        dataset = remove_duplicates(dataset, value_column)

        for embedding_model in tqdm(embedding_models, disable=not show_progress_bar):
            safely_call_on_progress(on_progress, step, n)
            step += 1

            memoryset_name = f"{run_name}_{embedding_model.value}"

            LabeledMemoryset.drop(memoryset_name)

            logging.info(f"Creating memoryset {memoryset_name}...")

            memoryset = LabeledMemoryset(
                memoryset_name, embedding_model=EmbeddingModel(embedding_model.path), label_names=label_names
            )
            memoryset.insert(
                dataset, value_column=value_column, label_column=label_column, source_id_column=source_id_column
            )

            safely_call_on_progress(on_progress, step, n)
            step += 1

            analyzer = LabeledMemorysetAnalyzer(memoryset, neighbor_count=neighbor_count)

            if len(memoryset) == 0:
                raise ValueError(
                    f"Cannot run embedding selection for {embedding_model.value} because the memoryset is empty"
                )

            logging.info(f"Analyzing neighbor labels for {embedding_model.value}...")
            analysis_result = analyzer.analyze_neighbor_labels()
            analysis_results[embedding_model.name] = analysis_result

            safely_call_on_progress(on_progress, step, n)
            step += 1

            if drop_memorysets:
                logging.info(f"Dropping memoryset {memoryset_name}...")
                LabeledMemoryset.drop(memoryset_name)
            else:
                memoryset_names[embedding_model.value] = memoryset_name

            safely_call_on_progress(on_progress, step, n)
            step += 1

        safely_call_on_progress(on_progress, n, n)

        evaluation_results = EmbeddingEvaluationResult(
            evaluation_results=[
                EmbeddingEvaluationResult.EmbeddingModelResult(
                    embedding_model_name=embedding_model.value,
                    embedding_model_path=embedding_model.path,
                    analysis_result=analysis_results[embedding_model.value],
                    memoryset_name=memoryset_names.get(embedding_model.value, None),
                )
                for embedding_model in embedding_models
            ]
        )

        evaluation_results.sort_by_neighbor_prediction_accuracy()
        return evaluation_results
