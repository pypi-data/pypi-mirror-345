import hashlib
from _hashlib import HASH
from uuid import UUID

from ragloader.extraction import ExtractedDocument
from ragloader.indexing import Document


class DocumentChunk:
    """Class representing a chunk of a document."""

    def __init__(self, content: str, index: int, document_metadata: dict):
        self.content: str = content
        self.chunk_index: int = index
        self.document_metadata: dict = document_metadata

        self.uuid: UUID = self.__generate_uuid()

    def __generate_uuid(self) -> UUID:
        chunk_id: str = f"{self.document_metadata['parent_document_path']}__{self.chunk_index}"
        chunk_hash: HASH = hashlib.md5(chunk_id.encode())
        chunk_uuid: UUID = UUID(chunk_hash.hexdigest())
        return chunk_uuid

    def __repr__(self):
        return (f"DocumentChunk(chunk_index={self.chunk_index}, metadata={self.document_metadata}, "
                f"content='{self.content}')")


class ChunkedDocument(Document):
    """Class representing a document split into chunks."""

    def __init__(self, extracted_document: ExtractedDocument):
        super().__init__(extracted_document.document_path, extracted_document.group)

        self.document_class: str = extracted_document.document_class
        self.chunks: list[DocumentChunk] = []

    def add_chunk(self, content: str):
        document_metadata: dict = {
                "parent_document_uuid": self.uuid,
                "parent_document_name": self.document_name,
                "parent_document_path": self.document_path,
                "parent_document_class": self.document_class
            }

        chunk: DocumentChunk = DocumentChunk(content, len(self.chunks), document_metadata)
        self.chunks.append(chunk)

    @property
    def db_payload(self):
        return {
            "document_name": self.document_name,
            "document_class": self.document_class,
            "previous_stage_hash": "...",
            "document_chunks": [
                {"chunk_index": chunk.chunk_index, "content": chunk.content,
                 "metadata": chunk.document_metadata}
            for chunk in self.chunks]
        }

    def __repr__(self):
        return (f"ChunkedDocument(name={self.document_name}, n_chunks={len(self.chunks)}, "
                f"document_class={self.document_class})")
