# app.py
import streamlit as st
import requests
import json
import re
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

    # Health check
    try:
        health = requests.get(f"{API_URL}/health", timeout=2).json()
        st.success(f"✅ Server: {health['status']}")
    except:
        st.error("❌ Server offline — run uvicorn first")

    st.divider()

    # Current order status in sidebar
    if st.session_state.get("pending_order_id"):
        order_id = st.session_state["pending_order_id"]
        st.subheader("🛒 Pending Order")
        st.info(f"Order #{order_id}")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Pay Now"):
                payment_url = st.session_state.get("payment_url", "")
                if payment_url:
                    st.markdown(f"[Open Payment Page]({payment_url})")
                else:
                    st.warning("No payment link available")
        with col2:
            if st.button("❌ Cancel"):
                try:
                    r = requests.post(
                        f"{API_URL}/orders/{order_id}/cancel"
                    ).json()
                    if r.get("success"):
                        st.success("Order cancelled")
                        st.session_state.pop("pending_order_id", None)
                        st.session_state.pop("payment_url", None)
                        st.rerun()
                    else:
                        st.error(r.get("message"))
                except Exception as e:
                    st.error(str(e))

    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()


# ── Session state defaults ────────────────────────
if "messages"         not in st.session_state: st.session_state.messages         = []
if "customer_id"      not in st.session_state: st.session_state.customer_id      = 0
if "pending_order_id" not in st.session_state: st.session_state.pending_order_id = None
if "payment_url"      not in st.session_state: st.session_state.payment_url      = None
if "last_intent"      not in st.session_state: st.session_state.last_intent      = ""


# ── Main area ─────────────────────────────────────
st.title("AI Sales Agent Dashboard")

tab1, tab2, tab3 = st.tabs(["💬 Chat", "🛒 My Orders", "📊 API Logs"])


# ═══════════════════════════════════════════════════
# TAB 1 — CHAT
# ═══════════════════════════════════════════════════
with tab1:

    # Active order banner
    if st.session_state.get("pending_order_id"):
        order_id    = st.session_state["pending_order_id"]
        payment_url = st.session_state.get("payment_url", "")
        st.warning(
            f"⏳ **Order #{order_id} is awaiting payment.**  "
            f"{'[Complete Payment](' + payment_url + ')' if payment_url else ''}",
            icon="💳"
        )

    # ── Scrollable chat window ────────────────────────
    chat_container = st.container(height=550, border=False)
    with chat_container:
        if not st.session_state.messages:
            st.markdown(
                """
                <div style='text-align:center; padding: 80px 0; color: #888;'>
                    <h2>🤖 AI Sales Assistant</h2>
                    <p>Ask about products, prices, recommendations, or place an order.</p>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            for msg in st.session_state.messages:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

                    if msg.get("order_id"):
                        with st.container(border=True):
                            st.markdown(f"**🛒 Order #{msg['order_id']} Created**")
                            st.markdown(f"Total: **${msg.get('total_price', 0):.2f}**")
                            st.markdown(f"Status: `awaiting_payment`")
                            if msg.get("payment_url"):
                                st.link_button("💳 Complete Payment", msg["payment_url"])

                    st.caption(msg.get("time", ""))

    # ── Intent badge row (shows after response) ──────
    if st.session_state.get("last_intent"):
        color_map = {
            "order":            "green",
            "payment":          "blue",
            "negotiation":      "orange",
            "product_inquiry":  "gray",
            "pricing":          "gray",
            "recommendation":   "violet",
            "followup":         "red",
            "general":          "gray",
        }
        intent = st.session_state.last_intent
        st.badge(f"⚡ Intent: {intent}", color=color_map.get(intent, "gray"))

    # ── Fixed input at bottom ─────────────────────────
    prompt = st.chat_input("Message AI Sales Agent...")

    if prompt:
        # Clear last intent
        st.session_state.last_intent = ""

        # Append user message
        st.session_state.messages.append({
            "role":    "user",
            "content": prompt,
            "time":    datetime.now().strftime("%H:%M:%S")
        })

        data  = {}
        reply = ""

        with st.spinner(""):
            try:
                if channel == "📱 Simulate WhatsApp":
                    resp = requests.post(
                        f"{API_URL}/webhook/whatsapp",
                        data={
                            "From":        f"whatsapp:{customer_phone}",
                            "To":          "whatsapp:+14155238886",
                            "Body":        prompt,
                            "ProfileName": customer_name
                        },
                        timeout=30
                    )
                    match = re.search(r"<Message>(.*?)</Message>", resp.text, re.DOTALL)
                    reply = match.group(1) if match else "No reply"

                elif channel == "📸 Simulate Instagram":
                    resp = requests.post(
                        f"{API_URL}/webhook/instagram",
                        json={
                            "entry": [{
                                "messaging": [{
                                    "sender":  {"id": customer_phone},
                                    "message": {"text": prompt}
                                }]
                            }]
                        },
                        timeout=30
                    )
                    reply = resp.json().get("reply", "✅ Processed")

                else:
                    resp = requests.post(
                        f"{API_URL}/chat",
                        json={
                            "message":     prompt,
                            "phone":       customer_phone,
                            "name":        customer_name,
                            "customer_id": st.session_state.customer_id
                        },
                        timeout=30
                    )
                    data  = resp.json()
                    reply = data.get("response", "No response")

                    # Save customer_id
                    if data.get("customer_id"):
                        st.session_state.customer_id = data["customer_id"]

                    # Save intent for badge
                    if data.get("intent"):
                        st.session_state.last_intent = data["intent"]

                    # Order created
                    if data.get("order_id"):
                        st.session_state.pending_order_id = data["order_id"]
                        st.session_state.payment_url      = data.get("payment_url", "")

                    # Payment confirmed
                    intent = data.get("intent", "")
                    if intent == "payment" and data.get("payment_status") == "confirmed":
                        st.session_state.pending_order_id = None
                        st.session_state.payment_url      = None
                        st.balloons()

            except requests.exceptions.Timeout:
                reply = "⚠️ Request timed out — is the server running?"
            except Exception as e:
                reply = f"❌ Error: {str(e)}"

        # Append assistant message
        assistant_msg = {
            "role":    "assistant",
            "content": reply,
            "time":    datetime.now().strftime("%H:%M:%S")
        }
        if data.get("order_id"):
            assistant_msg["order_id"]     = data["order_id"]
            assistant_msg["total_price"]  = data.get("total_price", 0)
            assistant_msg["order_status"] = "awaiting_payment"
            assistant_msg["payment_url"]  = data.get("payment_url", "")

        st.session_state.messages.append(assistant_msg)
        st.rerun()
# ═══════════════════════════════════════════════════
# TAB 2 — MY ORDERS
# ═══════════════════════════════════════════════════
with tab2:
    st.subheader("🛒 Order History")

    customer_id = st.session_state.get("customer_id", 0)

    if not customer_id:
        st.info("Start a chat first to create a customer profile and see your orders here.")
    else:
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("🔄 Refresh Orders"):
                st.rerun()

        try:
            orders = requests.get(
                f"{API_URL}/orders/{customer_id}",
                timeout=5
            ).json()

            if not orders:
                st.info("No orders yet. Start chatting to place one!")
            else:
                for order in orders:
                    status = order.get("status", "pending")

                    # Color code by status
                    status_color = {
                        "pending":          "🟡",
                        "awaiting_payment": "🟠",
                        "paid":             "🔵",
                        "confirmed":        "🟢",
                        "failed":           "🔴",
                        "cancelled":        "⚫",
                    }.get(status, "⚪")

                    with st.container(border=True):
                        col1, col2, col3, col4 = st.columns([1, 2, 1, 2])

                        with col1:
                            st.markdown(f"**Order #{order['order_id']}**")

                        with col2:
                            st.markdown(f"Product ID: `{order['product_id']}`")
                            st.markdown(f"Qty: {order['quantity']}")

                        with col3:
                            st.markdown(f"**${order['total']:.2f}**")

                        with col4:
                            st.markdown(f"{status_color} `{status.upper()}`")

                            # Actions based on status
                            if status == "awaiting_payment":
                                payment_url = st.session_state.get("payment_url", "")
                                if payment_url:
                                    st.link_button("💳 Pay Now", payment_url, use_container_width=True)

                            if status in ("pending", "awaiting_payment"):
                                if st.button(
                                    "❌ Cancel",
                                    key=f"cancel_{order['order_id']}",
                                    use_container_width=True
                                ):
                                    try:
                                        r = requests.post(
                                            f"{API_URL}/orders/{order['order_id']}/cancel"
                                        ).json()
                                        if r.get("success"):
                                            st.success(f"Order #{order['order_id']} cancelled")
                                            st.rerun()
                                        else:
                                            st.error(r.get("message"))
                                    except Exception as e:
                                        st.error(str(e))

        except Exception as e:
            st.error(f"Could not fetch orders: {e}")

    # ── Simulate payment webhook (for testing) ────
    st.divider()
    st.subheader("🧪 Simulate Payment (Testing Only)")

    with st.expander("Simulate payment gateway callback"):
        sim_order_id = st.number_input(
            "Order ID",
            min_value=1,
            value=st.session_state.get("pending_order_id") or 1
        )
        sim_status = st.radio("Payment Result", ["success", "failed"], horizontal=True)

        if st.button("🚀 Send Simulated Webhook"):
            try:
                r = requests.post(
                    f"{API_URL}/webhook/payment",
                    json={
                        "order_id":   sim_order_id,
                        "status":     sim_status,
                        "payment_id": f"TEST_{datetime.now().strftime('%H%M%S')}"
                    },
                    timeout=10
                ).json()
                if sim_status == "success":
                    st.success(f"✅ Payment confirmed! {r}")
                    st.session_state.pending_order_id = None
                    st.balloons()
                else:
                    st.error(f"❌ Payment failed. Retry link sent. {r}")
            except Exception as e:
                st.error(str(e))


# ═══════════════════════════════════════════════════
# TAB 3 — API LOGS
# ═══════════════════════════════════════════════════
with tab3:
    st.subheader("📊 API Logs")
    st.info("Monitor your FastAPI terminal for live logs")

    col1, col2, col3, col4 = st.columns(4)

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
                        "hub.mode":          "subscribe",
                        "hub.verify_token":  "my_secret_verify_token",
                        "hub.challenge":     "123456"
                    }
                )
                st.success(f"Response: {r.text}")
            except Exception as e:
                st.error(str(e))

    with col4:
        if st.button("⚡ Trigger Follow-ups"):
            try:
                r = requests.post(f"{API_URL}/admin/trigger-followups").json()
                st.success(str(r))
            except Exception as e:
                st.error(str(e))