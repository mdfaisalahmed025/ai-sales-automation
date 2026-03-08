# app.py
import streamlit as st
import requests
import json
from datetime import datetime

API_URL = "http://localhost:8000"
st.set_page_config(
    page_title="AI Sales Agent",
    page_icon="🤖",
    layout="wide"
)

# ── Sidebar ───────────────────────────────────────
with st.sidebar:
    st.title("🤖 AI Sales Agent")
    st.divider()

    channel = st.radio(
        "Channel",
        ["💬 Direct Chat", "📱 Simulate WhatsApp", "📸 Simulate Instagram"]
    )

    st.divider()
    st.subheader("Customer Info")
    customer_phone = st.text_input("Phone Number", value="+8801868984364")
    customer_name  = st.text_input("Name", value="Test User")

    st.divider()

    # ── Health check ──────────────────────────────
    try:
        health = requests.get(f"{API_URL}/health", timeout=2).json()
        st.success(f"✅ Server: {health['status']}")
    except:
        st.error("❌ Server offline — run uvicorn first")

    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# ── Main chat area ────────────────────────────────
st.title("AI Sales Agent Dashboard")

# tabs
tab1, tab2 = st.tabs(["💬 Chat", "📊 API Logs"])

with tab1:
    # Chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display messages
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            st.caption(msg.get("time", ""))

    # Chat input
    if prompt := st.chat_input("Type a message..."):

        # Show user message
        st.session_state.messages.append({
            "role": "user",
            "content": prompt,
            "time": datetime.now().strftime("%H:%M:%S")
        })
        with st.chat_message("user"):
            st.write(prompt)

        # Call API based on channel
        with st.chat_message("assistant"):
            with st.spinner("AI is thinking..."):
                try:
                    if channel == "📱 Simulate WhatsApp":
                        # Exact same request Twilio sends
                        resp = requests.post(
                            f"{API_URL}/webhook/whatsapp",
                            data={
                                "From": f"whatsapp:{customer_phone}",
                                "To": "whatsapp:+14155238886",
                                "Body": prompt,
                                "ProfileName": customer_name
                            },
                            timeout=30
                        )
                        # Parse TwiML response
                        import re
                        match = re.search(r"<Message>(.*?)</Message>", resp.text, re.DOTALL)
                        reply = match.group(1) if match else "No reply"

                    elif channel == "📸 Simulate Instagram":
                        resp = requests.post(
                            f"{API_URL}/webhook/instagram",
                            json={
                                "entry": [{
                                    "messaging": [{
                                        "sender": {"id": customer_phone},
                                        "message": {"text": prompt}
                                    }]
                                }]
                            },
                            timeout=30
                        )
                        reply = resp.json().get("reply", "✅ Processed — reply sent via Instagram DM")

                    else:
                        # Direct chat — fastest, no webhook simulation
                        resp = requests.post(
                            f"{API_URL}/chat",
                            json={
                                "message": prompt,
                                "phone": customer_phone,
                                "name": customer_name,
                                "customer_id": 0
                            },
                            timeout=30
                        )
                        data  = resp.json()
                        reply = data.get("response", "No response")

                        # Show intent badge
                        intent = data.get("intent", "")
                        if intent:
                            st.badge(f"Intent: {intent}")

                except requests.exceptions.Timeout:
                    reply = "⚠️ Request timed out — is the server running?"
                except Exception as e:
                    reply = f"❌ Error: {str(e)}"

            st.write(reply)
            st.session_state.messages.append({
                "role": "assistant",
                "content": reply,
                "time": datetime.now().strftime("%H:%M:%S")
            })

with tab2:
    st.subheader("📊 API Logs")
    st.info("Monitor your FastAPI terminal for live logs")

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🔍 Health Check"):
            try:
                r = requests.get(f"{API_URL}/health").json()
                st.json(r)
            except:
                st.error("Server offline")

    with col2:
        if st.button("📱 Test WhatsApp"):
            try:
                r = requests.post(
                    f"{API_URL}/webhook/whatsapp",
                    data={"From": f"whatsapp:{customer_phone}", "Body": "test message"}
                )
                st.code(r.text, language="xml")
            except Exception as e:
                st.error(str(e))

    with col3:
        if st.button("📸 Test Instagram"):
            try:
                r = requests.get(
                    f"{API_URL}/webhook/instagram",
                    params={
                        "hub.mode": "subscribe",
                        "hub.verify_token": "my_secret_verify_token",
                        "hub.challenge": "123456"
                    }
                )
                st.success(f"Response: {r.text}")
            except Exception as e:
                st.error(str(e))