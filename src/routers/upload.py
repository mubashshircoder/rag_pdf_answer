import logging
import shutil
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, File, HTTPException, UploadFile

from src.services.document_registry import (
    list_documents,
    register_document,
)
from src.services.ingestion import ingest_pdf
from src.services.vectore_store import VECTOR_STORE_PATH


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/upload",
    tags=["Upload"],
)

DATA_PATH = Path("data")
MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10 MB
READ_CHUNK_SIZE = 1024 * 1024  # 1 MB


@router.post("")
async def upload_pdf(file: UploadFile = File(...)):
    """Upload, validate, and ingest one PDF."""

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No file name provided.",
        )

    # Remove any path components supplied in the filename.
    original_file_name = (
        file.filename.replace("\\", "/").rsplit("/", 1)[-1].strip()
    )

    if not original_file_name or original_file_name in {".", ".."}:
        raise HTTPException(
            status_code=400,
            detail="Invalid file name.",
        )

    if not original_file_name.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed.",
        )

    DATA_PATH.mkdir(parents=True, exist_ok=True)

    document_id = str(uuid4())
    file_path = DATA_PATH / f"{document_id}.pdf"
    store_path = VECTOR_STORE_PATH / document_id

    total_size = 0
    header = b""

    try:
        # Stream the upload to disk instead of reading the whole PDF
        # into one large Python bytes object.
        with file_path.open("wb") as output_file:
            while True:
                chunk = await file.read(READ_CHUNK_SIZE)

                if not chunk:
                    break

                total_size += len(chunk)

                if total_size > MAX_UPLOAD_SIZE:
                    raise HTTPException(
                        status_code=413,
                        detail="PDF exceeds the 10 MB upload limit.",
                    )

                if len(header) < 1024:
                    header += chunk[: 1024 - len(header)]

                output_file.write(chunk)

        if total_size == 0:
            raise HTTPException(
                status_code=400,
                detail="The uploaded file is empty.",
            )

        if b"%PDF-" not in header:
            raise HTTPException(
                status_code=400,
                detail="The uploaded file does not appear to be a PDF.",
            )

        result = ingest_pdf(
            file_path=str(file_path),
            document_id=document_id,
            original_file_name=original_file_name,
        )

        document_record = {
            "document_id": document_id,
            "file_name": original_file_name,
            "pages": result["pages"],
            "chunks": result["chunks"],
        }

        register_document(document_record)

        return {
            **document_record,
            "message": result["message"],
        }

    except HTTPException:
        file_path.unlink(missing_ok=True)
        shutil.rmtree(store_path, ignore_errors=True)
        raise

    except ValueError as error:
        file_path.unlink(missing_ok=True)
        shutil.rmtree(store_path, ignore_errors=True)

        raise HTTPException(
            status_code=422,
            detail=str(error),
        ) from error

    except Exception as error:
        file_path.unlink(missing_ok=True)
        shutil.rmtree(store_path, ignore_errors=True)

        logger.exception("PDF ingestion failed.")

        raise HTTPException(
            status_code=500,
            detail="PDF processing failed. Check the server logs.",
        ) from error

    finally:
        await file.close()


@router.get("/documents")
def get_uploaded_documents():
    """List the PDFs available for question-answering."""

    try:
        return {"documents": list_documents()}

    except Exception as error:
        logger.exception("Could not read the document registry.")

        raise HTTPException(
            status_code=500,
            detail="Could not retrieve the uploaded PDF list.",
        ) from error