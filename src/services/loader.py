from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader


def load_pdf(file_path: str):
    """
    Load one PDF file and return LangChain Document objects.
    """

    pdf_path = Path(file_path)

    if not pdf_path.exists():
        raise FileNotFoundError(
            f"PDF file not found: {pdf_path}"
        )

    if pdf_path.suffix.lower() != ".pdf":
        raise ValueError(
            "The provided file is not a PDF."
        )

    loader = PyPDFLoader(str(pdf_path))

    documents = loader.load()

    return documents


def get_pdf_files(data_path: str):
    """
    Find all PDF files inside the data folder.
    """

    folder = Path(data_path)

    if not folder.exists():
        raise FileNotFoundError(
            f"Data folder not found: {folder}"
        )

    pdf_files = list(folder.glob("*.pdf"))

    return pdf_files


def load_all_pdf(data_path: str):
    """
    Load all PDF files from the data folder.
    """

    pdf_files = get_pdf_files(data_path)

    all_documents = []

    for pdf_file in pdf_files:
        documents = load_pdf(str(pdf_file))
        all_documents.extend(documents)

    return all_documents