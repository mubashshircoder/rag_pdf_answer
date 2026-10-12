
from pathlib import Path
from uuid import UUID

from langchain_community.vectorstores import FAISS

from src.services.embedding import get_embedding


VECTOR_STORE_PATH = Path("vectoredb")


def _get_document_store_path(document_id: str) -> Path:
    """Build a safe index path from a valid document UUID."""

    try:
        safe_id = str(UUID(str(document_id)))
    except (ValueError, TypeError, AttributeError) as error:
        raise ValueError("Invalid document ID.") from error

    return VECTOR_STORE_PATH / safe_id


def create_vector_store(documents, document_id: str):
    """Create and save a separate FAISS index for one PDF."""

    if not documents:
        raise ValueError("No document chunks were provided.")

    store_path = _get_document_store_path(document_id)
    store_path.mkdir(parents=True, exist_ok=True)

    embedding = get_embedding()

    vector_store = FAISS.from_documents(
        documents,
        embedding,
    )

    vector_store.save_local(str(store_path))

    return vector_store


def load_vector_store(document_id: str):
    """Load the FAISS index belonging to the selected PDF."""

    store_path = _get_document_store_path(document_id)

    index_file = store_path / "index.faiss"
    metadata_file = store_path / "index.pkl"

    if not index_file.exists() or not metadata_file.exists():
        raise FileNotFoundError(
            "The selected PDF's vector store was not found. "
            "Please upload the PDF again."
        )

    embedding = get_embedding()

    # Load only trusted indexes created by this application.
    vector_store = FAISS.load_local(
        str(store_path),
        embedding,
        allow_dangerous_deserialization=True,
    )

    return vector_store
