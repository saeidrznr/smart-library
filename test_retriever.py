
from app.rag.retriever import retrieve_documents


def main() -> None:
    query = "جریمهٔ دیرکرد روزانه چقدر است؟"

    documents = retrieve_documents(query, k=4)

    print(f"Query: {query}")
    print(f"Retrieved documents: {len(documents)}")

    for index, document in enumerate(documents, start=1):
        print(f"\n{'=' * 60}")
        print(f"Result {index}")
        print(f"Metadata: {document.metadata}")
        print(document.page_content)


if __name__ == "__main__":
    main()
