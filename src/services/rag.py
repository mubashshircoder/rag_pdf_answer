from langchain_core.output_parsers import StrOutputParser

from src.services.document_registry import get_document
from src.services.llm import get_llm
from src.services.prompt import get_rag_prompt
from src.services.retriever import get_retriever


def ask_question(question: str, document_id: str):
    """Answer a question using only the selected PDF's index."""

    # Ensure the selected ID belongs to a registered document.
    get_document(document_id)

    retriever = get_retriever(document_id)
    documents = retriever.invoke(question)

    if not documents:
        return {
            "answer": (
                "I could not find relevant information "
                "in the selected PDF."
            ),
            "sources": [],
        }

    context = "\n\n".join(
        document.page_content
        for document in documents
    )

    prompt = get_rag_prompt()
    llm = get_llm()

    chain = prompt | llm | StrOutputParser()

    answer = chain.invoke(
        {
            "context": context,
            "question": question,
        }
    )

    sources = []
    seen_sources = set()

    for document in documents:
        source = document.metadata.get("source", "Unknown")
        page = document.metadata.get("page")

        # PyPDFLoader normally uses zero-based page metadata.
        if isinstance(page, int):
            page += 1

        source_key = (source, page)

        if source_key in seen_sources:
            continue

        seen_sources.add(source_key)

        sources.append(
            {
                "source": source,
                "page": page,
            }
        )

    return {
        "answer": answer,
        "sources": sources,
    }