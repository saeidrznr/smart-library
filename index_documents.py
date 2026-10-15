from collections import Counter
from pathlib import Path

from app.core.embeddings import embedding_model
from app.rag.chunker import chunk_documents
from app.rag.loader import load_documents
from app.rag.vector_store import VectorStore


PROJECT_ROOT = Path(__file__).resolve().parent
OUTPUT_PATH = PROJECT_ROOT / "outputs" / "chunking_output.txt"


def save_chunks(chunks) -> None:
    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with OUTPUT_PATH.open("w", encoding="utf-8") as file:
        for index, chunk in enumerate(chunks, start=1):
            file.write("=" * 80 + "\n")
            file.write(f"CHUNK {index}/{len(chunks)}\n")
            file.write("=" * 80 + "\n")
            file.write(f"Metadata: {chunk.metadata}\n\n")
            file.write(chunk.page_content)
            file.write("\n\n")


def main() -> None:
    print("Loading PDF documents...")
    documents = load_documents()
    print(f"Loaded pages: {len(documents)}")

    print("\nChunking documents...")
    chunks = chunk_documents(documents)
    print(f"Generated chunks: {len(chunks)}")

    counts = Counter(
        chunk.metadata.get("chunk_type", "unknown")
        for chunk in chunks
    )

    for chunk_type, count in counts.items():
        print(f"  {chunk_type}: {count}")

    print("\nSaving chunking report...")
    save_chunks(chunks)
    print(f"Report saved to: {OUTPUT_PATH}")

    print("\nIndexing chunks into ChromaDB...")
    vector_store = VectorStore(
        embedding_model=embedding_model,
    )
    vector_store.add_documents(chunks)

    print("Indexing completed successfully.")


if __name__ == "__main__":
    main()