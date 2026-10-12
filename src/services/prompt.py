from langchain_core.prompts import ChatPromptTemplate


def get_rag_prompt():
    """
    Create and return the RAG prompt.
    """

    prompt = ChatPromptTemplate.from_template(
        """
You are a helpful AI assistant answering questions
based only on the provided context.

Rules:

1. Use only the provided context.
2. Do not invent information.
3. If the answer is not present in the context,
   clearly say that the information is not available
   in the provided documents.
4. Give a clear and concise answer.

Context:
{context}

Question:
{question}

Answer:
"""
    )

    return prompt