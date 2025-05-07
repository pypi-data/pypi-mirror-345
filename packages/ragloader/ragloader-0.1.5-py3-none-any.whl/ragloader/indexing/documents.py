from __future__ import annotations
import hashlib
from uuid import UUID
from pathlib import Path
from _hashlib import HASH


class File:
    """Represents a file to be parsed."""

    def __init__(self, file_path: Path | str):
        self.file_path: Path = Path(file_path)
        self.file_name: str = self.file_path.name
        self.extension: str = self.file_path.suffix

        self.hash = self.__generate_hash()

    def __generate_hash(self, block_size=4096) -> HASH:
        hash_obj: HASH = hashlib.new("md5")
        with open(self.file_path, "rb") as file:
            while chunk := file.read(block_size):
                hash_obj.update(chunk)

        return hash_obj

    def __repr__(self):
        return f"File(name={self.file_name})"


class Document:
    """Represents a document which consists of a list of files."""

    def __init__(self, document_path: Path | str, group: str):
        self.document_path: Path = Path(document_path)
        self.document_name: str = self.document_path.name
        self.files: list[File] = []
        self.group: str = group

        self.hash_indexed = hashlib.new("md5")
        self.uuid: UUID = UUID(hashlib.md5(str(self.document_path).encode("utf-8")).hexdigest())

    def __add_file(self, file: File):
        self.files.append(file)
        self.hash_indexed.update(file.hash.hexdigest().encode("utf-8"))

    @property
    def hash(self) -> str:
        return self.hash_indexed.hexdigest()

    @classmethod
    def from_file_path(cls, file_path: Path, group: str) -> Document:
        """
        Create a Document object based on a single file.

        Args:
            file_path (Path): path to the file
            group (str): name of the group which this document belongs to
        """
        document: Document = cls(document_path=file_path, group=group)
        file: File = File(file_path)
        document.__add_file(file)
        return document

    @classmethod
    def from_directory_path(cls, directory_path: Path, group: str) -> Document:
        """
        Create a Document object based on a directory with files.

        Args:
            directory_path (Path): path to the directory with files
            group (str): name of the group which this document belongs to
        """
        document: Document = cls(document_path=directory_path, group=group)
        for file_path in sorted(filter(Path.is_file, directory_path.glob("*"))):
            document.__add_file(File(file_path))

        return document if document.files else None

    def __repr__(self):
        files_repr: str = ", ".join(repr(file) for file in self.files)
        return f"Document(n_files={len(self.files)}, files=[\n\t\t\t\t{files_repr}\n\t\t\t])"


class Group:
    """Represents a group of documents."""

    def __init__(self, group_path: Path | str):
        self.group_name: str = Path(group_path).name
        self.documents: list[Document] = []

    def add_document(self, document: Document):
        self.documents.append(document)

    def __repr__(self):
        documents_repr: str = ",\n\t\t".join(repr(document) for document in self.documents)
        return (f"Group(n_docs={len(self.documents)}, name='{self.group_name}',"
                f" documents=[\n\t\t{documents_repr}\n\t])")


class DocumentsStructure:
    """Represents the whole structure of documents to be parsed."""

    def __init__(self, path: Path | str):
        self.root_path: Path = Path(path)
        self.name: str = self.root_path.name
        self.groups: list[Group] = []

    def add_group(self, group: Group):
        self.groups.append(group)


    def __repr__(self):
        separator_length: int = 30
        group_separator: str = separator_length * "="
        groups_repr: str = f"\n\t{group_separator}\n\t".join(repr(group) for group in self.groups)
        return (f"DocumentsStructure(n_groups={len(self.groups)}, name='{self.name}',"
                f" groups=[\n\t{group_separator}\n\t{groups_repr}\n\t{group_separator}\n])")
