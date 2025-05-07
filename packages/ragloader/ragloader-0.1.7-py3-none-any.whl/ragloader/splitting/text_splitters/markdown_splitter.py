from langchain_text_splitters import MarkdownTextSplitter as LangchainMarkdownTextSplitter

from ragloader.splitting import BaseTextSplitter


class MarkdownTextSplitter(BaseTextSplitter):
    """Simple Markdown splitter with configurable chunk size and overlap"""

    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
    ):
        self.chunk_size: int = chunk_size
        self.chunk_overlap: int = chunk_overlap
        self.splitter: LangchainMarkdownTextSplitter | None = None

    def split(self, text: str) -> list[str]:
        """Splits markdown text into chunks of a given size with a given overlap."""
        if not self.splitter:
            self.splitter = LangchainMarkdownTextSplitter(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
            )
        return self.splitter.split_text(text)
