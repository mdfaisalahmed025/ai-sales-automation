# agents/order_agent.py
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from config import GROQ_API_KEY, LLM_MODEL
from utils.logger import logger
from services.order_service import create_order
from services.product_service import get_product_by_id
from services.notification_service import notify_order_created
from vector_store.vector_search import search_products

llm = ChatGroq(model=LLM_MODEL, api_key=GROQ_API_KEY, temperature=0.3)

SYSTEM_PROMPT = """You are an order processing assistant for a tech store.
When an order is placed, respond with a friendly confirmation message that includes:
- Product name and order ID
- Total price  
- A clear instruction to complete payment to confirm the order
Keep it concise and professional."""


def order_agent(state: dict) -> dict:
    message     = state.get("message", "")
    customer_id = state.get("customer_id")

    try:
        # Step 1 — Find product
        results = search_products(message, top_k=1)
        if not results:
            return {**state, "response": "I couldn't find that product. Could you clarify the name?"}

        product      = results[0]
        product_id   = product.get("id")
        product_name = product.get("name")

        # Step 2 — Check stock
        product_details = get_product_by_id(product_id)
        if not product_details or product_details["stock"] < 1:
            return {
                **state,
                "response": f"Sorry, **{product_name}** is currently out of stock. "
                            f"Would you like me to notify you when it's available?"
            }

        # Step 3 — Require customer
        if not customer_id:
            return {
                **state,
                "response": "I need your details to place an order. Could you share your name and phone number?"
            }

        # Step 4 — Create order
        order_result = create_order(
            customer_id=customer_id,
            product_id=product_id,
            quantity=1
        )
        if not order_result["success"]:
            return {**state, "response": f"Order failed: {order_result['message']}"}

        order_id    = order_result["order_id"]
        total_price = order_result["total_price"]

        # Step 5 — Payment placeholder (no gateway)
        payment_url = f"http://localhost:8000/pay?order_id={order_id}&amount={total_price}"

        # Step 6 — Send notification
        notify_order_created(
            customer_id=customer_id,
            order_id=order_id,
            product_name=product_name,
            total=total_price,
            payment_url=payment_url
        )

        # Step 7 — LLM confirmation message
        context = (
            f"Order successfully created:\n"
            f"- Order ID: #{order_id}\n"
            f"- Product: {product_name}\n"
            f"- Total: ${total_price:.2f}\n"
            f"- Status: Awaiting Payment\n\n"
            f"Tell the customer their order is created and they need to make payment to confirm it."
        )
        llm_messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=context)
        ]
        response = llm.invoke(llm_messages)

        return {
            **state,
            "response":         response.content.strip(),
            "intent":           "order",
            "order_id":         order_id,
            "total_price":      total_price,
            "payment_url":      payment_url,
            "pending_order_id": order_id
        }

    except Exception as e:
        logger.error(f"Order agent failed: {e}")
        return {
            **state,
            "response": "I'm unable to process your order right now. Please try again in a moment."
        }