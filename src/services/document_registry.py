import json
from pathlib import Path
from uuid import UUID


DATA_PATH = Path("data")
REGISTRY_PATH = DATA_PATH / "documents.json"


def _validate_document_id(document_id: str) -> str:
    """Validate and normalize a document UUID."""

    try:
        return str(UUID(str(document_id)))
    except (ValueError, TypeError, AttributeError) as error:
        raise ValueError("Invalid document ID.") from error


def list_documents() -> list[dict]:
    """Return metadata for all registered PDFs."""

    if not REGISTRY_PATH.exists():
        return []

    with REGISTRY_PATH.open("r", encoding="utf-8") as file:
        documents = json.load(file)

    if not isinstance(documents, list):
        raise ValueError("The document registry has an invalid format.")

    return documents


def get_document(document_id: str) -> dict:
    """Find one registered document by its unique ID."""

    safe_id = _validate_document_id(document_id)

    for document in list_documents():
        if document.get("document_id") == safe_id:
            return document

    raise FileNotFoundError("The selected PDF was not found.")


def register_document(document: dict) -> None:
    """Save document metadata without losing existing entries."""

    safe_id = _validate_document_id(document["document_id"])
    documents = list_documents()

    documents = [
        item
        for item in documents
        if item.get("document_id") != safe_id
    ]

    new_document = {
        "document_id": safe_id,
        "file_name": document["file_name"],
        "pages": document["pages"],
        "chunks": document["chunks"],
    }

    documents.append(new_document)

    DATA_PATH.mkdir(parents=True, exist_ok=True)

    temporary_path = REGISTRY_PATH.with_suffix(".tmp")

    with temporary_path.open("w", encoding="utf-8") as file:
        json.dump(documents, file, indent=2, ensure_ascii=False)

    temporary_path.replace(REGISTRY_PATH)