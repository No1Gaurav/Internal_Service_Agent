import sys
from pathlib import Path

import streamlit as st


# ---------------------------------------------------------
# Backend path
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
BACKEND_DIR = PROJECT_ROOT / "Backend"

sys.path.insert(0, str(BACKEND_DIR))


from config import KNOWLEDGE_BASE_DIR, VECTOR_STORE_DIR
from rag import RAGSystem
from agent import ITSupportAgent
from llm import generate_response


# ---------------------------------------------------------
# Page configuration
# ---------------------------------------------------------

st.set_page_config(
    page_title="Veridian IT Assistant",
    page_icon="🛡️",
    layout="centered",
    initial_sidebar_state="collapsed"
)


# ---------------------------------------------------------
# Custom CSS
# ---------------------------------------------------------

st.markdown(
    """
    <style>

    .stApp {
        background-color: #0f1117;
    }

    .chat-header {
        padding: 1.2rem 0 1rem 0;
        border-bottom: 1px solid #292d36;
        margin-bottom: 1.5rem;
    }

    .chat-title {
        font-size: 1.7rem;
        font-weight: 700;
        margin: 0;
    }

    .chat-subtitle {
        color: #8b93a1;
        font-size: 0.9rem;
        margin-top: 0.25rem;
    }

    .online {
        color: #4ade80;
        font-size: 0.8rem;
        float: right;
        margin-top: 0.4rem;
    }

    .welcome {
        text-align: center;
        padding: 3rem 1rem 2rem 1rem;
        color: #d1d5db;
    }

    .welcome-icon {
        font-size: 3rem;
        margin-bottom: 0.8rem;
    }

    .welcome h2 {
        margin-bottom: 0.5rem;
    }

    .welcome p {
        color: #8b93a1;
    }

    .user-bubble {
        background-color: #2563eb;
        border-radius: 14px;
        padding: 0.9rem 1.1rem;
        margin: 0.5rem 0 1rem auto;
        max-width: 85%;
        line-height: 1.5;
        overflow-wrap: anywhere;
    }

    .assistant-label {
        font-size: 0.75rem;
        color: #8b93a1;
        margin-bottom: 0.35rem;
    }

    .source-card {
        background-color: #171a21;
        border: 1px solid #292d36;
        border-radius: 8px;
        padding: 0.55rem 0.75rem;
        margin: 0.3rem 0;
        font-size: 0.82rem;
    }

    .request-info {
        background-color: #171a21;
        border: 1px solid #292d36;
        border-radius: 8px;
        padding: 0.6rem 0.9rem;
        margin-bottom: 1rem;
        color: #aeb6c3;
        font-size: 0.85rem;
    }

    .block-container {
        max-width: 850px;
        padding-top: 1rem;
        padding-bottom: 2rem;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ---------------------------------------------------------
# Initialize RAG once
# ---------------------------------------------------------

@st.cache_resource
def initialize_rag():

    rag = RAGSystem(
        KNOWLEDGE_BASE_DIR,
        VECTOR_STORE_DIR
    )

    rag.initialize()

    return rag


rag = initialize_rag()


# ---------------------------------------------------------
# Initialize Agent
# ---------------------------------------------------------

if "agent" not in st.session_state:

    st.session_state.agent = ITSupportAgent(
        PROJECT_ROOT / "outputs"
    )

agent = st.session_state.agent


# ---------------------------------------------------------
# Chat history
# ---------------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []


# ---------------------------------------------------------
# Employee name / request initialization
# ---------------------------------------------------------

if not agent.is_session_active():

    st.markdown(
        """
        <div class="welcome">
            <div class="welcome-icon">🛡️</div>
            <h2>Welcome to Veridian IT Assistant</h2>
            <p>
                I'm your internal IT support assistant.
                Please enter your name to begin.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    employee_name = st.text_input(
    "Employee Name",
    placeholder="Enter your name"
)

    employee_email = st.text_input(
        "Employee Email",
        placeholder="name@company.example"
    )


    if st.button(
        "Start Support Request",
        type="primary"
    ):

        if not employee_name.strip():

            st.warning(
                "Please enter your name."
            )

        elif not employee_email.strip():

            st.warning(
                "Please enter your email address."
            )

        else:

            request_id = agent.start_session(
                employee_name,
                employee_email
            )

            st.session_state.messages = [
                {
                    "role": "assistant",
                    "content": (
                        f"Hello **{employee_name.strip()}** 👋\n\n"
                        f"Your request ID is **{request_id}**.\n\n"
                        "How can I help you today?"
                    )
                }
            ]

            st.rerun()


# ---------------------------------------------------------
# Header
# ---------------------------------------------------------

st.markdown(
    """
    <div class="chat-header">

        <span class="chat-title">
            🛡️ Veridian IT Assistant
        </span>

        <span class="online">
            ● Online
        </span>

        <div class="chat-subtitle">
            Internal IT Support Agent
        </div>

    </div>
    """,
    unsafe_allow_html=True
)

# ---------------------------------------------------------
# Request information
# ---------------------------------------------------------

st.markdown(
    f"""
    <div class="request-info">
        👤 <b>{agent.employee}</b>
        &nbsp;&nbsp;|&nbsp;&nbsp;
        🆔 <b>{agent.request.request_id}</b>
    </div>
    """,
    unsafe_allow_html=True
)


# ---------------------------------------------------------
# Display conversation
# ---------------------------------------------------------

for message in st.session_state.messages:

    if message["role"] == "user":

        with st.chat_message("user"):
            st.markdown(message["content"])

    else:

        with st.chat_message("assistant"):

            st.markdown(
            message["content"]
            )

            if message.get("sources"):

                with st.expander(
                    "View knowledge sources"
                ):

                    for source in message["sources"]:

                        st.markdown(
                            f"""
                            <div class="source-card">
                                📄 <b>{source["source"]}</b>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )


# ---------------------------------------------------------
# Chat input
# ---------------------------------------------------------

user_input = st.chat_input(
    "Describe your IT issue..."
)


# ---------------------------------------------------------
# Process request
# ---------------------------------------------------------

if user_input:

    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    agent.add_message("user", user_input)

    if not agent.request.request:
        agent.set_initial_request(user_input)

    with st.spinner("IT Assistant is thinking..."):

        # ------------------------------------------------
        # 1. Continue an existing workflow
        # ------------------------------------------------

        if agent.workflow == "printer":

            answer = agent.handle_printer_workflow(user_input)
            results = []

        # ------------------------------------------------
        # 2. Detect a new workflow
        # ------------------------------------------------

        else:

            workflow = agent.detect_workflow(user_input)

            if workflow == "printer":

                agent.start_printer_workflow()

                answer = agent.handle_printer_workflow(
                    user_input
                )

                results = rag.search(
                    user_input,
                    top_k=3
                )

            # --------------------------------------------
            # 3. Normal RAG conversation
            # --------------------------------------------

            else:

                results = rag.search(
                    user_input,
                    top_k=3
                )

                answer = generate_response(
                    user_input,
                    results,
                    agent.conversation_history
                )

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "sources": results
    })

    agent.add_message(
        "assistant",
        answer
    )

    st.rerun()