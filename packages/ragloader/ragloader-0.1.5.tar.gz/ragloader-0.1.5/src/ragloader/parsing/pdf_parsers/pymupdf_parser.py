from langchain_community.document_loaders import PyMuPDFLoader
from langchain_core.documents.base import Document as LangchainDocument

from ragloader.indexing import File
from ragloader.parsing import ParsedFile
from ragloader.parsing import BaseFileParser


class PyMuPDFFileParser(BaseFileParser):
    """This class implements another abstraction layer over PyMuPDF loader."""

    def parse(self, file: File) -> ParsedFile:
        loader: PyMuPDFLoader = PyMuPDFLoader(file.file_path)
        loaded_docs: list[LangchainDocument] = loader.load()
        file_content: str = "\n".join([doc.page_content for doc in loaded_docs])
        parsed_file: ParsedFile = ParsedFile(file.file_path, file_content)
        return parsed_file
