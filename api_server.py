import os
import base64
import pymupdf
from typing import List
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from dotenv import load_dotenv

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.messages import HumanMessage

load_dotenv()

os.makedirs("pdf_documents", exist_ok=True)
app = FastAPI(title="VAYAL THOZHAN API")

# Batch 1,000 chunks per OpenAI API call for much faster indexing
embeddings = OpenAIEmbeddings(model="text-embedding-3-small", chunk_size=1000)
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, streaming=True)
vision_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
history = ChatMessageHistory()

# Auto-load previously indexed PDFs if faiss_index already exists on disk
if os.path.exists("faiss_index"):
    db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
else:
    db = None



def read_scanned_image_with_vision(image_bytes: bytes, mime_type: str = "image/png") -> str:
    b64_img = base64.b64encode(image_bytes).decode("utf-8")
    msg = HumanMessage(
        content=[
            {
                "type": "text",
                "text": (
                    "Read and transcribe ALL content, tables, eligibility criteria, subsidy amounts, "
                    "and scheme details from this agricultural document image. Preserve English and Tamil "
                    "text accurately. Return only the extracted content without extra commentary."
                ),
            },
            {
                "type": "image_url",
                "image_url": {"url": f"data:{mime_type};base64,{b64_img}"},
            },
        ]
    )
    return vision_llm.invoke([msg]).content.strip()

# ---------------------------------------------------------------------
# ENDPOINT 1: FAST PDF EXTRACTION (PyMuPDF) & FAISS INDEXING
# ---------------------------------------------------------------------
@app.post("/upload")
async def upload_pdfs(files: List[UploadFile] = File(...)):
    global db
    splitter = RecursiveCharacterTextSplitter(chunk_size=1200, chunk_overlap=150)
    all_chunks = []

    for file in files:
        save_path = os.path.join("pdf_documents", file.filename)
        file_bytes = await file.read()
        with open(save_path, "wb") as f:
            f.write(file_bytes)

        # Extract all pages in milliseconds using PyMuPDF
        ext = os.path.splitext(file.filename)[1].lower()
        pages = []

        if ext in [".png", ".jpg", ".jpeg", ".webp"]:
            mime = "image/jpeg" if ext in [".jpg", ".jpeg"] else "image/png"
            content = read_scanned_image_with_vision(file_bytes, mime)
            if content:
                pages.append(
                    Document(
                        page_content=content,
                        metadata={"source_file": file.filename, "page_number": 1},
                    )
                )
        elif ext == ".pdf":
            doc = pymupdf.open(stream=file_bytes, filetype="pdf")
            for i, page in enumerate(doc):
                text = page.get_text("text").strip()
                if len(text) < 30:
                    pix = page.get_pixmap(dpi=150)
                    text = read_scanned_image_with_vision(pix.tobytes("png"), "image/png")
                if text:
                    pages.append(
                        Document(
                            page_content=text,
                            metadata={"source_file": file.filename, "page_number": i + 1},
                    )
                )
        all_chunks.extend(splitter.split_documents(pages))

    if not all_chunks:
        return {"status": "error", "message": "No readable text found in PDFs."}

    if db is None:
        db = FAISS.from_documents(all_chunks, embeddings)
    else:
        db.add_documents(all_chunks)

    db.save_local("faiss_index")
    return {"status": "success", "chunks_indexed": len(all_chunks)}


# ---------------------------------------------------------------------
# ENDPOINT 2: RECEIVE QUESTION & STREAM ANSWER BACK
# ---------------------------------------------------------------------
class ChatRequest(BaseModel):
    question: str
    language: str = "English"


@app.post("/chat")
def chat(req: ChatRequest):
    if db is None:
        msg = (
            "முதலில் திட்ட PDF கோப்புகளைப் பதிவேற்றிச் செயலாக்கவும்."
            if req.language == "Tamil"
            else "Please upload and process PDFs first."
        )
        return StreamingResponse(iter([msg]), media_type="text/plain")

    docs = db.similarity_search(req.question, k=3)
    context = "\n\n".join(
        f"[{d.metadata['source_file']} - Page {d.metadata['page_number']}]\n{d.page_content}"
        for d in docs
    )

    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "Answer ONLY using this context. You MUST write your entire response in {language} "
            "(if {language} is Tamil, translate the scheme details accurately into clear, natural Tamil). "
            "Include the PDF name and page number at the end. If not found in the context, say so in {language}.\n\n"
            "Context:\n{context}",
        ),
        MessagesPlaceholder("history"),
        ("human", "{question}"),
    ])

    def generate_stream():
        full_reply = ""
        for chunk in (prompt | llm).stream({
            "context": context,
            "history": history.messages[-4:],
            "question": req.question,
            "language": req.language,
        }):
            if chunk.content:
                full_reply += chunk.content
                yield chunk.content

        history.add_user_message(req.question)
        history.add_ai_message(full_reply)

    return StreamingResponse(generate_stream(), media_type="text/plain")