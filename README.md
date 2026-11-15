# 🌾 Vayal Thozhan (வயல் தோழன்) – Bilingual Agricultural Scheme AI Assistant

**Vayal Thozhan** (*Field Companion*) is a local, bilingual (**English & தமிழ்**) Retrieval-Augmented Generation (RAG) web application built to help farmers and agricultural officers query government agricultural schemes, eligibility rules, and subsidy Government Orders (GOs) from both digital and scanned PDFs or document images.

---

## ✨ Key Features

- **Hybrid Document & Scanned GO Ingestion:**
  - Extracts selectable text directly from digital PDFs using **PyMuPDF (`pymupdf`)**.
  - Automatically detects scanned PDF pages and uploaded scheme images (`.png`, `.jpg`, `.jpeg`, `.webp`) and transcribes English and Tamil content using **GPT-4o-mini Vision**—with zero heavy local OCR binary dependencies.
- **Bilingual Interface & Responses (English / தமிழ்):**
  - Top-right floating language switcher dynamically translates the entire UI and instructs the LLM to respond in clear, natural **English** or **Tamil** with exact source file and page citations.
- **Farmer-Friendly Custom UI:**
  - Full-width permanent paddy field header banner with a custom **Vayal Thozhan** farmer mascot avatar.
  - Mild agricultural green theme (`#EBF5EE`), fixed static upload sidebar, clean `"You"` / `"நீங்கள்"` user message badges, and a highlighted green-bordered chat input box.
- **Fast Local Vector Search & Streaming Answers:**
  - Indexes document chunks locally using **OpenAI `text-embedding-3-small`** and **FAISS**, streaming answers in real time via **FastAPI** and **Streamlit**.

---

## 🛠️ Tech Stack

- **Backend:** FastAPI, Uvicorn, Python 3.12
- **Frontend:** Streamlit (with custom CSS & base64 asset embedding)
- **AI & RAG Pipeline:** LangChain, OpenAI (`gpt-4o-mini` & `text-embedding-3-small`), FAISS (`faiss-cpu`)
- **PDF & Image Handling:** PyMuPDF (`pymupdf`)

---

## 📂 Project Structure

```text
UZHAVAN_AI_ASSISTANT/
├── assets/
│   ├── paddy_banner.jpg      # Top header paddy field banner image
│   └── agri_bot.png          # Vayal Thozhan farmer mascot avatar
├── pdf_documents/            # Uploaded scheme PDFs and images (auto-created)
├── faiss_index/              # Persistent local FAISS vector store (auto-created)
├── api_server.py             # FastAPI backend (/upload & /chat endpoints)
├── ui_client.py              # Streamlit bilingual frontend UI
├── .env                      # Environment variables (OPENAI_API_KEY)
└── README.md                 # Project documentation


How to Use
Upload Documents: In the left sidebar, select one or more scheme files (.pdf, .png, .jpg, .jpeg) and click Process Files (கோப்புகளைச் செயலாக்கு).

Choose Language: Use the top-right pill selector to switch between 🌐 English and 🌐 தமிழ்.

Ask Questions: Type your question in the highlighted bottom chat box (e.g., "What is the subsidy amount and eligibility criteria under this scheme?") to receive a streamed, source-cited answer.
