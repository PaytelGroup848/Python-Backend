from typing import Any

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)

from app.modules.pipeline_runtime.models.pipeline_run import (
    PipelineRun,
)

from app.modules.pipeline_runtime.models.pipeline_step_run import (
    PipelineStepRun,
)

from app.modules.data_pipelines.models.data_pipeline import (
    DataPipeline,
)

from app.modules.data_pipelines.models.data_pipeline_step import (
    DataPipelineStep,
)

from app.modules.datasets.models.dataset import (
    Dataset,
)

from app.modules.corpora.models.corpus_source import (
    CorpusSource,
)


class PipelineExecutionContext(
    BaseModel,
):

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
    )

    pipeline: DataPipeline

    pipeline_step: DataPipelineStep

    pipeline_run: PipelineRun

    pipeline_step_run: PipelineStepRun

    dataset: Dataset | None = None

    corpus_source: CorpusSource | None = None

    inputs: list[
        dict[
            str,
            Any,
        ]
    ] = Field(
        default_factory=list,
    )

    execution_metadata: dict[
        str,
        Any,
    ] = Field(
        default_factory=dict,
    )