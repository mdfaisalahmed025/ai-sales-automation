# agents/order_agent.py
from langchain_groq import ChatGroq
from langchain.messages import HumanMessage, SystemMessage
from config import GROQ_API_KEY, LLM_MODEL
from utils.logger import logger

llm = ChatGroq(model=LLM_MODEL, api_key=GROQ_API_KEY, temperature=0.3)

SYSTEM_PROMPT = """You are an order processing assistant for a tech store.
Help customers confirm their order details, provide order status updates,
and guide them through the purchase process. Be clear and reassuring."""

def order_agent(message: str, customer_id: int = None) -> str:
    try:
        context = f"Customer ID: {customer_id}" if customer_id else "Guest customer"
        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=f"{context}\nCustomer: {message}")
        ]
        response = llm.invoke(messages)
        return response.content.strip()
    except Exception as e:
        logger.error(f"Order agent failed: {e}")
        return "I'm unable to process your order request right now. Please try again."
