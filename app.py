# app.py
import streamlit as st
import requests

st.set_page_config(page_title="AI Sales Agent", page_icon="🛍️", layout="centered")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=Inter:wght@300;400;500&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background: #0e0e11; color: #f0f0f0; }
    .main { background: #0e0e11; }
    h1 { font-family:'Syne',sans-serif; font-weight:800; font-size:2.2rem;
         background:linear-gradient(135deg,#e0c97f,#f5a623);
         -webkit-background-clip:text; -webkit-text-fill-color:transparent; }
    .subtitle { color:#888; font-size:.9rem; margin-bottom:1.5rem; }
    .chat-user { background:linear-gradient(135deg,#e0c97f22,#f5a62311);
        border:1px solid #e0c97f44; border-radius:16px 16px 4px 16px;
        padding:12px 16px; margin:6px 0; font-size:.9rem; text-align:right; }
    .chat-ai { background:#1a1a22; border:1px solid #2e2e3a;
        border-radius:16px 16px 16px 4px; padding:12px 16px;
        margin:6px 0; font-size:.9rem; line-height:1.6; }
    .intent-badge { display:inline-block; background:#e0c97f22; border:1px solid #e0c97f44;
        border-radius:20px; padding:2px 10px; font-size:.72rem; color:#e0c97f; margin-top:4px; }
    .section-label { font-family:'Syne',sans-serif; font-size:.72rem; font-weight:700;
        letter-spacing:.12em; text-transform:uppercase; color:#e0c97f; margin:1.2rem 0 .4rem; }
    .stTextInput>div>div>input { background:#1a1a22 !important; border:1px solid #2e2e3a !important;
        border-radius:10px !important; color:#f0f0f0 !important; padding:12px 16px !important; }
    .stTextInput>div>div>input:focus { border-color:#e0c97f !important; }
    .stButton>button { background:linear-gradient(135deg,#e0c97f,#f5a623) !important;
        color:#0e0e11 !important; font-family:'Syne',sans-serif !important; font-weight:700 !important;
        border:none !important; border-radius:10px !important; width:100% !important; }
    hr { border-top:1px solid #2e2e3a; margin:1.2rem 0; }
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────
st.markdown("<h1>AI Sales Agent</h1>", unsafe_allow_html=True)
st.markdown('<p class="subtitle">Powered by LangGraph · Groq LLaMA 3.3 · FAISS Vector Search</p>', unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    customer_name  = st.text_input("Your Name",  value="Guest")
    customer_phone = st.text_input("Phone (optional)", placeholder="+880...")
    st.markdown("---")
    st.markdown("### 📌 Quick Prompts")
    quick_prompts = [
        "What laptops do you have?",
        "Tell me about iPhone 15 Pro",
        "Can you give me a discount on MacBook?",
        "I want to buy Samsung Galaxy S24",
        "What headphones would you recommend?",
        "What is your return policy?",
    ]
    selected_quick = None
    for qp in quick_prompts:
        if st.button(qp, key=f"qp_{qp}"):
            selected_quick = qp

# ── Chat History ──────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = []

if st.session_state.history:
    st.markdown('<p class="section-label">✦ Conversation</p>', unsafe_allow_html=True)
    for turn in st.session_state.history:
        st.markdown(f'<div class="chat-user">🧑 {turn["user"]}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="chat-ai">🤖 {turn["ai"]}'
                    f'<br><span class="intent-badge">intent: {turn.get("intent","—")}</span></div>',
                    unsafe_allow_html=True)

# ── Input ─────────────────────────────────────────
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown('<p class="section-label">✦ Your message</p>', unsafe_allow_html=True)

# ✅ After
user_input = st.text_input(
    label="Your message",
    value=selected_quick or "",
    placeholder="e.g. Can you give me a deal on the MacBook Air?",
    label_visibility="collapsed"
)

col1, col2 = st.columns([4, 1])
with col1:
    send = st.button("Send →")
with col2:
    if st.button("🗑"):
        st.session_state.history = []
        st.rerun()

# ── API Call ──────────────────────────────────────
if send and user_input.strip():
    with st.spinner("Agent is thinking..."):
        try:
            res = requests.post(
                "http://localhost:8000/chat",
                json={
                    "message":     user_input,
                    "name":        customer_name,
                    "phone":       customer_phone or "guest",
                    "customer_id": 0
                },
                timeout=30
            )
            if res.status_code == 200:
                data       = res.json()
                ai_reply   = data.get("response", "No response.")
                intent     = data.get("intent", "—")
            else:
                ai_reply = f"⚠️ Error {res.status_code}: {res.json().get('detail','Unknown error')}"
                intent   = "error"
        except requests.exceptions.ConnectionError:
            ai_reply = "❌ Cannot connect. Make sure FastAPI is running: `uvicorn main:app --reload`"
            intent   = "error"
        except requests.exceptions.Timeout:
            ai_reply = "⏱️ Request timed out. Please try again."
            intent   = "error"

    st.session_state.history.append({"user": user_input, "ai": ai_reply, "intent": intent})
    st.rerun()

elif send and not user_input.strip():
    st.warning("Please enter a message.")
