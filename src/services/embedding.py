import os

from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings


load_dotenv()


def get_embedding():
    """
    Create and return the HuggingFace embedding model.
    """

    embedding = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    return embedding