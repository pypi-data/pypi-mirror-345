from ragloader.indexing import Document
from ragloader.classification import ClassifiedDocument


class ExtractedDocument(Document):
    def __init__(self, classified_document: ClassifiedDocument):
        super().__init__(classified_document.document_path, classified_document.group)

        self.document_content: str = classified_document.document_content
        self.document_class: str = classified_document.document_class
        self.document_structure: dict | None = None

    def set_document_structure(self, document_structure: dict):
        self.document_structure: dict = document_structure

    @property
    def db_payload(self):
        return {
            "document_name": self.document_name,
            "document_content": self.document_content,
            "document_class": self.document_class,
            "document_structure": self.document_structure,
            "previous_stage_hash": "...",
        }
