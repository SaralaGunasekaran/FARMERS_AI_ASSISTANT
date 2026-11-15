import os
import logging
from typing import List
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from dotenv import load_dotenv

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_message_histories import ChatMessageHistory

logging.getLogger("pypdf").setLevel(logging.ERROR)
load_dotenv()

os.makedirs("pdf_documents", exist_ok=True)
app = FastAPI(title="AgriSahayak API")

# Initialize models & memory
embeddings = OpenAIEmbeddings(model="text-embedding-3-small", chunk_size=100)
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, streaming=True)
history = ChatMessageHistory()
db = None


# ---------------------------------------------------------------------
# ENDPOINT 1: RECEIVE MULTIPLE PDFs & BUILD FAISS INDEX
# ---------------------------------------------------------------------
@app.post("/upload")
async def upload_pdfs(files: List[UploadFile] = File(...)):
    global db
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    all_chunks = []

    for file in files:
        save_path = os.path.join("pdf_documents", file.filename)
        with open(save_path, "wb") as f:
            f.write(await file.read())

        pages = PyPDFLoader(save_path).load()
        for p in pages:
            p.metadata["source_file"] = file.filename
            p.metadata["page_number"] = p.metadata.get("page", 0) + 1
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


@app.post("/chat")
def chat(req: ChatRequest):
    if db is None:
        return StreamingResponse(
            iter(["Please upload and process PDFs first."]),
            media_type="text/plain",
        )

    docs = db.similarity_search(req.question, k=3)
    context = "\n\n".join(
        f"[{d.metadata['source_file']} - Page {d.metadata['page_number']}]\n{d.page_content}"
        for d in docs
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", "Answer ONLY using this context. Include the PDF name and page number at the end. If not found, say you couldn't find it.\n\nContext:\n{context}"),
        MessagesPlaceholder("history"),
        ("human", "{question}"),
    ])

    def generate_stream():
        full_reply = ""
        for chunk in (prompt | llm).stream({
            "context": context,
            "history": history.messages[-4:],
            "question": req.question,
        }):
            if chunk.content:
                full_reply += chunk.content
                yield chunk.content

        history.add_user_message(req.question)
        history.add_ai_message(full_reply)

    return StreamingResponse(generate_stream(), media_type="text/plain")