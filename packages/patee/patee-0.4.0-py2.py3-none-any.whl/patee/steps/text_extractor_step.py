import logging

from patee.core_types import PipelineContext
from patee.input_types import MonolingualSingleFile, MonolingualSingleFilePair, MultilingualSingleFile
from patee.step_types import (
    ParallelExtractStep,
    StepResult,
    DocumentContext,
    DocumentSource,
    StepContext,
    DocumentPairContext,
)


logger = logging.getLogger(__name__)


class TextReaderExtractor(ParallelExtractStep):
    def __init__(self, name: str, pipeline_context: PipelineContext, **kwargs):
        super().__init__(name, pipeline_context)

    @staticmethod
    def step_type() -> str:
        return "text_extractor"

    def _extract_monolingual_single_file(self, context: StepContext, source: MonolingualSingleFile) -> StepResult:
        logger.debug("reading document from %s ...", source.document_path)
        document_text = source.document_path.read_text(encoding="utf-8")

        context = DocumentContext(
            source=DocumentSource.from_monolingual_file(source),
            text_blocks=[document_text],
            extra={}
        )

        result = StepResult(
            context=context,
        )

        logger.debug("monolingual single file read successfully.")

        return result

    def _extract_monolingual_single_file_pair(self, context: StepContext,
                                              source: MonolingualSingleFilePair) -> StepResult:
        logger.debug("reading document 1 from %s ...", source.document_1.document_path)
        document_1_text = source.document_1.document_path.read_text(encoding="utf-8")

        logger.debug("reading document 2 from %s ...", source.document_2.document_path)
        document_2_text = source.document_2.document_path.read_text(encoding="utf-8")

        context = DocumentPairContext(
            document_1=DocumentContext(
                source=DocumentSource.from_monolingual_file(source.document_1),
                text_blocks=[document_1_text],
                extra={}
            ),
            document_2=DocumentContext(
                source=DocumentSource.from_monolingual_file(source.document_2),
                text_blocks=[document_2_text],
                extra={}
            ),
        )
        result = StepResult(
            context=context,
        )

        logger.debug("monolingual single file pairs read successfully.")

        return result

    def _extract_multilingual_single_file(self, context: StepContext, source: MultilingualSingleFile) -> StepResult:
        raise NotImplementedError("Multilingual single file extraction is not implemented yet.")
