import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq


load_dotenv()


def get_llm():
    """
    Create and return the Groq LLM.
    """

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise ValueError(
            "GROQ_API_KEY is missing from the .env file."
        )

    llm = ChatGroq(
        model="openai/gpt-oss-20b",
        temperature=0
    )

    return llm