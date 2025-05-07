import logging

from ragloader.conf import Config
from ragloader.extraction import ExtractedDocument
from ragloader.splitting import BaseTextSplitter, ChunkedDocument
from ragloader.splitting.mapper import TextSplittersMapper


logger = logging.getLogger("logger")


class DocumentSplitter:
    """Class for splitting a document into chunks."""

    def __init__(self, config: Config):
        self.default_splitters: dict = config["pipeline_stages"]["splitting"]["splitters"]
        self.splitters_params: dict = config["pipeline_stages"]["splitting"]["splitters_params"]

        logger.info("DocumentSplitter initialized.")
        logger.debug(f"DocumentSplitter default splitters: {self.default_splitters}.")
        logger.debug(f"DocumentSplitter splitters params: {self.splitters_params}.")

    def split(self, extracted_document: ExtractedDocument) -> ChunkedDocument:
        """Splits a document into chunks based on its class and schema."""
        chunked_document: ChunkedDocument = ChunkedDocument(extracted_document)
        splitter_name: str | None = self.default_splitters.get(extracted_document.document_class)

        if not splitter_name:
            raise ValueError(f"No default splitter was specified for the class {extracted_document.document_class}")

        splitter_params: dict = self.splitters_params.get(splitter_name, {})
        try:
            splitter_class: type = TextSplittersMapper.__getitem__(splitter_name).value
        except KeyError:
            logger.error(f"Tried to access '{splitter_name}' splitter which is not yet implemented")
            raise NotImplementedError(f"Splitter {splitter_name} is not yet implemented")
        splitter: BaseTextSplitter = splitter_class(**splitter_params)

        chunks: list[str] = splitter.split(extracted_document.document_content)
        for chunk in chunks:
            chunked_document.add_chunk(chunk)

        logger.info(f"Document successfully chunked: {chunked_document}")
        return chunked_document

    def __repr__(self):
        return f"DocumentSplitter({self.default_splitters})"

