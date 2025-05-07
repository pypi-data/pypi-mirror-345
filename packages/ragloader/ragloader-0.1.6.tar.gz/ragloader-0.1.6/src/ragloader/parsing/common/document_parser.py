import logging

from ragloader.exceptions import ParserNotFound
from ragloader.conf import Config
from ragloader.indexing import Document, File
from ragloader.parsing import ParsedFile, ParsedDocument
from ragloader.parsing import BaseFileParser
from ragloader.parsing.mapper import FileParsersMapper


logger = logging.getLogger("logger")


class DocumentParser:
    """This class is used to parse a document (extract its content)."""

    def __init__(self, config: Config):
        self.extensions_parsers: dict = config["pipeline_stages"]["parsing"]["parsers"]
        self.extensions_parsers_instances: dict = dict().fromkeys(self.extensions_parsers.keys())

        logger.info("DocumentParser initialized.")
        logger.debug(f"DocumentParser extensions parsers: {self.extensions_parsers}.")

    def parse(self, document: Document) -> ParsedDocument:
        """
        This method converts a `Document` object to a `ParsedDocument` object.
        It iterates over all files in the document and combines all `ParsedFile` objects together.
        """
        files: list[File] = document.files

        parsed_document: ParsedDocument = ParsedDocument(document)

        for file in files:
            parser_name: str = self.extensions_parsers.get(file.extension)
            if parser_name is None:
                logger.error(f"No parser configured for extension: {file.extension}.")
                raise ParserNotFound(f"No parser configured for extension: {file.extension}. "
                                     f"You can set it in the config.")

            if self.extensions_parsers_instances[file.extension] is not None:
                parser: BaseFileParser = self.extensions_parsers_instances[file.extension]
            else:
                try:
                    parser_class: type = FileParsersMapper[parser_name].value
                except KeyError:
                    logger.error(
                        f"Tried to access '{parser_name}' parser which is not yet implemented")
                    raise ParserNotFound(f"Parser {parser_name} not implemented.")

                parser: BaseFileParser = parser_class()
                self.extensions_parsers_instances[file.extension]: BaseFileParser = parser

            parsed_file: ParsedFile = parser.parse(file)
            parsed_document.add_parsed_file(parsed_file)

        logger.info(f"Document successfully parsed: {parsed_document}")
        return parsed_document

    def __repr__(self):
        return f"DocumentParser(extensions_parsers={self.extensions_parsers})"
