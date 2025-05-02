import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Union

from .core_types import StepContext, PipelineContext
from .input_types import MonolingualSingleFile, MultilingualSingleFile, MonolingualSingleFilePair


TEXT_BLOCK_SEPARATOR = "\n\n---- patee_block_separator ------------------------------- \n\n"


@dataclass(frozen=True)
class DocumentSource:
    document_path: Path
    iso2_language: str

    @staticmethod
    def from_monolingual_file(file: MonolingualSingleFile) -> 'DocumentSource':
        return DocumentSource(file.document_path, file.iso2_language)

    @staticmethod
    def from_multilingual_file(file: MultilingualSingleFile, language_idx: int) -> 'DocumentSource':
        return DocumentSource(file.document_path, file.iso2_languages[language_idx])

    def create_context_executed_step(self, current_dir: Path) -> "DocumentContext":
        return DocumentContext.load_from(self, current_dir)


@dataclass(frozen=True)
class DocumentContext:
    source: DocumentSource
    text_blocks: list[str]
    extra: dict

    def dump_to(self, result_dir: Path):
        file_path = result_dir / f"{self.source.document_path.stem}.txt"
        file_path.write_text(TEXT_BLOCK_SEPARATOR.join(self.text_blocks))

        if len(self.extra) > 0:
            extra_path = result_dir / f"{self.source.document_path.stem}_extra.json"
            extra_path.write_text(json.dumps(self.extra, ensure_ascii=False, indent=2), encoding="utf-8")

    @staticmethod
    def load_from(original_source: "DocumentSource", current_dir: Path) -> "DocumentContext":
        if not current_dir.is_dir():
            raise ValueError(f"out_dit path {current_dir} is not a directory")

        text = (current_dir / f"{original_source.document_path.stem}.txt").read_text()
        extra = {}

        return DocumentContext(original_source, text.split(TEXT_BLOCK_SEPARATOR), extra)


@dataclass(frozen=True)
class DocumentPairContext:
    document_1: DocumentContext
    document_2: DocumentContext

    def dump_to(self, out_dir: Path) -> None:
        if not out_dir.is_dir():
            raise ValueError(f"out_dit path {out_dir} is not a directory")

        self.document_1.dump_to(out_dir)
        self.document_2.dump_to(out_dir)

    @staticmethod
    def read_from(original_context: "DocumentPairContext", current_dir: Path) -> "DocumentPairContext":
        if not current_dir.is_dir():
            raise ValueError(f"out_dit path {current_dir} is not a directory")

        document_1 = DocumentContext.load_from(original_context.document_1.source, current_dir)
        document_2 = DocumentContext.load_from(original_context.document_2.source, current_dir)

        return DocumentPairContext(document_1, document_2)


@dataclass(frozen=True)
class StepResult:
    context: Union[DocumentContext, DocumentPairContext, None]
    should_stop_pipeline: bool = False
    skipped: bool = False

    def __post_init__(self):
        if self.should_stop_pipeline == True and self.context is not None:
            raise ValueError("Cannot stop pipeline and have a context at the same time.")
        if self.should_stop_pipeline == False and self.context is None:
            raise ValueError("Cannot have a context and not stop pipeline at the same time.")


class Step(ABC):
    """Base class for all extraction steps."""

    def __init__(self, name: str, pipeline_context: PipelineContext):
        """Initialize the step."""
        self.name = name
        self._pipeline_context = pipeline_context


class ParallelExtractStep(Step):

    def __init__(self, name: str, pipeline_context: PipelineContext):
        super().__init__(name, pipeline_context)

    def extract(self, context: StepContext,
                source: Union[MonolingualSingleFile, MonolingualSingleFilePair, MultilingualSingleFile]) -> StepResult:
        if source is None:
            raise ValueError("Source cannot be None")
        elif isinstance(source, MonolingualSingleFile):
            return self._extract_monolingual_single_file(context, source)
        elif isinstance(source, MonolingualSingleFilePair):
            return self._extract_monolingual_single_file_pair(context, source)
        elif isinstance(source, MultilingualSingleFile):
            return self._extract_multilingual_single_file(context, source)
        else:
            raise ValueError(f"Unsupported source type: {type(source)}")

    @abstractmethod
    def _extract_monolingual_single_file(self, context: StepContext, source: MonolingualSingleFile) -> StepResult:
        pass

    @abstractmethod
    def _extract_monolingual_single_file_pair(self, context: StepContext, source: MonolingualSingleFilePair) -> StepResult:
        pass

    @abstractmethod
    def _extract_multilingual_single_file(self, context: StepContext, source: MultilingualSingleFile) -> StepResult:
        pass


class ParallelProcessStep(Step):

    def __init__(self, name: str, pipeline_context: PipelineContext):
        super().__init__(name, pipeline_context)

    def process(self, context: StepContext,
                source: Union[DocumentContext, DocumentPairContext]) -> StepResult:
        if source is None:
            raise ValueError("Source cannot be None")
        elif isinstance(source, DocumentContext):
            return self._process_document(context, source)
        elif isinstance(source, DocumentPairContext):
            return self._process_document_pair(context, source)
        else:
            raise ValueError(f"Unsupported source type: {type(source)}")

    @abstractmethod
    def _process_document(self, context: StepContext, source: DocumentContext) -> StepResult:
        pass

    @abstractmethod
    def _process_document_pair(self, context: StepContext, source: DocumentPairContext) -> StepResult:
        pass


@dataclass(frozen=True)
class StepMetadata:
    name: str
    type: str
    idx: int
    config_hash: int

    def __key(self):
        return self.name, self.type, self.idx, self.config_hash

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        if isinstance(other, StepMetadata):
            return self.__key() == other.__key()
        return NotImplemented


class StepsBuilder(ABC):

    @abstractmethod
    def get_supported_step_types(self) -> set[str]:
        pass

    @abstractmethod
    def build(self, step_type: str, step_name: str, pipeline_context: PipelineContext, **kwargs) -> Step:
        pass
