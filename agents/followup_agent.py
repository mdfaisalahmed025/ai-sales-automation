# agents/followup_agent.py
from langchain_groq import ChatGroq
from langchain.messages import HumanMessage
from prompts.followup_prompt import FOLLOWUP_PROMPT
from config import GROQ_API_KEY, LLM_MODEL
from utils.logger import logger

llm = ChatGroq(model=LLM_MODEL, api_key=GROQ_API_KEY, temperature=0.7)

def generate_followup(customer_name: str, interest: str, days_since: int = 3) -> str:
    try:
        prompt = FOLLOWUP_PROMPT.format(
            customer_name=customer_name,
            interest=interest,
            days_since=days_since
        )
        response = llm.invoke([HumanMessage(content=prompt)])
        return response.content.strip()
    except Exception as e:
        logger.error(f"Followup agent failed: {e}")
        return f"Hi {customer_name}, just checking in! Are you still interested in {interest}?"
