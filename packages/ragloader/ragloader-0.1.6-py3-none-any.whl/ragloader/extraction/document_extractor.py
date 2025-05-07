import logging

from ragloader.conf import Config
from ragloader.classification import ClassifiedDocument
from ragloader.extraction import ExtractedDocument


logger = logging.getLogger("logger")


class DocumentExtractor:
    def __init__(self, config: Config):
        # TODO set extraction config
        logger.info("DocumentExtractor initialized.")

    def extract(self, classified_document: ClassifiedDocument) -> ExtractedDocument:
        extracted_document: ExtractedDocument = ExtractedDocument(classified_document)

        extracted_document.document_class = classified_document.document_class
        # TODO implement extracting the structure
        document_structure = {}
        extracted_document.set_document_structure(document_structure)

        logger.info(f"Document successfully extracted: {extracted_document}")
        return extracted_document

    def __repr__(self):
        return "DocumentExtractor()"
