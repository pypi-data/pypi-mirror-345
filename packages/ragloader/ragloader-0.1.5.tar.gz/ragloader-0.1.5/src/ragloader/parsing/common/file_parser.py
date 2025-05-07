from abc import ABC, abstractmethod

from ragloader.indexing.documents import File


class BaseFileParser(ABC):
    """Abstract class for all file parsers"""

    @abstractmethod
    def parse(self, file: File):
        raise NotImplementedError
