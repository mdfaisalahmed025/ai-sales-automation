
from langchain_groq import ChatGroq
from config import GROQ_API_KEY, LLM_MODEL
from utils.logger import logger
from langchain_core.messages import HumanMessage, SystemMessage

llm = ChatGroq(model=LLM_MODEL, api_key=GROQ_API_KEY, temperature=0)

INTENT_PROMPT = """
You are an intent classifier for an AI sales agent.

Classify the customer message into EXACTLY ONE of these intents:
- product_inquiry  : asking about product features, specs, availability, price
- pricing          : asking specifically about price, cost, how much
- negotiation      : asking for discount, deal, better price, bulk offer
- order            : wants to buy, place order, purchase
- recommendation   : asking for suggestions, comparisons, what should I get
- followup         : follow up on previous order or conversation
- general          : greeting, thank you, or anything else

Rules:
- If they mention a product AND ask about price → pricing
- If they mention discount, deal, negotiate → negotiation  
- If they say buy, order, purchase, want to get → order
- If they ask what's best, suggest, recommend → recommendation
- If they ask about features, specs, tell me about → product_inquiry

Respond with ONLY the intent label. No explanation. No punctuation.

Customer message: {message}
Intent:"""

VALID_INTENTS = {
    "product_inquiry", "pricing", "negotiation",
    "order", "recommendation", "followup", "general"
}

def detect_intent(message: str) -> str:
    try:
        prompt = INTENT_PROMPT.format(message=message)
        response = llm.invoke([HumanMessage(content=prompt)])
        intent = response.content.strip().lower().strip(".")
        logger.info(f"Raw intent response: '{intent}'")
        if intent not in VALID_INTENTS:
            logger.warning(f"Unknown intent '{intent}', defaulting to general")
            return "general"
        return intent
    except Exception as e:
        logger.error(f"Intent detection failed: {e}")
        return "general"