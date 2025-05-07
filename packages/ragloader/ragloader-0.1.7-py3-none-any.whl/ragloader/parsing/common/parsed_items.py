from __future__ import annotations
import hashlib
from pathlib import Path
from qdrant_client.models import Record

from ragloader.indexing import File, Document


class ParsedFile(File):
    """This class provides an abstraction for a parsed file."""

    def __init__(self,
                 file_path: Path | str,
                 file_content: str
        ):
        super().__init__(file_path)

        self.file_content: str = file_content

    def __repr__(self):
        return f"ParsedFile(name={self.file_name})"


class ParsedDocument(Document):
    """This class provides an abstraction for a parsed document."""

    def __init__(self, document: Document):
        super().__init__(document.document_path, document.group)

        self.document_content: str = ""
        self.parsed_files: list[ParsedFile] = []

        self.hash_indexed = hashlib.new("md5")

    def add_parsed_file(self, parsed_file: ParsedFile):
        """Adds a parsed file to the list of parsed files for a document."""
        self.document_content += ("\n\n" + parsed_file.file_content)
        self.parsed_files.append(parsed_file)

        self.hash_indexed.update(parsed_file.hash.hexdigest().encode("utf-8"))

    @property
    def hash(self) -> str:
        return hashlib.md5(str(self.document_content).encode("utf-8")).hexdigest()

    @classmethod
    def from_db_record(cls, parsed_document_record: Record) -> ParsedDocument:
        payload: dict = parsed_document_record.payload
        document_path, group = payload["document_path"], payload["group"]

        document: Document = Document(document_path=document_path, group=group)
        parsed_document: ParsedDocument = cls(document)
        for file_data in payload["parsed_files"]:
            parsed_file: ParsedFile = ParsedFile(file_data["file_path"], file_data["file_content"])
            parsed_document.add_parsed_file(parsed_file)

        return parsed_document

    @property
    def db_payload(self):
        return {
            "document_path": self.document_path,
            "document_name": self.document_name,
            "group": self.group,
            "previous_stage_hash": self.hash_indexed if type(self.hash_indexed)==str else self.hash_indexed.hexdigest(),
            "parsed_files": [
                {
                    "file_path": str(parsed_file.file_path),
                    "file_name": parsed_file.file_name,
                    "file_content": parsed_file.file_content,
                }
                for parsed_file in self.parsed_files]
        }

    def __repr__(self):
        parsed_files_repr: str = ", ".join(repr(parsed_file) for parsed_file in self.parsed_files)
        return (f"ParsedDocument(n_files={len(self.parsed_files)},"
                f" parsed_files=[\n\t\t\t\t{parsed_files_repr}\n\t\t\t])")
