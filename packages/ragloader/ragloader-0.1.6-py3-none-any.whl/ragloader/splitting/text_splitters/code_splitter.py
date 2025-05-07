from langchain_text_splitters import RecursiveCharacterTextSplitter, Language

from ragloader.splitting import BaseTextSplitter


class CodeTextSplitter(BaseTextSplitter):
    """Simple code splitter with configurable chunk size and overlap and provided language."""

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200, language: str | Language = "python"):
        self.chunk_size: int = chunk_size
        self.chunk_overlap: int = chunk_overlap
        self.language: str | Language = language
        self.splitter: RecursiveCharacterTextSplitter | None = None

    def split(self, text: str) -> list[str]:
        """Splits text using recursive character splitter into chunks of a given
        size with a given overlap."""
        if not self.splitter:
            self.splitter = RecursiveCharacterTextSplitter.from_language(
                language=self.language, chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap
            )
        return self.splitter.split_text(text)
