import logging
import sys
from dataclasses import dataclass
from typing import Union, Iterable, Set

from docling.backend.pypdfium2_backend import PyPdfiumDocumentBackend
from docling.datamodel.base_models import InputFormat, ConversionStatus
from docling.datamodel.document import ConversionResult
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling_core.types.doc import NodeItem, DocItemLabel

from patee.core_types import PipelineContext
from patee.input_types import (
    MonolingualSingleFile,
    MonolingualSingleFilePair,
    MultilingualSingleFile,
)
from patee.step_types import (
    ParallelExtractStep,
    StepResult,
    DocumentContext,
    DocumentSource,
    StepContext,
    DocumentPairContext,
)

logger = logging.getLogger(__name__)


@dataclass
class _DoclingExtractionResult:
    extracted_text: Iterable[NodeItem]
    excluded_text: Iterable[NodeItem]
    seen_labels: set[DocItemLabel]


@dataclass
class DoclingConfig:
    start_page: int = 1
    end_page: int = sys.maxsize
    pages_to_exclude: Set[int] = None

    def __key(self):
        return self.start_page, self.end_page, frozenset(sorted(self.pages_to_exclude))

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        if isinstance(other, DoclingConfig):
            return self.__key() == other.__key()
        return NotImplemented

    def __post_init__(self):
        # Validate page range
        if self.start_page < 1:
            raise ValueError(f"start_page must be at least 1, got {self.start_page}")

        if self.end_page < self.start_page:
            raise ValueError(f"end_page ({self.end_page}) must be >= start_page ({self.start_page})")

        # Initialize empty list of pages_to_exclude if None
        if self.pages_to_exclude is None:
            self.pages_to_exclude = set[int]()

        # Validate exclude_pages
        for page in self.pages_to_exclude:
            if page < 1:
                raise ValueError(f"exclude_pages must contain positive integers, got {page}")
            if page < self.start_page or page > self.end_page:
                raise ValueError(f"exclude_pages entry {page} is outside range {self.start_page}-{self.end_page}")


class DoclingExtractor(ParallelExtractStep):

    def __init__(self, name: str, pipeline_context: PipelineContext, **kwargs):
        super().__init__(name, pipeline_context)

        labels_to_extract = kwargs.get("labels_to_extract", None)
        if labels_to_extract is not None:
            if isinstance(labels_to_extract, str):
                self.labels_to_extract = { labels_to_extract.strip() }
            elif isinstance(labels_to_extract, Iterable):
                self.labels_to_extract = {label.strip() for label in labels_to_extract}
            else:
                raise TypeError(f"labels_to_extract must be str or iterable of str")
        else:
            self.labels_to_extract = {str(DocItemLabel.TEXT)}

        formats = kwargs.get("formats", None)

        if formats is not None and isinstance(formats, Iterable):
            allowed_formats = []
            for dl_format in formats:
                print(dl_format)

        pipeline_options = PdfPipelineOptions()
        pipeline_options.do_ocr = False

        parser = kwargs.get("parser", None)
        if parser is None or parser == "docling":
            self.parser = "docling"
            self._converter = DocumentConverter(
                allowed_formats=[InputFormat.PDF],
                format_options={
                    InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
                }
            )
        elif parser == "pypdfium":
            self.parser = "pypdfium"
            self._converter = DocumentConverter(
                allowed_formats=[InputFormat.PDF],
                format_options={
                    InputFormat.PDF: PdfFormatOption(
                        pipeline_options=pipeline_options, backend=PyPdfiumDocumentBackend
                    )
                }
            )
        else:
            raise ValueError(f"Unsupported parser: {parser}. Supported parsers are 'docling' and 'pypdfium'.")

        logger.info("DocumentConverter supported formats: %s", [f.name for f in self._converter.allowed_formats])

    @staticmethod
    def step_type() -> str:
        return "docling_extractor"

    def _extract_monolingual_single_file(self, context: StepContext, source: MonolingualSingleFile) -> StepResult:
        logger.debug("converting document from %s ...", source.document_path)
        result = self._convert_file(source, None)
        logger.info("document seen labels: %s", [str(label) for label in result.seen_labels])

        context = DocumentContext(
            source=DocumentSource.from_monolingual_file(source),
            text_blocks=[element[1] for element in result.extracted_text],
            extra={
                "excluded_text": result.excluded_text,
                "seen_labels": [label for label in result.seen_labels]
            },
        )
        result = StepResult(
            context=context,
        )

        logger.debug("monolingual single file converted successfully.")

        return result

    def _extract_monolingual_single_file_pair(self, context: StepContext,
                                              source: MonolingualSingleFilePair) -> StepResult:
        logger.debug("converting document 1 from %s ...", source.document_1.document_path)
        document_1_result = self._convert_file(source.document_1, source.shared_config)
        logger.info("document 1 seen labels: %s", [str(label) for label in document_1_result.seen_labels])

        logger.debug("converting document 2 from %s ...", source.document_2.document_path)
        document_2_result = self._convert_file(source.document_2, source.shared_config)
        logger.info("document 2 seen labels: %s", [str(label) for label in document_2_result.seen_labels])

        context = DocumentPairContext(
            document_1=DocumentContext(
                source=DocumentSource.from_monolingual_file(source.document_1),
                text_blocks=[element[1] for element in document_1_result.extracted_text],
                extra={
                    "excluded_text": document_1_result.excluded_text,
                    "seen_labels": [label for label in document_1_result.seen_labels]
                }
            ),
            document_2=DocumentContext(
                source=DocumentSource.from_monolingual_file(source.document_2),
                text_blocks=[element[1] for element in document_2_result.extracted_text],
                extra={
                    "excluded_text": document_2_result.excluded_text,
                    "seen_labels": [label for label in document_2_result.seen_labels]
                }
            ),
        )
        result = StepResult(
            context=context,
        )

        logger.debug("monolingual single file pairs converted successfully.")

        return result

    def _extract_multilingual_single_file(self, context: StepContext, source: MultilingualSingleFile) -> StepResult:
        raise NotImplementedError("Multilingual single file extraction is not implemented yet.")

    def _convert_file(self, file: MonolingualSingleFile, shared_config: Union[DoclingConfig, None]) -> _DoclingExtractionResult:
        page_range = [shared_config.start_page, shared_config.end_page] if shared_config \
            else [file.config.start_page, file.config.end_page] if file.config \
            else None
        excluded_pages = shared_config.pages_to_exclude if shared_config \
            else file.config.pages_to_exclude if file.config \
            else None

        result: ConversionResult

        if page_range is None:
            result = self._converter.convert(file.document_path)
        else:
            result = self._converter.convert(
                file.document_path,
                page_range=page_range)

        if result.status != ConversionStatus.SUCCESS:
            raise ValueError(f"Conversion failed for file {file.document_path}: {result.status}")

        extracted_text: list[(str, str)] = []
        excluded_text: list[(str, str)] = []
        seen_labels: set[DocItemLabel] = set()

        for element in result.assembled.body:
            if element.page_no + 1 not in excluded_pages:
                label = element.label
                text = element.text
                seen_labels.add(label)

                if label in self.labels_to_extract:
                    extracted_text.append((label, text))
                else:
                    excluded_text.append((label, text))

        return _DoclingExtractionResult(
            extracted_text=extracted_text,
            excluded_text=excluded_text,
            seen_labels=seen_labels
        )


