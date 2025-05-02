import re
from pathlib import Path

import pytest

from patee.input_types import (
    SingleFile,
    MonolingualSingleFile,
    MonolingualSingleFilePair,
    MultilingualSingleFile,
)
from tests.utils.mothers.sources import (
    get_existing_monolingual_single_file,
    PDF_ES_FILE,
    PDF_CA_FILE
)


class TestSingleFile:
    def test_create_with_string_path(self, monkeypatch):
        monkeypatch.setattr(Path, "exists", lambda x: True)
        monkeypatch.setattr(Path, "is_file", lambda x: True)

        single_file = SingleFile("path/to/file")

        assert isinstance(single_file.document_path, Path)
        assert single_file.document_path == Path("path/to/file")

    def test_create_with_path_object(self, monkeypatch):
        monkeypatch.setattr(Path, "exists", lambda x: True)
        monkeypatch.setattr(Path, "is_file", lambda x: True)

        single_file = SingleFile(Path("path/to/file"))

        assert single_file.document_path == Path("path/to/file")

    def test_file_not_found(self, monkeypatch):
        monkeypatch.setattr(Path, "exists", lambda x: False)

        with pytest.raises(ValueError, match="Document path not found"):
            SingleFile(document_path="nonexistent.pdf")

    def test_path_not_a_file(self, monkeypatch):
        monkeypatch.setattr(Path, "exists", lambda x: True)
        monkeypatch.setattr(Path, "is_file", lambda x: False)

        with pytest.raises(ValueError, match="Document path is not a file"):
            SingleFile(document_path="directory/")


class TestMonolingualSingleFile:
    def test_create_valid(self, monkeypatch):
        monkeypatch.setattr(Path, "exists", lambda x: True)
        monkeypatch.setattr(Path, "is_file", lambda x: True)

        mono_file = get_existing_monolingual_single_file()

        assert mono_file.document_path == PDF_ES_FILE
        assert mono_file.iso2_language == "es"
        assert mono_file.config is None

    def test_create_with_config(self, monkeypatch):
        monkeypatch.setattr(Path, "exists", lambda x: True)
        monkeypatch.setattr(Path, "is_file", lambda x: True)

        config = dict

        mono_file = get_existing_monolingual_single_file(dict)

        assert mono_file.config == config

    def test_invalid_language_code(self, monkeypatch):
        monkeypatch.setattr(Path, "exists", lambda x: True)
        monkeypatch.setattr(Path, "is_file", lambda x: True)

        with pytest.raises(ValueError, match="iso2_language must be a 2-letter ISO code"):
            MonolingualSingleFile(document_path=PDF_ES_FILE, iso2_language="esp")


class TestMonolingualSingleFilePair:
    def test_create_valid_with_shared_config(self, monkeypatch):
        monkeypatch.setattr(Path, "exists", lambda x: True)
        monkeypatch.setattr(Path, "is_file", lambda x: True)

        doc1 = MonolingualSingleFile(document_path=PDF_ES_FILE, iso2_language="es")
        doc2 = MonolingualSingleFile(document_path=PDF_CA_FILE, iso2_language="ca")
        shared_config = dict

        pair = MonolingualSingleFilePair(
            document_1=doc1,
            document_2=doc2,
            shared_config=shared_config,
        )

        assert pair.document_1 == doc1
        assert pair.document_2 == doc2
        assert pair.shared_config == shared_config

    def test_create_valid_with_individual_config(self, monkeypatch):
        monkeypatch.setattr(Path, "exists", lambda x: True)
        monkeypatch.setattr(Path, "is_file", lambda x: True)

        doc1_config = dict
        doc2_config = dict

        doc1 = MonolingualSingleFile(document_path=PDF_ES_FILE, iso2_language="es", config=doc1_config)
        doc2 = MonolingualSingleFile(document_path=PDF_CA_FILE, iso2_language="ca", config=doc2_config)

        pair = MonolingualSingleFilePair(
            document_1=doc1,
            document_2=doc2
        )

        assert pair.shared_config is None

    def test_same_language_error(self, monkeypatch):
        monkeypatch.setattr(Path, "exists", lambda x: True)
        monkeypatch.setattr(Path, "is_file", lambda x: True)

        doc1 = MonolingualSingleFile(document_path=PDF_ES_FILE, iso2_language="es")
        doc2 = MonolingualSingleFile(document_path=PDF_CA_FILE, iso2_language="es")

        with pytest.raises(ValueError, match="Documents must have different languages"):
            MonolingualSingleFilePair(document_1=doc1, document_2=doc2)

    def test_mixed_config_error_one_missing(self, monkeypatch):
        monkeypatch.setattr(Path, "exists", lambda x: True)
        monkeypatch.setattr(Path, "is_file", lambda x: True)

        doc1_config = dict
        doc1 = MonolingualSingleFile(document_path=PDF_ES_FILE, iso2_language="es", config=doc1_config)
        doc2 = MonolingualSingleFile(document_path=PDF_CA_FILE, iso2_language="ca")

        with pytest.raises(ValueError, match="Define configuration for both documents or use shared config"):
            MonolingualSingleFilePair(document_1=doc1, document_2=doc2)

    def test_mixed_config_error_with_shared(self, monkeypatch):
        monkeypatch.setattr(Path, "exists", lambda x: True)
        monkeypatch.setattr(Path, "is_file", lambda x: True)

        doc1_config = dict
        shared_config = dict
        doc1 = MonolingualSingleFile(document_path=PDF_ES_FILE, iso2_language="es", config=doc1_config)
        doc2 = MonolingualSingleFile(document_path=PDF_CA_FILE, iso2_language="ca")

        with pytest.raises(ValueError, match="Define configuration for both documents or use shared config"):
            MonolingualSingleFilePair(
                document_1=doc1,
                document_2=doc2,
                shared_config=shared_config,
            )


class TestMultilingualSingleFile:
    def test_create_valid(self, monkeypatch):
        monkeypatch.setattr(Path, "exists", lambda x: True)
        monkeypatch.setattr(Path, "is_file", lambda x: True)

        multi_file = MultilingualSingleFile(
            document_path=PDF_ES_FILE,
            iso2_languages=["es", "ca"]
        )
        assert multi_file.document_path == PDF_ES_FILE
        assert multi_file.iso2_languages == ["es", "ca"]
        assert multi_file.config is None

    def test_create_with_config(self, monkeypatch):
        monkeypatch.setattr(Path, "exists", lambda x: True)
        monkeypatch.setattr(Path, "is_file", lambda x: True)

        config = dict
        multi_file = MultilingualSingleFile(
            document_path=PDF_ES_FILE,
            iso2_languages=["es", "ca"],
            config=config
        )
        assert multi_file.config == config

    def test_invalid_language_code_number(self, monkeypatch):
        monkeypatch.setattr(Path, "exists", lambda x: True)
        monkeypatch.setattr(Path, "is_file", lambda x: True)

        with pytest.raises(ValueError, match=re.escape("iso2_languages must contain only two 2-letter ISO codes, got ['es', 'ca', 'en']")):
            MultilingualSingleFile(
                document_path=PDF_ES_FILE,
                iso2_languages=["es", "ca", "en"]
            )

    def test_invalid_language_code(self, monkeypatch):
        monkeypatch.setattr(Path, "exists", lambda x: True)
        monkeypatch.setattr(Path, "is_file", lambda x: True)

        with pytest.raises(ValueError, match="iso2_languages must contain 2-letter ISO codes"):
            MultilingualSingleFile(
                document_path=PDF_ES_FILE,
                iso2_languages=["es", "cat"]
            )

    def test_duplicate_language_codes(self, monkeypatch):
        monkeypatch.setattr(Path, "exists", lambda x: True)
        monkeypatch.setattr(Path, "is_file", lambda x: True)

        with pytest.raises(ValueError, match="iso2_languages must contain unique 2-letter ISO codes"):
            MultilingualSingleFile(
                document_path=PDF_ES_FILE,
                iso2_languages=["es", "es"]
            )