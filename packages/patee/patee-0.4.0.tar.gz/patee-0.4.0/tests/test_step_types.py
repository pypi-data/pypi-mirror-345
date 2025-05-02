import json
from pathlib import Path

import pytest

from patee.input_types import MultilingualSingleFile, MonolingualSingleFile
from patee.step_types import (
    StepContext,
    DocumentSource,
    DocumentContext,
    DocumentPairContext,
    StepResult,
    TEXT_BLOCK_SEPARATOR
)
from tests.utils.mothers.contexts import get_pipeline_context, get_run_context
from tests.utils.mothers.sources import get_existing_pdf_file


class TestStepContext:
    def test_initialization_without_dir(self):
        pipeline_context = get_pipeline_context()
        run_context = get_run_context(output_dir=None)
        step_context = StepContext(
            pipeline_context=pipeline_context,
            run_context=run_context,
            step_dir=None,
        )

        assert step_context.step_dir is None

    def test_initialization_with_dir(self):
        step_dir = Path("/path/to/step")
        pipeline_context = get_pipeline_context()
        run_context = get_run_context(output_dir=step_dir)
        step_context = StepContext(
            pipeline_context=pipeline_context,
            run_context=run_context,
            step_dir=step_dir,
        )

        assert step_context.step_dir == step_dir


class TestDocumentSource:
    def test_initialization(self):
        path = Path("/path/to/file.pdf")
        language = "es"
        source = DocumentSource(path, language)
        assert source.document_path == path
        assert source.iso2_language == language

    def test_from_monolingual_file(self):
        path = get_existing_pdf_file()
        language = "fr"
        mono_file = MonolingualSingleFile(
            document_path=path,
            iso2_language=language,
        )

        source = DocumentSource.from_monolingual_file(mono_file)
        assert source.document_path == path
        assert source.iso2_language == language

    def test_from_multilingual_file(self):
        path = get_existing_pdf_file()
        languages = ["en", "es"]
        multi_file = MultilingualSingleFile(
            document_path=path,
            iso2_languages=languages,
        )

        source_0 = DocumentSource.from_multilingual_file(multi_file, 0)
        source_1 = DocumentSource.from_multilingual_file(multi_file, 1)

        assert source_0.document_path == path
        assert source_0.iso2_language == "en"
        assert source_1.document_path == path
        assert source_1.iso2_language == "es"


class TestDocumentContext:
    def test_initialization(self):
        source = DocumentSource(Path("/path/to/file.pdf"), "en")
        text_blocks = ["Sample text content", "Another block of text"]
        extra = {"metadata": "test metadata"}

        doc_context = DocumentContext(source, text_blocks, extra)

        assert doc_context.source == source
        assert doc_context.text_blocks == text_blocks
        assert doc_context.extra == extra

    def test_dump_to(self, tmp_path):
        source = DocumentSource(Path("document.pdf"), "en")
        text_blocks = ["Sample text content", "Another block of text"]
        extra = {"metadata": "test metadata"}

        doc_context = DocumentContext(source, text_blocks, extra)
        doc_context.dump_to(tmp_path)

        # Check text file was created with correct content
        text_path = tmp_path / "document.txt"
        assert text_path.exists()
        assert text_path.read_text().split(TEXT_BLOCK_SEPARATOR) == text_blocks

        # Check extra file was created with correct content
        extra_path = tmp_path / "document_extra.json"
        assert extra_path.exists()
        assert json.loads(extra_path.read_text()) == extra

    def test_dump_to_no_extra(self, tmp_path):
        source = DocumentSource(Path("document.pdf"), "en")
        text_blocks = ["Sample text content", "Another block of text"]
        extra = {}  # Empty extra

        doc_context = DocumentContext(source, text_blocks, extra)
        doc_context.dump_to(tmp_path)

        # Check text file was created
        text_path = tmp_path / "document.txt"
        assert text_path.exists()

        # No extra file should be created
        extra_path = tmp_path / "document_extra.json"
        assert not extra_path.exists()

    def test_load_from(self, tmp_path):
        # Create original context
        original_source = DocumentSource(Path("document.pdf"), "en")
        original_text_blocks = ["Original text", "Another original block"]

        # Write text file with new content
        text_file = tmp_path / "document.txt"
        text_file.write_text(TEXT_BLOCK_SEPARATOR.join(original_text_blocks))

        # Load from the directory
        loaded_context = DocumentContext.load_from(original_source, tmp_path)

        # Check loaded content
        assert loaded_context.source == original_source
        assert loaded_context.text_blocks == original_text_blocks
        assert loaded_context.extra == {}  # Should be empty since no extra file

    def test_load_from_invalid_dir(self):
        original_source = DocumentSource(Path("document.pdf"), "en")

        with pytest.raises(ValueError, match="is not a directory"):
            DocumentContext.load_from(original_source, Path("/non/existent/path"))


class TestDocumentPairContext:
    def test_initialization(self):
        source1 = DocumentSource(Path("doc1.pdf"), "en")
        source2 = DocumentSource(Path("doc2.pdf"), "es")

        doc1 = DocumentContext(source1, ["English text"], {"lang": "en"})
        doc2 = DocumentContext(source2, ["Spanish text"], {"lang": "es"})

        pair = DocumentPairContext(doc1, doc2)
        assert pair.document_1 == doc1
        assert pair.document_2 == doc2

    def test_dump_to(self, tmp_path):
        source1 = DocumentSource(Path("doc1.pdf"), "en")
        source2 = DocumentSource(Path("doc2.pdf"), "es")

        doc1 = DocumentContext(source1, ["English text"], {"lang": "en"})
        doc2 = DocumentContext(source2, ["Spanish text"], {"lang": "es"})

        pair = DocumentPairContext(doc1, doc2)
        pair.dump_to(tmp_path)

        # Check files were created for both documents
        assert (tmp_path / "doc1.txt").exists()
        assert (tmp_path / "doc2.txt").exists()
        assert (tmp_path / "doc1_extra.json").exists()
        assert (tmp_path / "doc2_extra.json").exists()

    def test_dump_to_invalid_dir(self):
        source1 = DocumentSource(Path("doc1.pdf"), "en")
        source2 = DocumentSource(Path("doc2.pdf"), "es")

        doc1 = DocumentContext(source1, ["English text"], {})
        doc2 = DocumentContext(source2, ["Spanish text"], {})

        pair = DocumentPairContext(doc1, doc2)

        with pytest.raises(ValueError, match="is not a directory"):
            pair.dump_to(Path("/non/existent/path"))

    def test_read_from(self, tmp_path):
        # Create original pair context
        source1 = DocumentSource(Path("doc1.pdf"), "en")
        source2 = DocumentSource(Path("doc2.pdf"), "es")

        doc1 = DocumentContext(source1, ["Original English"], {"lang": "en"})
        doc2 = DocumentContext(source2, ["Original Spanish"], {"lang": "es"})

        original_pair = DocumentPairContext(doc1, doc2)

        # Write files with new content
        (tmp_path / "doc1.txt").write_text("New English text")
        (tmp_path / "doc2.txt").write_text("New Spanish text")

        # Read from directory
        loaded_pair = DocumentPairContext.read_from(original_pair, tmp_path)

        # Check loaded content
        assert loaded_pair.document_1.source == doc1.source
        assert loaded_pair.document_2.source == doc2.source
        assert loaded_pair.document_1.text_blocks == ["New English text"]
        assert loaded_pair.document_2.text_blocks == ["New Spanish text"]
        assert loaded_pair.document_1.extra == {}
        assert loaded_pair.document_2.extra == {}

    def test_read_from_invalid_dir(self):
        source1 = DocumentSource(Path("doc1.pdf"), "en")
        source2 = DocumentSource(Path("doc2.pdf"), "es")

        doc1 = DocumentContext(source1, ["English text"], {})
        doc2 = DocumentContext(source2, ["Spanish text"], {})

        pair = DocumentPairContext(doc1, doc2)

        with pytest.raises(ValueError, match="is not a directory"):
            DocumentPairContext.read_from(pair, Path("/non/existent/path"))


class TestStepResult:
    def test_initialization_with_context(self):
        source1 = DocumentSource(Path("doc1.pdf"), "en")
        source2 = DocumentSource(Path("doc2.pdf"), "es")

        doc1 = DocumentContext(source1, ["English text"], {})
        doc2 = DocumentContext(source2, ["Spanish text"], {})

        pair = DocumentPairContext(doc1, doc2)
        result = StepResult(pair, False)

        assert result.context == pair
        assert result.should_stop_pipeline is False

    def test_initialization_without_context(self):
        result = StepResult(None, True)
        assert result.context is None
        assert result.should_stop_pipeline is True