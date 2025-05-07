from enum import Enum

from ragloader.parsing.txt_parsers.txt_parser import TxtFileParser
from ragloader.parsing.docx_parsers.docx2txt_parser import Docx2txtFileParser
from ragloader.parsing.pdf_parsers.pymupdf_parser import PyMuPDFFileParser
from ragloader.parsing.image_parsers.openai_image_parser import OpenAIImageParser


class FileParsersMapper(Enum):
    """Mapper from parsers' names in config to parsing classes."""
    txt_parser = TxtFileParser
    pymupdf_parser = PyMuPDFFileParser
    docx2txt_parser = Docx2txtFileParser
    openai_image_parser = OpenAIImageParser
