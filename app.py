import streamlit as st
import time
import re
import html
from datetime import datetime
from similarity import CoretaxChatbot

DATASET_PATH = "data/dataset_csv.xlsx"
THRESHOLD = 0.50
BOT_NAME = "Cora"
LOGO_PATH = "assets/logo_djp.png"
SUGGESTED_QUESTIONS = [
    "Cara login Coretax kalau lupa password",
    "Cara bikin kode billing pajak",
    "Apa itu PKP dan syaratnya?",
    "Batas waktu lapor SPT tahunan",
]

st.set_page_config(
    page_title=f"{BOT_NAME} - Asisten Coretax",
    page_icon="🏛️",
    layout="centered",
    initial_sidebar_state="expanded",
)

def get_greeting() -> str:
    hour = datetime.now().hour
    if 4 <= hour < 11: return "Selamat pagi"
    if 11 <= hour < 15: return "Selamat siang"
    if 15 <= hour < 19: return "Selamat sore"
    return "Selamat malam"

def new_chat():
    session_id = datetime.now().strftime("%Y%m%d%H%M%S%f")
    st.session_state.sessions[session_id] = {"title": "Percakapan baru", "messages": []}
    st.session_state.active_session = session_id

def get_active_messages():
    if st.session_state.active_session is None:
        new_chat()
    return st.session_state.sessions[st.session_state.active_session]["messages"]

def maybe_update_title(session_id, first_message):
    sess = st.session_state.sessions[session_id]
    if sess["title"] == "Percakapan baru":
        title = first_message.strip()
        if len(title) > 32:
            title = title[:32].rsplit(" ", 1)[0] + "..."
        sess["title"] = title

def linkify_html(text: str) -> str:
    escaped = html.escape(text)
    url_pattern = r'(https?://[^\s\)]+|(?:www\.)?[a-zA-Z0-9-]+\.(?:go\.id|pajak\.go\.id|co\.id|com)(?:/[^\s]*)?)'

    def _wrap(match):
        raw = match.group(0)
        href = raw if raw.startswith("http") else f"https://{raw}"
        return f'<a href="{href}" target="_blank" rel="noopener">{raw}</a>'

    return re.sub(url_pattern, _wrap, escaped)

def user_bubble_html(text: str) -> str:
    return f"""
    <div style="display:flex; justify-content:flex-end; margin:6px 0;">
        <div style="background:#6D5BD0; color:#FFFFFF; padding:12px 16px;
                    border-radius:18px 18px 4px 18px; max-width:78%;
                    font-size:15px; line-height:1.5; word-wrap:break-word;">
            {html.escape(text)}
        </div>
    </div>
    """

def bot_bubble_html(inner_html: str) -> str:
    return f"""
    <div style="display:flex; justify-content:flex-start; margin:6px 0;">
        <div style="background:#FFFFFF; border:1px solid #E9E4FB; color:#1F2430;
                    padding:12px 16px; border-radius:18px 18px 18px 4px; max-width:82%;
                    font-size:15px; line-height:1.5; word-wrap:break-word;
                    box-shadow:0 2px 10px rgba(109,91,208,0.06);">
            {inner_html}
        </div>
    </div>
    """

TYPING_DOTS_HTML = """
<div class="typing-bubble"><span></span><span></span><span></span></div>
"""

def stream_bot_answer(placeholder, answer_html: str, delay: float = 0.015):
    words = re.split(r"(\s+)", answer_html)
    buffer = ""
    for w in words:
        buffer += w
        placeholder.markdown(bot_bubble_html(buffer + " ▌"), unsafe_allow_html=True)
        time.sleep(delay)
    placeholder.markdown(bot_bubble_html(buffer), unsafe_allow_html=True)

@st.cache_resource
def load_bot():
    return CoretaxChatbot(dataset_path=DATASET_PATH, threshold=THRESHOLD)

bot = None
with st.spinner("Menyiapkan Cora... (proses pertama kali bisa memakan waktu 1-3 menit, mohon jangan ditutup)"):
    bot = load_bot()
if "sessions" not in st.session_state: st.session_state.sessions = {}
if "active_session" not in st.session_state: st.session_state.active_session = None

st.markdown("""
<style>
.stApp {
    background: linear-gradient(180deg, #F5F3FF 0%, #F7F9FC 100%);
}
.hero-wrap {
    padding: 60px 20px 30px 20px;
    text-align: center;
}
.hero-badge {
    width: 84px; height: 84px;
    margin: 0 auto 14px auto;
    border-radius: 50%;
    background: radial-gradient(circle at 30% 30%, #F5A9E0, #A78BFA 45%, #6D5BD0 100%);
    box-shadow: 0 8px 24px rgba(109, 91, 208, 0.35);
    display: flex; align-items: center; justify-content: center;
    font-size: 34px; font-weight: 700; color: #FFFFFF;
    font-family: -apple-system, "Segoe UI", sans-serif;
}
.hero-wrap h1 {
    font-size: 26px;
    margin-bottom: 4px;
    background: linear-gradient(90deg, #6D5BD0, #A855F7);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.hero-wrap p { color: #6B7280; font-size: 14px; }
section[data-testid="stSidebar"] {
    background-color: #FFFFFF;
    border-right: 1px solid #EDE9FE;
}
.typing-bubble {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 2px 0;
}
.typing-bubble span {
    width: 7px; height: 7px;
    border-radius: 50%;
    background: #A78BFA;
    animation: typing-bounce 1.1s infinite ease-in-out;
}
.typing-bubble span:nth-child(2) { animation-delay: 0.15s; }
.typing-bubble span:nth-child(3) { animation-delay: 0.3s; }
@keyframes typing-bounce {
    0%, 60%, 100% { transform: translateY(0); opacity: 0.5; }
    30% { transform: translateY(-6px); opacity: 1; }
}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    logo_col, name_col = st.columns([1, 3])
    with logo_col:
        st.image(LOGO_PATH, width=42)
    with name_col:
        st.markdown(f"### {BOT_NAME}")
        st.caption("Asisten Coretax DJP")

    if st.button("➕ Percakapan Baru", use_container_width=True, type="primary"):
        new_chat()
        st.rerun()

    st.markdown("---")
    st.caption("RIWAYAT PERCAKAPAN")

    if len(st.session_state.sessions) == 0:
        st.caption("Belum ada percakapan.")
    else:
        for sid, sess in reversed(list(st.session_state.sessions.items())):
            is_active = sid == st.session_state.active_session
            if st.button(
                sess["title"],
                key=f"hist_{sid}",
                use_container_width=True,
                type="primary" if is_active else "secondary",
            ):
                st.session_state.active_session = sid
                st.rerun()

messages = get_active_messages()

if len(messages) == 0:
    st.markdown(f"""
        <div class="hero-wrap">
            <div class="hero-badge">{BOT_NAME[0]}</div>
            <h1>👋 {get_greeting()}, Wajib Pajak!</h1>
            <p>Tanyakan seputar Coretax di sini.</p>
        </div>
    """, unsafe_allow_html=True)

    cols = st.columns(2)
    for i, q in enumerate(SUGGESTED_QUESTIONS):
        with cols[i % 2]:
            if st.button(q, key=f"chip_{i}", use_container_width=True):
                st.session_state.pending_question = q
                st.rerun()

for msg in messages:
    if msg["role"] == "user":
        st.markdown(user_bubble_html(msg["content"]), unsafe_allow_html=True)
    else:
        st.markdown(bot_bubble_html(msg["content"]), unsafe_allow_html=True)

typed_input = st.chat_input("Tulis pertanyaan kamu di sini...")
user_input = st.session_state.pop("pending_question", None) or typed_input

if user_input:
    messages.append({"role": "user", "content": user_input})
    maybe_update_title(st.session_state.active_session, user_input)

    st.markdown(user_bubble_html(user_input), unsafe_allow_html=True)

    placeholder = st.empty()
    placeholder.markdown(bot_bubble_html(TYPING_DOTS_HTML), unsafe_allow_html=True)
    time.sleep(0.6)

    try:
        hasil = bot.get_response(user_input)
        answer_html = linkify_html(hasil["answer"])
    except Exception:
        answer_html = html.escape(
            "Maaf, terjadi kendala saat mencari jawaban. Coba tanyakan ulang dengan kalimat lain, ya."
        )

    stream_bot_answer(placeholder, answer_html)

    messages.append({"role": "assistant", "content": answer_html})