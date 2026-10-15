from collections import Counter

from app.rag.loader import load_documents
from app.rag.chunker import chunk_documents


def main():
    # 1. Load all PDF documents.
    documents = load_documents()

    print("=" * 80)
    print("LOADED DOCUMENTS")
    print("=" * 80)
    print(f"Pages loaded: {len(documents)}")

    for document in documents:
        print(
            f"Source: {document.metadata.get('source')} | "
            f"Page: {document.metadata.get('page')}"
        )

    # 2. Chunk all documents.
    chunks = chunk_documents(documents)


    print("\n" + "=" * 80)
    print("CHUNKING SUMMARY")
    print("=" * 80)
    print(f"Total chunks: {len(chunks)}")

    type_counts = Counter(
        chunk.metadata.get("chunk_type", "unknown")
        for chunk in chunks
    )

    print("\nChunks by type:")
    for chunk_type, count in type_counts.items():
        print(f"  {chunk_type}: {count}")

    source_counts = Counter(
        chunk.metadata.get("source", "unknown")
        for chunk in chunks
    )

    print("\nChunks by source:")
    for source, count in source_counts.items():
        print(f"  {source}: {count}")

    # 3. Print every chunk with its metadata and content.
    for index, chunk in enumerate(chunks, start=1):
        print("\n" + "=" * 80)
        print(f"CHUNK {index}/{len(chunks)}")
        print("=" * 80)

        print("Metadata:")
        for key, value in chunk.metadata.items():
            print(f"  {key}: {value}")

        print("\nContent:")
        print(chunk.page_content)

    # 4. Save all chunks to a readable text file.
    with open(
        "chunking_output.txt",
        "w",
        encoding="utf-8",
    ) as file:
        for index, chunk in enumerate(chunks, start=1):
            file.write("=" * 80 + "\n")
            file.write(f"CHUNK {index}/{len(chunks)}\n")
            file.write("=" * 80 + "\n")

            file.write(f"Metadata: {chunk.metadata}\n\n")
            file.write(chunk.page_content)
            file.write("\n\n")

    print("\nFull output saved to chunking_output.txt")


if __name__ == "__main__":
    main()