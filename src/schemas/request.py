from uuid import UUID

from pydantic import BaseModel, Field


class QuestionRequest(BaseModel):
    question: str = Field(
        min_length=1,
        max_length=2000,
        description="The question to ask about the selected PDF.",
    )

    document_id: UUID = Field(
        description="The unique ID returned when the PDF was uploaded.",
    )