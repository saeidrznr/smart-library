import hashlib

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings

from app.core.config import settings


class VectorStore:
    def __init__(
        self,
        embedding_model: Embeddings,
    ) -> None:
        settings.CHROMA_PERSIST_DIRECTORY.mkdir(
            parents=True,
            exist_ok=True,
        )

        self._store = Chroma(
            collection_name="library_documents",
            embedding_function=embedding_model,
            persist_directory=str(
                settings.CHROMA_PERSIST_DIRECTORY
            ),
        )

    @staticmethod
    def _document_id(document: Document) -> str:
        identity = (
            document.metadata.get("source", "")
            + document.metadata.get("chunk_type", "")
            + document.metadata.get("clause_number", "")
            + document.metadata.get("question_number", "")
            + document.page_content
        )

        return hashlib.sha256(
            identity.encode("utf-8")
        ).hexdigest()

    def add_documents(
        self,
        documents: list[Document],
    ) -> None:
        if not documents:
            return

        ids = [
            self._document_id(document)
            for document in documents
        ]

        self._store.add_documents(
            documents=documents,
            ids=ids,
        )

    def similarity_search(
        self,
        query: str,
        k: int = 4,
    ) -> list[Document]:
        return self._store.similarity_search(
            query=query,
            k=k,
        )