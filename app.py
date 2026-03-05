import streamlit as st
import requests

# ─── Page Config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Sales Agent",
    page_icon="🛍️",
    layout="centered"
)

# ─── Custom CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=Inter:wght@300;400;500&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background-color: #0e0e11;
        color: #f0f0f0;
    }

    .main { background-color: #0e0e11; }

    h1 {
        font-family: 'Syne', sans-serif;
        font-weight: 800;
        font-size: 2.4rem;
        background: linear-gradient(135deg, #e0c97f, #f5a623);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }

    .subtitle {
        color: #888;
        font-size: 0.95rem;
        margin-bottom: 2rem;
        font-weight: 300;
    }

    .prompt-card {
        background: #1a1a22;
        border: 1px solid #2e2e3a;
        border-radius: 12px;
        padding: 14px 18px;
        margin: 6px 0;
        cursor: pointer;
        transition: all 0.2s ease;
        font-size: 0.9rem;
        color: #ccc;
    }

    .prompt-card:hover {
        border-color: #e0c97f;
        color: #fff;
        background: #1f1f2e;
    }

    .section-label {
        font-family: 'Syne', sans-serif;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: #e0c97f;
        margin: 1.5rem 0 0.5rem 0;
    }

    .chat-bubble-user {
        background: linear-gradient(135deg, #e0c97f22, #f5a62311);
        border: 1px solid #e0c97f44;
        border-radius: 16px 16px 4px 16px;
        padding: 12px 16px;
        margin: 8px 0;
        font-size: 0.92rem;
        color: #f0f0f0;
        text-align: right;
    }

    .chat-bubble-ai {
        background: #1a1a22;
        border: 1px solid #2e2e3a;
        border-radius: 16px 16px 16px 4px;
        padding: 12px 16px;
        margin: 8px 0;
        font-size: 0.92rem;
        color: #d0d0d0;
        line-height: 1.6;
    }

    .stTextInput > div > div > input {
        background-color: #1a1a22 !important;
        border: 1px solid #2e2e3a !important;
        border-radius: 10px !important;
        color: #f0f0f0 !important;
        font-family: 'Inter', sans-serif !important;
        padding: 12px 16px !important;
    }

    .stTextInput > div > div > input:focus {
        border-color: #e0c97f !important;
        box-shadow: 0 0 0 2px #e0c97f22 !important;
    }

    .stButton > button {
        background: linear-gradient(135deg, #e0c97f, #f5a623) !important;
        color: #0e0e11 !important;
        font-family: 'Syne', sans-serif !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 10px 28px !important;
        font-size: 0.95rem !important;
        letter-spacing: 0.04em !important;
        width: 100% !important;
        transition: opacity 0.2s !important;
    }

    .stButton > button:hover { opacity: 0.88 !important; }

    .divider {
        border: none;
        border-top: 1px solid #2e2e3a;
        margin: 1.5rem 0;
    }

    .badge {
        display: inline-block;
        background: #1a1a22;
        border: 1px solid #2e2e3a;
        border-radius: 20px;
        padding: 3px 12px;
        font-size: 0.75rem;
        color: #888;
        margin-right: 6px;
    }
</style>
""", unsafe_allow_html=True)


# ─── Header ─────────────────────────────────────────────────────────────────
st.markdown("<h1>AI Sales Agent</h1>", unsafe_allow_html=True)
st.markdown(
    '<p class="subtitle">Ask about products, pricing, discounts, or negotiate a deal.</p>',
    unsafe_allow_html=True
)
st.markdown(
    '<span class="badge">🟢 Online</span>'
    '<span class="badge">⚡ Groq LLaMA 3.3</span>'
    '<span class="badge">🔀 LangGraph</span>',
    unsafe_allow_html=True
)
st.markdown("<hr class='divider'>", unsafe_allow_html=True)


# ─── Suggested Prompts ──────────────────────────────────────────────────────
PROMPT_SUGGESTIONS = {
    "🛒 Product Inquiry": [
        "What laptops do you have under $1000?",
        "Tell me about the features of the iPhone 15 Pro.",
        "What's the difference between the Basic and Pro plan?",
        "Do you have any wireless headphones in stock?",
    ],
    "💰 Pricing & Deals": [
        "What is the price of the MacBook Air M3?",
        "Are there any ongoing discounts or seasonal offers?",
        "What's included in the premium package?",
        "Is there a bundle deal if I buy multiple items?",
    ],
    "🤝 Negotiation": [
        "Can you give me a better price on the Samsung Galaxy S24?",
        "I'm a returning customer — can I get a loyalty discount?",
        "If I buy 3 units, will you offer a bulk discount?",
        "What's the best deal you can offer me today?",
    ],
    "📦 After Sales": [
        "What is your return and refund policy?",
        "How long does shipping take?",
        "Do you offer warranty on electronics?",
        "Can I exchange a product after purchase?",
    ],
}

st.markdown('<p class="section-label">✦ Try a prompt</p>', unsafe_allow_html=True)

selected_prompt = None
for category, prompts in PROMPT_SUGGESTIONS.items():
    with st.expander(category, expanded=False):
        for prompt in prompts:
            if st.button(prompt, key=f"btn_{prompt}"):
                selected_prompt = prompt


# ─── Chat History ───────────────────────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = []

if st.session_state.history:
    st.markdown('<p class="section-label">✦ Conversation</p>', unsafe_allow_html=True)
    for turn in st.session_state.history:
        st.markdown(
            f'<div class="chat-bubble-user">🧑 {turn["user"]}</div>',
            unsafe_allow_html=True
        )
        st.markdown(
            f'<div class="chat-bubble-ai">🤖 {turn["ai"]}</div>',
            unsafe_allow_html=True
        )


# ─── Input ──────────────────────────────────────────────────────────────────
st.markdown("<hr class='divider'>", unsafe_allow_html=True)
st.markdown('<p class="section-label">✦ Your message</p>', unsafe_allow_html=True)

user_input = st.text_input(
    label="",
    value=selected_prompt if selected_prompt else "",
    placeholder="e.g. Can you give me a discount on the MacBook Pro?",
    label_visibility="collapsed"
)

col1, col2 = st.columns([3, 1])
with col1:
    send = st.button("Send Message →")
with col2:
    if st.button("🗑 Clear"):
        st.session_state.history = []
        st.rerun()


# ─── API Call ───────────────────────────────────────────────────────────────
if send and user_input.strip():
    with st.spinner("Agent is thinking..."):
        try:
            res = requests.post(
                "http://localhost:8000/chat",
                json={"message": user_input},
                timeout=20
            )
            if res.status_code == 200:
                ai_response = res.json().get("response", "No response received.")
            else:
                ai_response = f"⚠️ Error {res.status_code}: {res.json().get('detail', res.text)}"
        except requests.exceptions.ConnectionError:
            ai_response = "❌ Cannot connect to backend. Make sure FastAPI is running on port 8000."
        except requests.exceptions.Timeout:
            ai_response = "⏱️ Request timed out. The agent is taking too long to respond."
        except Exception as e:
            ai_response = f"❌ Unexpected error: {str(e)}"

    st.session_state.history.append({"user": user_input, "ai": ai_response})
    st.rerun()

elif send and not user_input.strip():
    st.warning("Please enter a message before sending.")