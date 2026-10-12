from pydantic import BaseModel


class Source(BaseModel):
    source: str
    page: int | None = None


class QuestionResponse(BaseModel):
    answer: str
    sources: list[Source]