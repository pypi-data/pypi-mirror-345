from langchain_openai.embeddings import OpenAIEmbeddings

from ragloader.splitting import DocumentChunk
from ragloader.embedding import ChunkEmbedder, EmbeddedChunk


class OpenAIAda(ChunkEmbedder):
    model_name: str = "text-embedding-ada-002"
    vector_length: int = 1536

    def embed(self, chunk: DocumentChunk) -> EmbeddedChunk:
        embeddings = OpenAIEmbeddings(model=self.model_name)
        embedding: list[float] = embeddings.embed_query(chunk.content)

        embedded_chunk: EmbeddedChunk = EmbeddedChunk(
            document_chunk=chunk, embedding=embedding, embedding_model=self.model_name
        )

        return embedded_chunk
