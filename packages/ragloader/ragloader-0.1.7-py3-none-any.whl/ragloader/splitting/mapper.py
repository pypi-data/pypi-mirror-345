from enum import Enum

from ragloader.splitting.text_splitters import (
    CharacterBasedSplitter,
    TokenizerBasedSplitter,
    CodeTextSplitter,
    HtmlTextSplitter,
    MarkdownTextSplitter,
)


class TextSplittersMapper(Enum):
    """Mapper from splitters' names in config to splitting classes."""
    tokenizer_based_splitter = TokenizerBasedSplitter
    character_based_splitter = CharacterBasedSplitter
    code_splitter = CodeTextSplitter
    html_splitter = HtmlTextSplitter
    markdown_splitter = MarkdownTextSplitter
