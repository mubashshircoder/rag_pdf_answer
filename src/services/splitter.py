from langchain_text_splitters import RecursiveCharacterTextSplitter


def get_splitter():
    """
    Create and return the text splitter.
    """

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    return splitter


def split_documents(documents):
    """
    Split documents into smaller chunks.
    """

    splitter = get_splitter()

    chunks = splitter.split_documents(documents)

    return chunks