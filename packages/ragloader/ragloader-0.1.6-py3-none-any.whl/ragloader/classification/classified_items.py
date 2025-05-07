from ragloader.indexing import Document
from ragloader.parsing import ParsedDocument


class ClassifiedDocument(Document):
    def __init__(self, parsed_document: ParsedDocument):
        super().__init__(parsed_document.document_path, parsed_document.group)

        self.document_content = parsed_document.document_content
        self.document_class: str = ""

    def set_document_class(self, document_class: str):
        self.document_class: str = document_class

    @property
    def db_payload(self):
        return {
            "document_name": self.document_name,
            "document_content": self.document_content,
            "document_class": self.document_class,
            "previous_stage_hash": "...",
        }
