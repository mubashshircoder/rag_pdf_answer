from fastapi import FastAPI

from src.routers.upload import router as upload_router
from src.routers.question import router as question_router


app = FastAPI(
    title="RAG Smart PDF",
    description="PDF Question Answering RAG API",
    version="1.0.0"
)


app.include_router(upload_router)
app.include_router(question_router)


@app.get("/")
def root():
    return {
        "message": "RAG Smart PDF API is running."
    }