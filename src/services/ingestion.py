from pathlib import Path

from src.services.loader import load_pdf
from src.services.splitter import split_documents
from src.services.vectore_store import create_vector_store


def ingest_pdf(
    file_path: str,
    document_id: str,
    original_file_name: str,
):
    """Load one PDF and create its separate vector store."""

    pdf_path = Path(file_path)

    documents = load_pdf(str(pdf_path))

    if not documents:
        raise ValueError("No readable pages were found in this PDF.")

    # Keep the original filename in source citations.
    for document in documents:
        document.metadata["source"] = original_file_name

    chunks = split_documents(documents)

    if not chunks:
        raise ValueError(
            "No extractable text was found in this PDF."
        )

    create_vector_store(
        chunks,
        document_id=document_id,
    )

    return {
        "file_name": original_file_name,
        "pages": len(documents),
        "chunks": len(chunks),
        "message": "PDF successfully ingested.",
    }