from langchain_community.document_loaders import Docx2txtLoader
from langchain_core.documents.base import Document as LangchainDocument

from ragloader.indexing import File
from ragloader.parsing import ParsedFile
from ragloader.parsing import BaseFileParser


class Docx2txtFileParser(BaseFileParser):
    """This class implements another abstraction layer over `Docx2txtLoader`."""

    def parse(self, file: File) -> ParsedFile:
        loader: Docx2txtLoader = Docx2txtLoader(file.file_path)
        loaded_docs: list[LangchainDocument] = loader.load()
        file_content: str = "\n".join([doc.page_content for doc in loaded_docs])
        parsed_file: ParsedFile = ParsedFile(file.file_path, file_content)
        return parsed_file
