from langchain_groq import ChatGroq
from config import config

llm = ChatGroq(
    api_key=config.GROQ_API_KEY,
   model="llama-3.3-70b-versatile"
)

def detect_intent(user_message):

    prompt = f"""
    Detect user intent.

    Possible intents:
    - product_search
    - negotiation
    - order
    - general

    message: {user_message}

    return only intent
    """

    response = llm.invoke(prompt)

    return response.content.strip()