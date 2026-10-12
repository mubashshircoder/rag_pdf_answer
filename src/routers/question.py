import logging

from fastapi import APIRouter, HTTPException

from src.schemas.request import QuestionRequest
from src.schemas.response import QuestionResponse
from src.services.rag import ask_question


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/ask",
    tags=["Question"],
)


@router.post("", response_model=QuestionResponse)
def question_answer(request: QuestionRequest):
    """Answer a question using the selected PDF."""

    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty.",
        )

    try:
        return ask_question(
            question=question,
            document_id=str(request.document_id),
        )

    except FileNotFoundError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        ) from error

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    except Exception as error:
        logger.exception("Question answering failed.")

        raise HTTPException(
            status_code=500,
            detail="Question answering failed. Check the server logs.",
        ) from error