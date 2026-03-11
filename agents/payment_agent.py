from langchain_groq import ChatGroq
from config import GROQ_API_KEY, LLM_MODEL, TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN
import config
from services.order_service import get_order, cancel_order, update_order_status
from automation.discount_engine import calculate_discount

llm = ChatGroq(api_key=config.GROQ_API_KEY, model="llama-3.3-70b-versatile")

def payment_agent(state: dict) -> dict:
    if not state.get("pending_order_id"):
        state["response"] = "I don't see a pending order. Would you like to place one?"
        return state

    order_id = state.get("pending_order_id")
    order    = get_order(order_id)

    if not order:
        state["response"] = "I couldn't find your order. Please try again."
        return state

    # Look up product name from product_id
    from services.product_service import get_product_by_id
    product      = get_product_by_id(order["product_id"])
    product_name = product["name"] if product else f"Product #{order['product_id']}"
    total_price  = float(order["total_price"])
    payment_url  = f"http://localhost:8000/pay?order_id={order_id}&amount={total_price}"

    message     = state.get("message", "").lower()

    if any(word in message for word in ["pay", "payment", "checkout", "card", "bkash", "nagad"]):
        response = (
            f"Your order total is **${total_price:.2f}**.\n\n"
            f"Please complete your payment to confirm Order #{order_id}.\n"
            f"Payment link: {payment_url}"
        )
    elif any(word in message for word in ["cancel", "nevermind", "don't want"]):
        from services.order_service import cancel_order
        cancel_order(order_id)
        state["pending_order_id"] = None
        response = f"Order #{order_id} has been cancelled. Let me know if you'd like to order anything else."
    else:
        response = (
            f"You have a pending order for **{product_name}** — **${total_price:.2f}**.\n\n"
            f"Please make payment to confirm your order: {payment_url}"
        )

    return {**state, "response": response, "intent": "payment"}

def generate_payment_link(order: dict) -> str:
    # Hook into your payment gateway here
    # SSLCommerz for Bangladesh, or Stripe for international
    base_url = "https://yourapp.com/pay"
    return f"{base_url}?order_id={order['id']}&amount={order['total_price']}"