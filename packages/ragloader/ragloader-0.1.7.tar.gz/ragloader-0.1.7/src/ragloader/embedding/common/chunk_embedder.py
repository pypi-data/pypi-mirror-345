from abc import ABC, abstractmethod

from ragloader.embedding import EmbeddedChunk
from ragloader.splitting import DocumentChunk


class ChunkEmbedder(ABC):
    model_name = None
    vector_length = None
    @abstractmethod
    def embed(self, chunk: DocumentChunk) -> EmbeddedChunk:
        raise NotImplementedError

    def __repr__(self):
        return f"ChunkEmbedder(model_name='{self.model_name}')"