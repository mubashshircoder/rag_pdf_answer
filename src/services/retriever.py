from src.services.vectore_store import load_vector_store


def get_retriever(document_id: str):
    """Create a retriever for one selected PDF."""

    vector_store = load_vector_store(document_id)

    return vector_store.as_retriever(
        search_type="mmr",
        search_kwargs={
            "k": 3,
            "fetch_k": 10,
        },
    )