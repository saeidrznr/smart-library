from langchain_core.documents import Document

from app.core.embeddings import embedding_model
from app.rag.vector_store import VectorStore


vector_store = VectorStore(
    embedding_model=embedding_model,
)


def retrieve_documents(
    query: str,
    k: int = 4,
) -> list[Document]:
    """Retrieve the most relevant library document chunks."""
    return vector_store.similarity_search(
        query=query,
        k=k,
    )