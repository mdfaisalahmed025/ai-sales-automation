# agents/recommendation_agent.py
from langchain_groq import ChatGroq
from langchain.messages import HumanMessage
from vector_store.vector_search import search_products
from prompts.recommendation_prompt import RECOMMENDATION_PROMPT
from config import GROQ_API_KEY, LLM_MODEL
from utils.logger import logger

llm = ChatGroq(model=LLM_MODEL, api_key=GROQ_API_KEY, temperature=0.6)

def recommend(message: str) -> str:
    try:
        results = search_products(message, top_k=5)
        product_list = "\n".join([
            f"- {r['name']} (${r['price']}) – {r['description']}"
            for r in results
        ]) if results else "No products available."

        prompt = RECOMMENDATION_PROMPT.format(
            product_list=product_list,
            message=message
        )
        response = llm.invoke([HumanMessage(content=prompt)])
        return response.content.strip()
    except Exception as e:
        logger.error(f"Recommendation agent failed: {e}")
        return "I couldn't generate recommendations right now. Please try again."
