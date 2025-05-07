from langchain_community.document_loaders import TextLoader
from langchain_core.documents.base import Document as LangchainDocument

from ragloader.indexing import File
from ragloader.parsing import BaseFileParser
from ragloader.parsing import ParsedFile


class TxtFileParser(BaseFileParser):

    def parse(self, file: File):
        loader: TextLoader = TextLoader(file.file_path)
        loaded_docs: list[LangchainDocument] = loader.load()
        file_content: str = "\n".join([doc.page_content for doc in loaded_docs])
        parsed_file: ParsedFile = ParsedFile(file.file_path, file_content)
        return parsed_file
