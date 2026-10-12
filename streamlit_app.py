
import requests
import streamlit as st


# --------------------------------------------------
# 1. Page configuration
# --------------------------------------------------

st.set_page_config(
    page_title="RAG Smart PDF",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)


# --------------------------------------------------
# 2. API configuration
# --------------------------------------------------

DEFAULT_API_URL = "http://127.0.0.1:8000"


# --------------------------------------------------
# 3. Custom styling
# --------------------------------------------------

st.markdown(
    """
    <style>
    .stApp {
        background: #0b1020;
        color: #edf2ff;
    }

    [data-testid="stSidebar"] {
        background: #11182b;
        border-right: 1px solid #26314a;
    }

    .hero {
        padding: 26px;
        border: 1px solid #293654;
        border-radius: 18px;
        background: linear-gradient(
            135deg, #17223d, #101629
        );
        margin-bottom: 22px;
    }

    .hero h1 {
        color: #f4f7ff;
        font-size: 34px;
        margin-bottom: 8px;
    }

    .hero p {
        color: #b5c2df;
        font-size: 15px;
        margin-bottom: 0;
    }

    .section-title {
        color: #e5ebff;
        font-size: 21px;
        font-weight: 700;
        margin: 12px 0;
    }

    div[data-testid="stMetric"] {
        background: #121b30;
        border: 1px solid #293654;
        padding: 15px;
        border-radius: 14px;
    }

    div.stButton > button {
        border-radius: 10px;
        min-height: 42px;
        font-weight: 600;
    }

    div[data-testid="stTextInput"] input,
    div[data-testid="stTextArea"] textarea {
        background: #11182b;
        color: #edf2ff;
        border-radius: 10px;
    }

    .stCaption {
        color: #9eacc9;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# 4. Session state
# --------------------------------------------------

if "api_url" not in st.session_state:
    st.session_state.api_url = DEFAULT_API_URL

if "last_answer" not in st.session_state:
    st.session_state.last_answer = None


# --------------------------------------------------
# 5. Helper functions
# --------------------------------------------------

def get_api_url():
    return st.session_state.api_url.strip().rstrip("/")


def get_documents():
    """Fetch registered PDFs from the FastAPI backend."""

    try:
        response = requests.get(
            f"{get_api_url()}/upload/documents",
            timeout=15,
        )
        response.raise_for_status()

        result = response.json()
        return result.get("documents", []), None

    except requests.RequestException as error:
        return [], str(error)

    except (ValueError, AttributeError):
        return [], "The API returned an invalid response."


def upload_pdf(uploaded_file):
    """Send a PDF to the existing FastAPI endpoint."""

    try:
        response = requests.post(
            f"{get_api_url()}/upload",
            files={
                "file": (
                    uploaded_file.name,
                    uploaded_file.getvalue(),
                    "application/pdf",
                )
            },
            timeout=(10, 300),
        )

        if not response.ok:
            try:
                detail = response.json().get(
                    "detail", response.text
                )
            except ValueError:
                detail = response.text

            return None, str(detail)

        return response.json(), None

    except requests.RequestException as error:
        return None, str(error)


def ask_question(question, document_id):
    """Ask the selected PDF a question."""

    try:
        response = requests.post(
            f"{get_api_url()}/ask",
            json={
                "question": question,
                "document_id": document_id,
            },
            timeout=(10, 180),
        )

        if not response.ok:
            try:
                detail = response.json().get(
                    "detail", response.text
                )
            except ValueError:
                detail = response.text

            return None, str(detail)

        return response.json(), None

    except requests.RequestException as error:
        return None, str(error)


# --------------------------------------------------
# 6. Sidebar
# --------------------------------------------------

with st.sidebar:
    st.markdown("## 📚 RAG Smart PDF")
    st.caption("Your personal document assistant")

    st.divider()

    st.markdown("### ⚙️ Backend settings")

    st.text_input(
        "FastAPI URL",
        key="api_url",
        help="Keep the default URL when running locally.",
    )

    st.caption(
        "Your FastAPI server must be running "
        "before you upload or ask questions."
    )

    if st.button("🔄 Refresh document list", use_container_width=True):
        st.rerun()

    st.divider()

    st.markdown("### 🧠 How it works")
    st.markdown(
        """
        1. Upload a PDF.
        2. Select your document.
        3. Ask a question.
        4. Read the answer and sources.
        """
    )

    st.divider()
    st.caption("Built with Streamlit + FastAPI + FAISS")


# --------------------------------------------------
# 7. Main header
# --------------------------------------------------

st.markdown(
    """
    <div class="hero">
        <h1>Ask your documents.</h1>
        <p>
            Upload a PDF, choose your document, and get
            AI answers grounded in its content.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# 8. Check backend and load documents
# --------------------------------------------------

documents, documents_error = get_documents()

if documents_error:
    st.error(
        "Cannot connect to the document API. "
        "Make sure FastAPI is running at the URL in "
        "the sidebar."
    )
    st.caption(documents_error)

    st.stop()


# --------------------------------------------------
# 9. Dashboard metrics
# --------------------------------------------------

metric_col1, metric_col2, metric_col3 = st.columns(3)

metric_col1.metric(
    "Uploaded PDFs",
    len(documents),
)

metric_col2.metric(
    "Status",
    "Connected",
)

metric_col3.metric(
    "Answer engine",
    "RAG",
)

st.divider()


# --------------------------------------------------
# 10. Upload section
# --------------------------------------------------

left_col, right_col = st.columns(
    [1, 1.5],
    gap="large",
)

with left_col:
    st.markdown(
        '<div class="section-title">📤 Upload a PDF</div>',
        unsafe_allow_html=True,
    )

    uploaded_file = st.file_uploader(
        "Choose a PDF document",
        type=["pdf"],
        help="Maximum supported upload size: 10 MB.",
    )

    if uploaded_file:
        st.caption(
            f"Selected: {uploaded_file.name} "
            f"({uploaded_file.size / 1024:.1f} KB)"
        )

        if uploaded_file.size > 10 * 1024 * 1024:
            st.error("This file exceeds the 10 MB limit.")

        elif st.button(
            "Upload and process PDF",
            type="primary",
            use_container_width=True,
        ):
            with st.spinner(
                "Uploading PDF and creating its vector index..."
            ):
                result, error = upload_pdf(uploaded_file)

            if error:
                st.error(f"Upload failed: {error}")

            else:
                st.success("PDF uploaded successfully!")

                st.markdown(
                    f"**Filename:** {result['file_name']}"
                )
                st.write(f"Pages: {result['pages']}")
                st.write(f"Chunks: {result['chunks']}")

                st.session_state.last_answer = None

                st.info(
                    "Refresh the document list to select "
                    "your newly uploaded PDF."
                )

                st.rerun()


# --------------------------------------------------
# 11. Document selection
# --------------------------------------------------

with right_col:
    st.markdown(
        '<div class="section-title">📁 Your documents</div>',
        unsafe_allow_html=True,
    )

    if not documents:
        st.info(
            "No PDFs found yet. Upload your first PDF "
            "using the panel on the left."
        )

    else:
        document_options = {
            (
                f"{item['file_name']} "
                f"({item['pages']} pages)"
            ): item["document_id"]
            for item in documents
        }

        selected_label = st.selectbox(
            "Choose a PDF to ask questions about",
            options=list(document_options.keys()),
            key="selected_document_label",
        )

        selected_document_id = document_options[
            selected_label
        ]

        selected_document = next(
            item
            for item in documents
            if item["document_id"] == selected_document_id
        )

        st.success(f"Selected: {selected_document['file_name']}")

        info_col1, info_col2 = st.columns(2)

        info_col1.metric(
            "Pages",
            selected_document["pages"],
        )

        info_col2.metric(
            "Text chunks",
            selected_document["chunks"],
        )


# --------------------------------------------------
# 12. Question and answer section
# --------------------------------------------------

st.divider()

st.markdown(
    '<div class="section-title">💬 Ask your PDF</div>',
    unsafe_allow_html=True,
)

if documents:
    with st.form("question_form"):
        question = st.text_area(
            "Your question",
            placeholder=(
                "Example: What are the main topics "
                "covered in this PDF?"
            ),
            max_chars=2000,
            height=100,
        )

        submit_question = st.form_submit_button(
            "✨ Generate answer",
            type="primary",
            use_container_width=True,
        )

    if submit_question:
        if not question.strip():
            st.warning("Please enter a question first.")

        else:
            with st.spinner(
                "Searching your PDF and generating an answer..."
            ):
                result, error = ask_question(
                    question.strip(),
                    selected_document_id,
                )

            if error:
                st.error(f"Question failed: {error}")

            else:
                st.session_state.last_answer = {
                    "question": question.strip(),
                    "document_id": selected_document_id,
                    "result": result,
                }

    # Show the most recent answer only for its selected PDF.
    saved_answer = st.session_state.last_answer

    if (
        saved_answer
        and saved_answer["document_id"] == selected_document_id
    ):
        st.markdown("### 🧠 Answer")

        st.markdown(
            f"**Question:** {saved_answer['question']}"
        )

        st.markdown(saved_answer["result"]["answer"])

        st.markdown("### 📚 Sources")

        sources = saved_answer["result"].get("sources", [])

        if sources:
            for source in sources:
                page = source.get("page")

                if page is not None:
                    st.markdown(
                        f"- **{source['source']}** — "
                        f"Page {page}"
                    )
                else:
                    st.markdown(
                        f"- **{source['source']}**"
                    )
        else:
            st.caption("No source citations were returned.")

else:
    st.info(
        "Upload a PDF first. Then you can select it "
        "and ask questions here."
    )


# --------------------------------------------------
# 13. Footer
# --------------------------------------------------

st.divider()

st.caption(
    "RAG Smart PDF · Answers may be incomplete. "
    "Check the cited pages when accuracy matters."
)
