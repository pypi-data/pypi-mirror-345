from dataclasses import dataclass
from pathlib import Path
from typing import Union, List, Any


@dataclass()
class SingleFile:
    document_path: Union[str, Path]

    def __key(self):
        return self.document_path

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        if isinstance(other, SingleFile):
            return self.__key() == other.__key()
        return NotImplemented

    def __post_init__(self):
        # Convert string path to Path object
        if isinstance(self.document_path, str):
            self.document_path = Path(self.document_path)

        # Validate document exists and is a file
        if not self.document_path.exists():
            raise ValueError(f"Document path not found: {self.document_path}")

        if not self.document_path.is_file():
            raise ValueError(f"Document path is not a file: {self.document_path}")


@dataclass
class MonolingualSingleFile(SingleFile):
    iso2_language: str
    config: Any = None

    def __key(self):
        return self.document_path, self.iso2_language, self.config

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        if isinstance(other, MonolingualSingleFile):
            return self.__key() == other.__key()
        return NotImplemented

    def __post_init__(self):
        super().__post_init__()

        # Validate language code
        if len(self.iso2_language) != 2:
            raise ValueError(f"iso2_language must be a 2-letter ISO code, got {self.iso2_language}")


@dataclass
class MonolingualSingleFilePair:
    document_1: MonolingualSingleFile
    document_2: MonolingualSingleFile
    shared_config: Any = None

    def __key(self):
        return self.document_1, self.document_2, self.shared_config

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        if isinstance(other, MonolingualSingleFilePair):
            return self.__key() == other.__key()
        return NotImplemented

    def __post_init__(self):
        # Documents should define different languages
        if self.document_1.iso2_language == self.document_2.iso2_language:
            raise ValueError("Documents must have different languages")

        # Should be just one shared config or each document must have its own
        if self.shared_config is None:
            if ((self.document_1.config is not None and self.document_2.config is None) or
                (self.document_1.config is None and self.document_2.config is not None)):
                raise ValueError("Define configuration for both documents or use shared config")
        else:
            if self.document_1.config is not None or self.document_2.config is not None:
                raise ValueError("Define configuration for both documents or use shared config")


@dataclass
class MultilingualSingleFile(SingleFile):
    iso2_languages: List[str]
    config: Any = None

    def __key(self):
        return self.document_path, self.iso2_languages, self.config

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        if isinstance(other, MultilingualSingleFile):
            return self.__key() == other.__key()
        return NotImplemented

    def __post_init__(self):
        super().__post_init__()
        # Validate language codes
        if len(self.iso2_languages) != 2:
            raise ValueError(f"iso2_languages must contain only two 2-letter ISO codes, got {self.iso2_languages}")

        for lang in self.iso2_languages:
            if len(lang) != 2:
                raise ValueError(f"iso2_languages must contain 2-letter ISO codes, got {lang}")

        unique_languages = set(lang for lang in self.iso2_languages)
        if len(unique_languages) != len(self.iso2_languages):
            raise ValueError("iso2_languages must contain unique 2-letter ISO codes")
