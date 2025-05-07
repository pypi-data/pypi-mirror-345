from typing import Optional
from langchain_core.documents.base import Document as LangchainDocument
from langchain_text_splitters import HTMLSemanticPreservingSplitter

from ragloader.splitting import BaseTextSplitter


DEFAULT_HEADERS_TO_SPLIT_ON = [
    ("h1", "Header 1"),
    ("h2", "Header 2"),
]
DEFAULT_ELEMENTS_TO_PRESERVE = ["table", "ul", "ol"]


class HtmlTextSplitter(BaseTextSplitter):
    """
    HTML splitter that preserves semantic structure of the content.
    It splits the text based on the headers and elements specified in the configuration.
    """

    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        headers_to_split_on: list[tuple] = DEFAULT_HEADERS_TO_SPLIT_ON,
        elements_to_preserve: Optional[list[str]] = DEFAULT_ELEMENTS_TO_PRESERVE,
    ):
        self.chunk_size: int = chunk_size
        self.chunk_overlap: int = chunk_overlap
        self.headers_to_split_on: list[tuple] = headers_to_split_on
        self.elements_to_preserve: Optional[list[str]] = elements_to_preserve
        self.splitter: HTMLSemanticPreservingSplitter | None = None

    def split(self, text: str) -> list[str]:
        """Splits HTML text while preserving semantic elements like tables and lists."""
        if not self.splitter:
            self.splitter = HTMLSemanticPreservingSplitter(
                headers_to_split_on=self.headers_to_split_on,
                elements_to_preserve=self.elements_to_preserve,
                max_chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
            )
        split_documents: list[LangchainDocument] = self.splitter.split_text(text)
        return [doc.page_content for doc in split_documents]
