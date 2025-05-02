import logging

from patee.core_types import PipelineContext
from patee.step_types import (
    ParallelProcessStep,
    StepResult,
    DocumentContext,
    StepContext,
    DocumentPairContext,
)


logger = logging.getLogger(__name__)


class NoopProcessorStep(ParallelProcessStep):
    def __init__(self, name: str, pipeline_context: PipelineContext, **kwargs):
        super().__init__(name, pipeline_context)

    @staticmethod
    def step_type() -> str:
        return "noop"

    def _process_document(self, context: StepContext, source: DocumentContext) -> StepResult:
        context = DocumentContext(
                source=source.source,
                text_blocks=source.text_blocks,
                extra={},
        )

        return StepResult(
            context=context,
        )

    def _process_document_pair(self, context: StepContext, source: DocumentPairContext) -> StepResult:
        context = DocumentPairContext(
            document_1=DocumentContext(
                source=source.document_1.source,
                text_blocks=source.document_1.text_blocks,
                extra={},
            ),
            document_2=DocumentContext(
                source=source.document_2.source,
                text_blocks=source.document_2.text_blocks,
                extra={},
            )
        )
        return StepResult(
            context=context,
        )
