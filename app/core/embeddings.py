from langchain_huggingface import HuggingFaceEmbeddings


embedding_model = HuggingFaceEmbeddings(
    model_name=(
        "sentence-transformers/"
        "paraphrase-multilingual-MiniLM-L12-v2"
    ),
    model_kwargs={
        "device": "cpu",
    },
    encode_kwargs={
        "normalize_embeddings": True,
    },
)
