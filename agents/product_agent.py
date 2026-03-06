# agents/product_agent.py
from langchain_groq import ChatGroq
from langchain.messages import HumanMessage, SystemMessage
from vector_store.vector_search import search_products
from config import GROQ_API_KEY, LLM_MODEL
from utils.logger import logger

llm = ChatGroq(model=LLM_MODEL, api_key=GROQ_API_KEY, temperature=0.4)

SYSTEM_PROMPT = """You are a knowledgeable product specialist for a tech store.
Answer customer questions about products clearly and helpfully.
Use the product context provided. Be concise (2-4 sentences).
Always mention price and availability if known."""

def product_agent(message: str) -> str:
    try:
        # Search vector store for relevant products
        results = search_products(message, top_k=3)
        product_context = "\n".join([
            f"- {r['name']} | ${r['price']} | Stock: {r['stock']} | {r['description']}"
            for r in results
        ]) if results else "No specific products found."

        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=f"Product context:\n{product_context}\n\nCustomer: {message}")
        ]
        response = llm.invoke(messages)
        return response.content.strip()
    except Exception as e:
        logger.error(f"Product agent failed: {e}")
        return "I'm having trouble fetching product information. Please try again."
