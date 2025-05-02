import logging
from pathlib import Path

from patee.core_types import PipelineContext
from patee.step_types import (
    ParallelProcessStep,
    StepResult,
    StepContext,
    DocumentContext,
    DocumentPairContext,
)

logger = logging.getLogger(__name__)


class TextWriterProcessorStep(ParallelProcessStep):
    def __init__(self, name: str, pipeline_context: PipelineContext, **kwargs):
        super().__init__(name, pipeline_context)

        # Mandatory configuration
        output_path = kwargs.get("output_path")
        if output_path is None:
            output_path = self._pipeline_context.execution_path

        provided_output_path = Path(output_path)
        if not provided_output_path.is_absolute():
            self._output_path = self._pipeline_context.execution_path / provided_output_path
        else:
            self._output_path = provided_output_path

        if not self._output_path.exists():
            raise ValueError(f"output_path does not exist: {self._output_path}")

        if not self._output_path.is_dir():
            raise ValueError(f"output_path must be a directory: {self._output_path}")

        # Safe defaults
        self._block_separator = kwargs.get("block_separator")
        if self._block_separator is None:
            self._block_separator = "\n"

        self._encoding = kwargs.get("encoding")
        if self._encoding is None:
            self._encoding = "utf-8"


    @staticmethod
    def step_type() -> str:
        return "write_to_file"

    def _process_document(self, context: StepContext, source: DocumentContext) -> StepResult:
        document_path = self._output_path / f"{source.source.document_path.stem}.txt"

        document_path.write_text(
            data=self._block_separator.join(source.text_blocks),
            encoding=self._encoding,
        )

        logger.debug(f"Document written to {document_path}")

        return StepResult(
            context=source,
        )

    def _process_document_pair(self, context: StepContext, source: DocumentPairContext) -> StepResult:
        document_1_path = self._output_path / f"{source.document_1.source.document_path.stem}.txt"
        document_2_path = self._output_path / f"{source.document_2.source.document_path.stem}.txt"

        document_1_path.write_text(
            data=self._block_separator.join(source.document_1.text_blocks),
            encoding=self._encoding,
        )
        logger.debug(f"Document 1 written to {document_1_path}")

        document_2_path.write_text(
            data=self._block_separator.join(source.document_2.text_blocks),
            encoding=self._encoding,
        )
        logger.debug(f"Document 2 written to {document_2_path}")

        return StepResult(
            context=source,
        )
