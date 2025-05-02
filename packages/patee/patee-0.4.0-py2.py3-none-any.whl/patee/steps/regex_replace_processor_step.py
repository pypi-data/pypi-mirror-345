import logging
import re

from patee.core_types import PipelineContext
from patee.step_types import (
    ParallelProcessStep,
    StepResult,
    DocumentContext,
    StepContext,
    DocumentPairContext,
)


logger = logging.getLogger(__name__)


class RegexReplaceStep(ParallelProcessStep):
    def __init__(self, name: str, pipeline_context: PipelineContext, **kwargs):
        super().__init__(name, pipeline_context)

        include_regex = kwargs.get("replacements", None)
        if include_regex is None and not isinstance(include_regex, list):
            raise ValueError("Replacement must be defined and must be a list.")

        self.replacements = []
        for item in include_regex:
            name = item.get("name", None)
            regex = item.get("regex", None)
            replacement = item.get("replacement", None)
            if name is None or not isinstance(name, str):
                raise ValueError(f"Name must be defined and must be a string.")
            if regex is None or not isinstance(regex, str):
                raise ValueError(f"Regex for {name} must be defined and be a string.")
            if replacement is None or not isinstance(replacement, str):
                raise ValueError(f"Replacement for {name} must be defined and be a string.")

            self.replacements.append((re.compile(regex, re.RegexFlag.MULTILINE), replacement))

    @staticmethod
    def step_type() -> str:
        return "regex_replace"

    def _process_document(self, context: StepContext, source: DocumentContext) -> StepResult:
        self._replace_document_blocks(source.text_blocks)
        context = DocumentContext(
            source=source.source,
            text_blocks=source.text_blocks,
            extra={},
        )

        return StepResult(
            context=context,
        )

    def _process_document_pair(self, context: StepContext, source: DocumentPairContext) -> StepResult:
        self._replace_document_blocks(source.document_1.text_blocks)
        self._replace_document_blocks(source.document_2.text_blocks)

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

    def _replace_document_blocks(self, original_blocks: list[str]):
        for idx, block in enumerate(original_blocks):
            for replacement in self.replacements:
                block = replacement[0].sub(replacement[1], block)

            original_blocks[idx] = block
