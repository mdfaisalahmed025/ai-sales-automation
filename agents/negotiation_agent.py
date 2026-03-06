# agents/negotiation_agent.py
from langchain_groq import ChatGroq
from langchain.messages import HumanMessage
from vector_store.vector_search import search_products
from prompts.negotiation_prompt import NEGOTIATION_PROMPT
from config import GROQ_API_KEY, LLM_MODEL
from utils.logger import logger

llm = ChatGroq(model=LLM_MODEL, api_key=GROQ_API_KEY, temperature=0.5)

def negotiate(message: str) -> str:
    try:
        results = search_products(message, top_k=2)
        product_context = "\n".join([
            f"- {r['name']} | Price: ${r['price']} | Min Price: ${r.get('min_price', 'N/A')}"
            for r in results
        ]) if results else "No specific product found."

        prompt = NEGOTIATION_PROMPT.format(
            product_context=product_context,
            message=message
        )
        response = llm.invoke([HumanMessage(content=prompt)])
        return response.content.strip()
    except Exception as e:
        logger.error(f"Negotiation agent failed: {e}")
        return "I'm unable to process your request right now. Please try again."
