import requests
import streamlit as st

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Vayal Thozhan", page_icon="🌾", layout="wide")
st.title("🌾 Vayal Thozhan")

# ---------------------------------------------------------------------
# 1. SIDEBAR: SEND MULTIPLE PDFs TO FASTAPI (/upload)
# ---------------------------------------------------------------------
with st.sidebar:
    st.header("📄 Upload")
    uploaded_files = st.file_uploader(
        "Select one or more PDF files",
        type=["pdf"],
        accept_multiple_files=True,
    )

    if st.button("Process PDFs"):
        if not uploaded_files:
            st.warning("Please choose at least one PDF file.")
        else:
            with st.spinner("Sending PDFs to FastAPI..."):
                files_payload = [
                    ("files", (f.name, f.getvalue(), "application/pdf"))
                    for f in uploaded_files
                ]
                res = requests.post(f"{API_URL}/upload", files=files_payload).json()

                if res.get("status") == "success":
                    st.success(f"Indexed {res['chunks_indexed']} chunks!")
                else:
                    st.error(res.get("message", "Upload failed."))

# ---------------------------------------------------------------------
# 2. MAIN AREA: SEND QUESTION TO FASTAPI (/chat) & STREAM REPLY
# ---------------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if question := st.chat_input("Ask about eligibility, subsidies, or benefits..."):
    st.session_state.messages.append({"role": "user", "content": question})
    st.chat_message("user").write(question)

    response = requests.post(
        f"{API_URL}/chat",
        json={"question": question},
        stream=True,
    )

    with st.chat_message("assistant"):
        reply = st.write_stream(
            response.iter_content(chunk_size=None, decode_unicode=True)
        )

    st.session_state.messages.append({"role": "assistant", "content": reply})