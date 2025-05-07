from abc import ABC, abstractmethod


class BaseTextSplitter(ABC):
    @abstractmethod
    def split(self, text: str) -> list[str]:
        raise NotImplementedError
