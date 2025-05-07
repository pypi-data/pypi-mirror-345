import logging
from typing import Literal
from tokenizers import Tokenizer
from langchain_text_splitters import RecursiveCharacterTextSplitter

from ragloader.splitting import BaseTextSplitter


logger = logging.getLogger("logger")


class CharacterBasedSplitter(BaseTextSplitter):
    """Simple character-based splitter with configurable chunk size and overlap."""

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size: int = chunk_size
        self.chunk_overlap: int = chunk_overlap
        self.splitter: RecursiveCharacterTextSplitter | None = None

    def split(self, text: str) -> list[str]:
        """Splits text using recursive character splitter into chunks of a given size
        with a given overlap."""
        if not self.splitter:
            self.splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap
            )
        return self.splitter.split_text(text)


class TokenizerBasedSplitter(BaseTextSplitter):
    """
    Character-based splitter (which uses a tokenizer to count length) with configurable chunk
    size and overlap. Here the chunk size and overlap are specified in tokens, not characters.
    """

    def __init__(
        self,
        chunk_size: int = 200,
        chunk_overlap: int = 10,
        tokenizer_type: Literal["tiktoken", "huggingface"] = "tiktoken",
        tokenizer_name: str = "cl100k_base",
    ):
        self.chunk_size: int = chunk_size
        self.chunk_overlap: int = chunk_overlap
        self.tokenizer_type: Literal["tiktoken", "huggingface"] = tokenizer_type
        self.tokenizer_name: str = tokenizer_name
        self.splitter: RecursiveCharacterTextSplitter | None = None

    def split(self, text: str) -> list[str]:
        """Splits text using tokenizer based splitter into chunks of a given size with
        a given overlap."""
        if not self.splitter:
            self._initialize_splitter(
                self.chunk_size, self.chunk_overlap, self.tokenizer_type, self.tokenizer_name
            )
        return self.splitter.split_text(text)

    def _initialize_splitter(
        self,
        chunk_size: int = 200,
        chunk_overlap: int = 10,
        tokenizer_type: Literal["tiktoken", "huggingface"] = "tiktoken",
        tokenizer_name: str = "cl100k_base",
    ):
        """Initialises a character-based splitter based on the tokenizer name and type."""
        if tokenizer_type == "tiktoken":
            try:
                splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
                    encoding_name=tokenizer_name,
                    chunk_size=chunk_size,
                    chunk_overlap=chunk_overlap,
                )
            except Exception as e:
                logger.error(f"Creating a splitter for tokenizer '{tokenizer_name}' failed "
                             f"with error: {e}")
                raise type(e)(f"Couldn't create the splitter for '{tokenizer_name}'"
                                f" tokenizer due to {e}")
            self.splitter = splitter
        elif tokenizer_type == "huggingface":
            try:
                tokenizer = Tokenizer.from_pretrained(tokenizer_name)
                splitter = RecursiveCharacterTextSplitter.from_huggingface_tokenizer(
                    tokenizer, chunk_size=chunk_size, chunk_overlap=chunk_overlap
                )
            except Exception as e:
                logger.error(f"Creating a splitter for tokenizer '{tokenizer_name}' failed "
                             f"with error: {e}")
                raise type(e)(f"Couldn't create the splitter for '{tokenizer_name}' "
                                f"tokenizer due to {e}")
            self.splitter = splitter
