from ragloader.indexing import Document
from ragloader.splitting import ChunkedDocument, DocumentChunk


class EmbeddedChunk(DocumentChunk):
    def __init__(self, document_chunk: DocumentChunk, embedding: list[float], embedding_model: str):
        super().__init__(document_chunk.content, document_chunk.chunk_index,
                         document_chunk.document_metadata)

        self.embedding_model = embedding_model
        self.embedding: list[float] = embedding

    @property
    def db_payload(self):
        return {
            "embedding_model": self.embedding_model,
            "content": self.content,
            "metadata": self.document_metadata,
            "previous_stage_hash": "...",
        }

    def __repr__(self):
        embedding_preview = (f"[{round(self.embedding[0], 2)}..., {round(self.embedding[1], 2)}..., ..., "
                             f"{round(self.embedding[-2], 2)}..., {round(self.embedding[-1], 2)}...])"
                             if len(self.embedding) > 4 else str(self.embedding))
        return (f"EmbeddedChunk(chunk_index={self.chunk_index}, metadata={self.document_metadata}, "
                f"content='{self.content}', embedding={embedding_preview})")


class EmbeddedDocument(Document):
    def __init__(self, chunked_document: ChunkedDocument):
        super().__init__(chunked_document.document_path, chunked_document.group)

        self.document_class: str = chunked_document.document_class
        self.embedded_chunks: list[EmbeddedChunk] = []

    def add_chunk(self, chunk: EmbeddedChunk):
        self.embedded_chunks.append(chunk)

    def __repr__(self):
        return f"EmbeddedDocument(name={self.document_name}, n_chunks={len(self.embedded_chunks)})"
