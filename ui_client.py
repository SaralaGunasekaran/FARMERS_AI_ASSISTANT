import os
import base64
import requests
import streamlit as st

API_URL = "http://127.0.0.1:8000"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def get_base64_uri(filename):
    """Finds the image even if saved as .jpg, .jpeg, or .png inside assets/ or root."""
    name_no_ext = os.path.splitext(filename)[0]
    for folder in [os.path.join(BASE_DIR, "assets"), BASE_DIR]:
        for ext in ["", ".jpg", ".jpeg", ".png", ".webp"]:
            candidate = os.path.join(folder, (filename if ext == "" else name_no_ext + ext))
            if os.path.exists(candidate):
                actual_ext = os.path.splitext(candidate)[1].lower()
                mime = "image/jpeg" if actual_ext in [".jpg", ".jpeg"] else "image/png"
                with open(candidate, "rb") as f:
                    encoded = base64.b64encode(f.read()).decode("utf-8")
                return f"data:{mime};base64,{encoded}"
    return ""


def load_avatar_html(filename, size=42, border_color="#2E7D32"):
    """Creates a circular avatar <img> tag from your image filename."""
    uri = get_base64_uri(filename)
    return (
        f'<img src="{uri}" '
        f'style="width:{size}px; height:{size}px; border-radius:50%; '
        f'object-fit:cover; border:2px solid {border_color}; flex-shrink:0;" />'
    )


# ---------------------------------------------------------------------
# IMAGE ASSETS
# ---------------------------------------------------------------------
PADDY_BANNER_URI = get_base64_uri("assests//Paddy_Banner.jpg")
HEADER_BOT_IMG = load_avatar_html("assests//Farmer_Bot.png", size=58, border_color="#FFFFFF")
BOT_IMG = load_avatar_html("assests//Farmer_Bot.png", size=38)
USER_IMG = load_avatar_html("assests//farmer1.png", size=38)

st.set_page_config(page_title="VAYAL THOZHAN", page_icon="🌾", layout="wide")

# ---------------------------------------------------------------------
# BILINGUAL UI DICTIONARY (ENGLISH & TAMIL)
# ---------------------------------------------------------------------
UI_TEXT = {
    "English": {
        "title": "VAYAL THOZHAN",
        "slogan": "உழவர்களின் நலனுக்கான அரசுத் திட்டங்கள் — உடனடித் தகவல்கள்!",
        "sidebar_header": "🌾 Upload",
        "uploader_label": "Select one or more PDF files",
        "process_btn": "Process PDFs",
        "warn_no_file": "Please choose at least one PDF file.",
        "spinner_text": "Sending PDFs to FastAPI...",
        "success_msg": "Indexed {count} chunks!",
        "fail_msg": "Upload failed.",
        "conn_err": "Cannot connect to FastAPI! Start `uvicorn api_server:app --reload` first.",
        "timeout_err": "Request timed out after 30s. Check your internet or OpenAI API key.",
        "chat_placeholder": "Ask about eligibility, subsidies, or benefits...",
        "you_label": "You",
    },
    "Tamil": {
        "title": "வயல் தோழன்",
        "slogan": "உழவர்களின் நலனுக்கான அரசுத் திட்டங்கள் — உடனடித் தகவல்கள்!",
        "sidebar_header": "🌾 திட்ட PDF கோப்புகளைப் பதிவேற்றவும்",
        "uploader_label": "ஒன்று அல்லது அதற்கு மேற்பட்ட PDF கோப்புகளைத் தேர்ந்தெடுக்கவும்",
        "process_btn": "PDF-களைச் செயலாக்கு",
        "warn_no_file": "குறைந்தது ஒரு PDF கோப்பையாவது தேர்ந்தெடுக்கவும்.",
        "spinner_text": "PDF கோப்புகள் செயலாக்கப்படுகின்றன...",
        "success_msg": "{count} தகவல் பகுதிகள் வெற்றிகரமாகச் சேர்க்கப்பட்டன!",
        "fail_msg": "பதிவேற்றம் தோல்வியடைந்தது.",
        "conn_err": "FastAPI சேவையகத்துடன் இணைக்க முடியவில்லை! முதலில் uvicorn-ஐ இயக்கவும்.",
        "timeout_err": "30 வினாடிகளுக்கு மேல் நேரம் ஆனது. இணைய இணைப்பு அல்லது API விசையைச் சரிபார்க்கவும்.",
        "chat_placeholder": "திட்டங்கள், மானியங்கள் அல்லது தகுதிகள் பற்றி கேளுங்கள்...",
        "you_label": "நீங்கள்",
    },
}

# Read current language selection before rendering header so the banner translates immediately
current_selection = st.session_state.get("ui_language", "🌐 English")
lang_key = "Tamil" if "தமிழ்" in current_selection else "English"
t = UI_TEXT[lang_key]


def render_message(role, text):
    clean_text = text.replace("\n", "<br>")

    if role == "user":
        st.markdown(
            f"""
            <div style="display:flex; align-items:flex-start; gap:12px; margin-bottom:14px;">
                <div style="background:#2E7D32; color:#FFFFFF; font-weight:700; font-size:0.85rem;
                            padding:6px 14px; border-radius:20px; flex-shrink:0; margin-top:2px;">
                    {t["you_label"]}
                </div>
                <div style="background:#DCEEE2; border:1px solid #A5D6A7; color:#1B4332;
                            border-radius:12px; padding:10px 14px; line-height:1.55; width:100%;">
                    {clean_text}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"""
            <div style="display:flex; align-items:flex-start; gap:12px; margin-bottom:14px;">
                {BOT_IMG}
                <div style="background:#FFFFFF; border:1px solid #CBE2D2; color:#1B2E22;
                            border-radius:12px; padding:10px 14px; line-height:1.55; width:100%;">
                    {clean_text}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
# ---------------------------------------------------------------------
# 1. FULL-SCREEN PERMANENT PADDY FIELD HEADER + ROOMY LANGUAGE SELECTOR
# ---------------------------------------------------------------------
st.markdown(
    """
    <style>
        /* >>> MILD GREEN FULL-SCREEN BACKGROUND <<< */
        .stApp,
        [data-testid="stAppViewContainer"],
        [data-testid="stMain"],
        [data-testid="stBottom"],
        [data-testid="stBottom"] > div {
            background-color: #EBF5EE !important;
        }
        section[data-testid="stSidebar"] {
            background-color: #DFEFE4 !important;
            border-right: 1px solid #C6E0CE !important;
            margin-top: 190px;
            height: calc(100vh - 190px) !important;
        }
        header[data-testid="stHeader"] {
            background: transparent;
            z-index: 1000001;
        }
        section[data-testid="stSidebar"] {
            margin-top: 190px;
            height: calc(100vh - 190px) !important;
        }
        .block-container {
            padding-top: 210px !important;
        }
        .permanent-paddy-header {
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 190px;
            z-index: 999999;
            overflow: hidden;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.18);
        }
        div[data-testid="stElementContainer"]:has(.lang-selector-anchor) + div[data-testid="stElementContainer"] {
            position: fixed !important;
            top: 14px !important;
            right: 20px !important;
            width: 185px !important;
            z-index: 1000005 !important;
            background: rgba(18, 55, 28, 0.82) !important;
            backdrop-filter: blur(6px);
            padding: 4px 10px !important;
            border-radius: 12px !important;
            border: 1px solid rgba(255, 255, 255, 0.35) !important;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.25) !important;
        }
        div[data-testid="stElementContainer"]:has(.lang-selector-anchor) + div[data-testid="stElementContainer"] div[data-baseweb="select"] > div {
            min-height: 48px !important;
            height: 48px !important;
            line-height: 1.8 !important;
            padding: 6px 6px !important;
            font-size: 0.95rem !important;
            background: transparent !important;
            border: none !important;
            color: #FFFFFF !important;
            overflow: visible !important;
        }
        div[data-testid="stElementContainer"]:has(.lang-selector-anchor) + div[data-testid="stElementContainer"] div[data-baseweb="select"] div {
            line-height: 1.8 !important;
            overflow: visible !important;
        }
        [data-testid="stChatInput"],
        [data-testid="stChatInput"] > div {
            background-color: #FFFFFF !important;
            border: 2.5px solid #2E7D32 !important;
            border-radius: 16px !important;
            box-shadow: 0 4px 16px rgba(46, 125, 50, 0.22) !important;
            transition: all 0.2s ease-in-out !important;
        }
        [data-testid="stChatInput"]:focus-within,
        [data-testid="stChatInput"] > div:focus-within {
            border-color: #1B5E20 !important;
            box-shadow: 0 0 0 4px rgba(76, 175, 80, 0.30), 0 6px 22px rgba(27, 94, 32, 0.28) !important;
        }
        [data-testid="stChatInput"] textarea {
            font-size: 1.02rem !important;
            color: #1B2E22 !important;
        }
        [data-testid="stChatInput"] button {
            background-color: #2E7D32 !important;
            color: #FFFFFF !important;
            border-radius: 10px !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

if PADDY_BANNER_URI:
    st.markdown(
        f"""
        <div class="permanent-paddy-header">
            <img src="{PADDY_BANNER_URI}"
                 style="width:100%; height:100%; object-fit:cover; object-position:center 60%; display:block;" />
            <div style="position:absolute; inset:0;
                        background:linear-gradient(to bottom, rgba(0,0,0,0) 35%, rgba(10,35,16,0.82) 100%);
                        display:flex; align-items:flex-end; padding:18px 28px;">
                <div style="display:flex; align-items:center; gap:16px;">
                    {HEADER_BOT_IMG}
                    <div>
                        <h1 style="margin:0; padding:0; color:#FFFFFF; font-size:1.85rem;
                                   text-shadow:1px 2px 6px rgba(0,0,0,0.7);">
                            {t["title"]}
                        </h1>
                        <p style="margin:3px 0 0 0; color:#E8F5E9; font-size:0.98rem;
                                  text-shadow:1px 1px 4px rgba(0,0,0,0.65);">
                            {t["slogan"]}
                        </p>
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# Top-Right Floating Language Selector
st.markdown('<div class="lang-selector-anchor"></div>', unsafe_allow_html=True)
selected_lang = st.selectbox(
    "Language",
    ["🌐 English", "🌐 தமிழ்"],
    key="ui_language",
    label_visibility="collapsed",
)

# ---------------------------------------------------------------------
# 2. SIDEBAR: UPLOAD MULTIPLE PDFs TO FASTAPI (/upload)
# ---------------------------------------------------------------------
with st.sidebar:
    st.header(t["sidebar_header"])
    uploaded_files = st.file_uploader(
      t["uploader_label"],
      type=["pdf", "png", "jpg", "jpeg"],
      accept_multiple_files=True,
  )

    if st.button(t["process_btn"]):
        if not uploaded_files:
            st.warning(t["warn_no_file"])
        else:
            with st.spinner(t["spinner_text"]):
                try:
                    files_payload = [
                      ("files", (f.name, f.getvalue(), f.type or "application/octet-stream"))
                      for f in uploaded_files
                    ]
                    response = requests.post(
                        f"{API_URL}/upload",
                        files=files_payload,
                        timeout=300,
                    )
                    if response.status_code == 200:
                        res = response.json()
                        if res.get("status") == "success":
                            st.success(t["success_msg"].format(count=res["chunks_indexed"]))
                        else:
                            st.error(res.get("message", t["fail_msg"]))
                    else:
                        st.error(f"FastAPI Error ({response.status_code}): {response.text}")
                except requests.exceptions.ConnectionError:
                    st.error(t["conn_err"])
                except requests.exceptions.Timeout:
                    st.error(t["timeout_err"])

# ---------------------------------------------------------------------
# 3. CHAT HISTORY & LIVE STREAMING
# ---------------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    render_message(msg["role"], msg["content"])

if question := st.chat_input(t["chat_placeholder"]):
    st.session_state.messages.append({"role": "user", "content": question})
    render_message("user", question)

    response = requests.post(
        f"{API_URL}/chat",
        json={"question": question, "language": lang_key},
        stream=True,
    )

    placeholder = st.empty()
    reply = ""

    for chunk in response.iter_content(chunk_size=None, decode_unicode=True):
        if chunk:
            reply += chunk
            formatted = reply.replace("\n", "<br>")
            placeholder.markdown(
                f"""
                <div style="display:flex; align-items:flex-start; gap:12px; margin-bottom:14px;">
                    {BOT_IMG}
                    <div style="background:#F8FBF8; border:1px solid #DCE7DC;
                                border-radius:12px; padding:10px 14px; line-height:1.55; width:100%;">
                        {formatted} ▌
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    placeholder.empty()
    render_message("assistant", reply)
    st.session_state.messages.append({"role": "assistant", "content": reply})