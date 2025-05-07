import threading
from pathlib import Path
from qdrant_client.models import PointStruct, Record
from concurrent.futures import ThreadPoolExecutor

from ragloader.conf import Config, get_logger
from ragloader.db import QdrantConnector
from ragloader.indexing import DocumentsStructure, FilesIndexer, Document
from ragloader.parsing import DocumentParser, ParsedDocument
from ragloader.classification import DocumentClassifier, ClassifiedDocument
from ragloader.extraction import DocumentExtractor, ExtractedDocument
from ragloader.splitting import DocumentSplitter, ChunkedDocument
from ragloader.embedding import DocumentEmbedder, EmbeddedDocument


class UploadOrchestrator:
    def __init__(
        self,
        data_directory: Path | str,
        config: Config | Path | str | None = None,
        initialize_collections: bool = True,
    ):
        if config is None:
            self.config: Config = Config()
        elif isinstance(config, (str, Path)):
            self.config: Config = Config(Path(config))
        elif isinstance(config, Config):
            self.config: Config = config
        else:
            raise TypeError(f"Invalid type for config: {type(config)}")

        self.logger = get_logger(self.config)

        self.logger.info(f"Config loaded")
        self.logger.debug(f"Config: {self.config}")

        self.data_directory: Path = Path(data_directory)
        self.documents_structure: DocumentsStructure | None = None

        self.lock = threading.Lock()
        self.qdrant: QdrantConnector = QdrantConnector(self.config["db"]["qdrant"])

        self.document_parser: DocumentParser = DocumentParser(self.config)
        self.document_classifier: DocumentClassifier = DocumentClassifier(self.config)
        self.document_extractor: DocumentExtractor = DocumentExtractor(self.config)
        self.document_splitter: DocumentSplitter = DocumentSplitter(self.config)
        self.document_embedder: DocumentEmbedder = DocumentEmbedder(self.config)

        self.stages: list[str] = list(self.config["pipeline_stages"].keys())
        self.collection_names: dict[str, str] = dict().fromkeys(self.stages)
        if initialize_collections:
            self.initialize_collections()
            self.db_state = self.scan_cache()
        else:
            self.logger.warning("Skipping collections initialization, initialize them manually before the upload")

    def initialize_collections(self):
        collections_names_base = [
            "parsed_documents",
            "classified_documents",
            "extracted_documents",
            "chunked_documents",
        ]
        for base_name, stage in zip(collections_names_base, self.stages):
            collection_name = f"{self.config['pipeline_stages'][stage]['label']}__{base_name}"
            self.collection_names[stage] = collection_name
            self.qdrant.create_collection(collection_name, if_exists="ignore")
            self.logger.debug(f"Collection created: {collection_name}")

        embedding_label = self.config["pipeline_stages"]["embedding"]["label"]
        embeddings_collection_name = f"{embedding_label}__embedded_chunks"
        self.collection_names["embedding"] = embeddings_collection_name
        self.qdrant.create_collection(
            embeddings_collection_name,
            vectors_length=self.document_embedder.embedding_model.vector_length,
            if_exists="ignore",
        )
        self.logger.debug(f"Collection created: {embeddings_collection_name}")

        self.logger.info("All collections initialized")

    def scan_cache(self):
        collection_names = self.collection_names.values()
        db_state = {col_name: {} for col_name in collection_names}
        for collection_name in collection_names:
            collection_uuids = self.qdrant.get_ids(collection_name)
            collection_previou_stage_hashes = [
                self.qdrant.get_record_payload_item(collection_name, uuid, "previous_stage_hash")
                for uuid in collection_uuids
            ]

            db_state[collection_name]["uuids"] = collection_uuids
            db_state[collection_name]["previous_stage_hashes"] = collection_previou_stage_hashes

        return db_state

    def upload(self):
        self.index_files()
        self.logger.info(f"Files from {self.data_directory} indexed")

        documents: list[Document] = [
            document for group in self.documents_structure.groups for document in group.documents
        ]
        self.logger.info(f"{len(documents)} documents found. Starting to upload.")
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(self.pipeline, document) for document in documents]
            for future in futures:
                future.result()

    def pipeline(self, document: Document):
        parsed_document: ParsedDocument = self.handle_document_parsing(document)
        classified_document: ClassifiedDocument = self.classify_document(parsed_document)
        extracted_document: ExtractedDocument = self.extract_content(classified_document)
        chunked_document: ChunkedDocument = self.split_document(extracted_document)
        self.embed_document(chunked_document)

    def index_files(self):
        indexer = FilesIndexer(self.data_directory)
        self.documents_structure = indexer.scan()

    def handle_document_parsing(self, document: Document) -> ParsedDocument:
        cache_step = self.config["pipeline_stages"]["parsing"]["cache_step"]
        use_cache = self.config["pipeline_stages"]["parsing"]["use_cache"]
        collection_name = self.collection_names["parsing"]
        uuids = self.db_state[collection_name]["uuids"]
        hashes = self.db_state[collection_name]["previous_stage_hashes"]

        if use_cache and str(document.uuid) in uuids and document.hash == hashes[uuids.index(str(document.uuid))]:
            parsed_document_record: Record = self.qdrant.get_record_by_id(collection_name, str(document.uuid))
            parsed_document: ParsedDocument = ParsedDocument.from_db_record(parsed_document_record)
        else:
            self.logger.info(f"Parsing document: {document.document_name}")
            parsed_document: ParsedDocument = self.document_parser.parse(document)

        if cache_step:
            point = PointStruct(id=str(parsed_document.uuid), vector={}, payload=parsed_document.db_payload)
            with self.lock:
                self.qdrant.add_record(collection_name, point)

        return parsed_document

    def classify_document(self, parsed_document: ParsedDocument) -> ClassifiedDocument:
        classified_document: ClassifiedDocument = self.document_classifier.classify(parsed_document)

        point: PointStruct = PointStruct(
            id=str(classified_document.uuid), vector={}, payload=classified_document.db_payload
        )
        with self.lock:
            self.qdrant.add_record(self.collection_names["classification"], point)

        return classified_document

    def extract_content(self, classified_document: ClassifiedDocument) -> ExtractedDocument:
        extracted_document: ExtractedDocument = self.document_extractor.extract(classified_document)

        point: PointStruct = PointStruct(
            id=str(extracted_document.uuid), vector={}, payload=extracted_document.db_payload
        )
        with self.lock:
            self.qdrant.add_record(self.collection_names["extraction"], point)

        return extracted_document

    def split_document(self, extracted_document: ExtractedDocument) -> ChunkedDocument:
        chunked_document: ChunkedDocument = self.document_splitter.split(extracted_document)

        point: PointStruct = PointStruct(
            id=str(chunked_document.uuid), vector={}, payload=chunked_document.db_payload
        )
        with self.lock:
            self.qdrant.add_record(self.collection_names["splitting"], point)

        return chunked_document

    def embed_document(self, chunked_document: ChunkedDocument):
        embedded_document: EmbeddedDocument = self.document_embedder.embed(chunked_document)

        for embedded_chunk in embedded_document.embedded_chunks:
            point: PointStruct = PointStruct(
                id=str(embedded_chunk.uuid), vector=embedded_chunk.embedding, payload=embedded_chunk.db_payload
            )
            with self.lock:
                self.qdrant.add_record(self.collection_names["embedding"], point)

        return embedded_document
