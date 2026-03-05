from langchain_groq import ChatGroq
from config import config

llm = ChatGroq(
    api_key=config.GROQ_API_KEY,
    model="llama-3.3-70b-versatile"
)

def negotiate(message):

    prompt = f"""
    You are a sales agent.

    Negotiate politely and try to close sale.

    Customer message:
    {message}
    """

    response = llm.invoke(prompt)

    return response.content