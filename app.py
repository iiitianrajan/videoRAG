import streamlit as st
import time
from dotenv import load_dotenv
from utils.audio_processor import process_input
from core.transcriber import transcribe_all
from core.summarizer import summarize, generate_title
from core.extractor import extract_action_items, extract_key_decisions, extract_questions
from core.rag_engine import build_rag_chain, ask_question

load_dotenv()

# ─── Page Config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Meeting Intelligence",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Source+Serif+4:wght@500;600;700&family=Inter:wght@400;500;600&display=swap');

:root {
    --bg: #faf9f6;
    --surface: #ffffff;
    --border: #e3e1da;
    --ink: #1b1a17;
    --ink-muted: #706e65;
    --accent: #1f3a5f;
    --accent-soft: #edf1f5;
    --success: #2e6f4e;
    --warning: #a8752b;
    --danger: #a8402f;
}

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: var(--bg) !important;
    color: var(--ink) !important;
}

.stApp { background: var(--bg) !important; }

h1, h2, h3, h4 {
    font-family: 'Source Serif 4', serif !important;
    color: var(--ink) !important;
    font-weight: 600 !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * { color: var(--ink) !important; }

.wordmark {
    font-family: 'Source Serif 4', serif;
    font-size: 1.25rem;
    font-weight: 600;
    color: var(--ink);
    letter-spacing: 0.01em;
}
.wordmark-sub {
    font-family: 'Inter', sans-serif;
    font-size: 0.75rem;
    color: var(--ink-muted);
    margin-top: 0.15rem;
}

.sidebar-label {
    font-family: 'Inter', sans-serif;
    font-size: 0.75rem;
    font-weight: 600;
    color: var(--ink-muted);
    margin: 1.25rem 0 0.5rem 0;
}

/* ── Page header ── */
.page-title {
    font-family: 'Source Serif 4', serif;
    font-size: 2rem;
    font-weight: 600;
    color: var(--ink);
    margin: 0;
}
.page-subtitle {
    font-family: 'Inter', sans-serif;
    font-size: 0.9rem;
    color: var(--ink-muted);
    margin-top: 0.35rem;
}

/* ── Section blocks (replace glowing cards with hairline structure) ── */
.section {
    border-top: 1px solid var(--border);
    padding-top: 0.85rem;
    margin-top: 0.5rem;
    margin-bottom: 1.25rem;
}
.section-label {
    font-family: 'Inter', sans-serif;
    font-size: 0.78rem;
    font-weight: 600;
    color: var(--ink-muted);
    margin-bottom: 0.6rem;
}
.section-content {
    font-family: 'Source Serif 4', serif;
    font-size: 0.98rem;
    line-height: 1.65;
    color: var(--ink);
    white-space: pre-wrap;
    word-break: break-word;
}
.section-content.sans {
    font-family: 'Inter', sans-serif;
    font-size: 0.88rem;
}

/* Title banner: the one place we spend visual weight */
.doc-title-block {
    border-left: 3px solid var(--accent);
    padding: 0.9rem 0 0.9rem 1.1rem;
    margin-bottom: 1.5rem;
}
.doc-title-label {
    font-family: 'Inter', sans-serif;
    font-size: 0.75rem;
    color: var(--ink-muted);
    margin-bottom: 0.25rem;
}
.doc-title {
    font-family: 'Source Serif 4', serif;
    font-size: 1.6rem;
    font-weight: 600;
    color: var(--ink);
}

/* ── Inputs & buttons ── */
.stTextInput > div > div > input,
.stSelectbox > div > div {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 6px !important;
    color: var(--ink) !important;
    font-family: 'Inter', sans-serif !important;
}
.stTextInput > div > div > input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 2px var(--accent-soft) !important;
}

.stButton > button {
    background: var(--accent) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 6px !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    padding: 0.55rem 1.3rem !important;
    transition: opacity 0.15s !important;
}
.stButton > button:hover { opacity: 0.85 !important; }

.stButton > button[kind="secondary"] {
    background: var(--surface) !important;
    color: var(--ink) !important;
    border: 1px solid var(--border) !important;
}

/* ── Pipeline status (plain checklist, no glow/pulse) ── */
.status-row {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    padding: 0.4rem 0;
    font-size: 0.82rem;
    border-bottom: 1px solid var(--border);
}
.status-row:last-child { border-bottom: none; }
.status-mark { width: 1rem; text-align: center; font-size: 0.85rem; }
.mark-done    { color: var(--success); }
.mark-active  { color: var(--accent); }
.mark-pending { color: var(--ink-muted); }
.status-text-done    { color: var(--ink); }
.status-text-active  { color: var(--ink); font-weight: 600; }
.status-text-pending { color: var(--ink-muted); }

/* ── Chat ── */
.chat-container {
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1rem 1.25rem;
    max-height: 420px;
    overflow-y: auto;
    margin-bottom: 1rem;
    background: var(--surface);
}
.chat-msg { margin-bottom: 1rem; }
.chat-label {
    font-family: 'Inter', sans-serif;
    font-size: 0.72rem;
    font-weight: 600;
    margin-bottom: 0.2rem;
}
.chat-text {
    font-family: 'Source Serif 4', serif;
    font-size: 0.92rem;
    line-height: 1.6;
    color: var(--ink);
}
.user-row { text-align: right; }
.user-row .chat-label { color: var(--accent); }
.bot-row .chat-label { color: var(--ink-muted); }
.bot-row {
    border-top: 1px solid var(--border);
    padding-top: 0.6rem;
}

.empty-state {
    text-align: center;
    padding: 2.5rem 1rem;
    border: 1px solid var(--border);
    border-radius: 8px;
    color: var(--ink-muted);
    font-size: 0.88rem;
}

hr { border: none !important; border-top: 1px solid var(--border) !important; margin: 1.5rem 0 !important; }

[data-testid="stMarkdownContainer"] p { color: var(--ink) !important; }
label { color: var(--ink-muted) !important; font-size: 0.8rem !important; }

::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

# ─── Session State Init ──────────────────────────────────────────────────────
for key, default in {
    "result": None,
    "chat_history": [],
    "processing": False,
    "pipeline_done": False,
    "pipeline_steps": {},
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ─── Helpers ─────────────────────────────────────────────────────────────────
STEP_LABELS = [
    ("audio",      "Audio processing"),
    ("transcript", "Transcription"),
    ("title",      "Title generation"),
    ("summary",    "Summarisation"),
    ("extract",    "Extraction"),
    ("rag",        "Chat index"),
]

def render_status_list(steps: dict):
    rows = []
    for key, label in STEP_LABELS:
        state = steps.get(key, "pending")
        if state == "done":
            mark, mark_cls, text_cls = "✓", "mark-done", "status-text-done"
        elif state == "active":
            mark, mark_cls, text_cls = "→", "mark-active", "status-text-active"
        else:
            mark, mark_cls, text_cls = "·", "mark-pending", "status-text-pending"
        rows.append(f"""
        <div class="status-row">
            <span class="status-mark {mark_cls}">{mark}</span>
            <span class="{text_cls}">{label}</span>
        </div>""")
    st.markdown("".join(rows), unsafe_allow_html=True)

# ─── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="wordmark">Meeting Intelligence</div>', unsafe_allow_html=True)
    st.markdown('<div class="wordmark-sub">Transcribe, summarise, and query recordings</div>', unsafe_allow_html=True)

    st.markdown('<div class="sidebar-label">Source</div>', unsafe_allow_html=True)
    source = st.text_input(
        "YouTube URL or file path",
        placeholder="https://youtube.com/watch?v=... or /path/to/file.mp4",
        label_visibility="collapsed",
    )

    language = st.selectbox("Language", ["english", "hinglish"], index=0)

    run_btn = st.button("Analyse", use_container_width=True)

    if st.session_state.pipeline_done:
        st.markdown('<div class="sidebar-label">Pipeline status</div>', unsafe_allow_html=True)
        render_status_list(st.session_state.pipeline_steps)

# ─── Main Area ────────────────────────────────────────────────────────────────
st.markdown('<div class="page-title">Meeting Intelligence</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="page-subtitle">Turn a recording into a transcript, a summary, and a queryable record of the conversation.</div>',
    unsafe_allow_html=True,
)
st.markdown("<hr/>", unsafe_allow_html=True)

# ── Run Pipeline ───────────────────────────────────────────────────────────
if run_btn:
    if not source.strip():
        st.error("Enter a YouTube URL or file path.")
    else:
        st.session_state.pipeline_done = False
        st.session_state.result = None
        st.session_state.chat_history = []
        st.session_state.pipeline_steps = {}

        progress_placeholder = st.empty()

        def update_step(key, state):
            st.session_state.pipeline_steps[key] = state

        try:
            with progress_placeholder.container():
                st.info("Processing — see the sidebar for pipeline status.")

            update_step("audio", "active")
            chunks = process_input(source)
            update_step("audio", "done")

            update_step("transcript", "active")
            transcript = transcribe_all(chunks, language)
            update_step("transcript", "done")

            update_step("title", "active")
            title = generate_title(transcript)
            update_step("title", "done")

            update_step("summary", "active")
            summary = summarize(transcript)
            update_step("summary", "done")

            update_step("extract", "active")
            action_items = extract_action_items(transcript)
            decisions = extract_key_decisions(transcript)
            questions = extract_questions(transcript)
            update_step("extract", "done")

            update_step("rag", "active")
            rag_chain = build_rag_chain(transcript)
            update_step("rag", "done")

            st.session_state.result = {
                "title": title,
                "transcript": transcript,
                "summary": summary,
                "action_items": action_items,
                "key_decisions": decisions,
                "open_questions": questions,
                "rag_chain": rag_chain,
            }
            st.session_state.pipeline_done = True
            progress_placeholder.success("Analysis complete.")
            time.sleep(0.5)
            progress_placeholder.empty()
            st.rerun()

        except Exception as e:
            for k, _ in STEP_LABELS:
                if st.session_state.pipeline_steps.get(k) == "active":
                    st.session_state.pipeline_steps[k] = "pending"
            progress_placeholder.error(f"Something went wrong: {e}")

# ── Results ────────────────────────────────────────────────────────────────
if st.session_state.result:
    r = st.session_state.result

    st.markdown(f"""
    <div class="doc-title-block">
        <div class="doc-title-label">Session</div>
        <div class="doc-title">{r['title']}</div>
    </div>""", unsafe_allow_html=True)

    col1, col2 = st.columns([3, 2], gap="large")

    with col1:
        st.markdown(f"""
        <div class="section">
            <div class="section-label">Summary</div>
            <div class="section-content">{r['summary']}</div>
        </div>""", unsafe_allow_html=True)

    with col2:
        with st.expander("Full transcript", expanded=False):
            st.markdown(f'<div class="section-content sans">{r["transcript"]}</div>', unsafe_allow_html=True)

    st.markdown("<hr/>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3, gap="large")

    with c1:
        st.markdown(f"""
        <div class="section">
            <div class="section-label">Action items</div>
            <div class="section-content sans">{r['action_items']}</div>
        </div>""", unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="section">
            <div class="section-label">Key decisions</div>
            <div class="section-content sans">{r['key_decisions']}</div>
        </div>""", unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="section">
            <div class="section-label">Open questions</div>
            <div class="section-content sans">{r['open_questions']}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<hr/>", unsafe_allow_html=True)

    # ── Chat ─────────────────────────────────────────────────────────────
    st.markdown('<h3 style="margin-bottom:1rem">Ask about this meeting</h3>', unsafe_allow_html=True)

    if st.session_state.chat_history:
        chat_html = '<div class="chat-container">'
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                chat_html += f"""
                <div class="chat-msg user-row">
                    <div class="chat-label">You</div>
                    <div class="chat-text">{msg['content']}</div>
                </div>"""
            else:
                chat_html += f"""
                <div class="chat-msg bot-row">
                    <div class="chat-label">Assistant</div>
                    <div class="chat-text">{msg['content']}</div>
                </div>"""
        chat_html += '</div>'
        st.markdown(chat_html, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="empty-state">
            Ask a question about the transcript — for example, "what were the main decisions made?"
        </div>""", unsafe_allow_html=True)

    chat_col1, chat_col2 = st.columns([5, 1], gap="small")
    with chat_col1:
        user_input = st.text_input(
            "Your question",
            placeholder="What were the main decisions made?",
            label_visibility="collapsed",
        )
    with chat_col2:
        send_btn = st.button("Send", use_container_width=True)

    if send_btn and user_input.strip():
        with st.spinner("Thinking..."):
            answer = ask_question(r["rag_chain"], user_input.strip())
        st.session_state.chat_history.append({"role": "user", "content": user_input.strip()})
        st.session_state.chat_history.append({"role": "assistant", "content": answer})
        st.rerun()

    if st.session_state.chat_history:
        if st.button("Clear chat", type="secondary"):
            st.session_state.chat_history = []
            st.rerun()

else:
    st.markdown("""
    <div class="empty-state" style="padding:4rem 2rem">
        <div class="doc-title" style="margin-bottom:0.5rem">Ready when you are</div>
        <div style="max-width:420px;margin:0 auto;line-height:1.7">
            Add a YouTube URL or a local file path in the sidebar, choose the language, and select Analyse
            to generate a transcript, summary, and queryable record of the meeting.
        </div>
    </div>""", unsafe_allow_html=True)