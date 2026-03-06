# main.py
import traceback
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from contextlib import asynccontextmanager

from graph import graph
from database.db import test_connection
from memory.conversation_memory import save_message
from memory.customer_profile import get_or_create_customer
from utils.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Starting AI Sales Agent API...")
    test_connection()
    yield
    logger.info("🛑 Shutting down.")

app = FastAPI(
    title="AI Sales Agent",
    description="LangGraph-powered sales agent with product search, negotiation & orders.",
    version="1.0.0",
    lifespan=lifespan
)


# ── Schemas ───────────────────────────────────────

class ChatRequest(BaseModel):
    message:     str
    customer_id: int  = 0      # 0 = guest
    phone:       str  = "guest"
    name:        str  = "Guest"

class ChatResponse(BaseModel):
    response:    str
    intent:      str
    customer_id: int


# ── Routes ────────────────────────────────────────

@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    try:
        # Resolve customer
        customer_id = req.customer_id
        if customer_id == 0 and req.phone != "guest":
            customer_id = get_or_create_customer(req.phone, req.name)

        # Run LangGraph
        state = {"message": req.message, "customer_id": customer_id}
        result = graph.invoke(state)

        response = result.get("response", "Sorry, I could not generate a response.")
        intent   = result.get("intent", "general")

        # Persist conversation
        if customer_id:
            save_message(customer_id, "user",      req.message)
            save_message(customer_id, "assistant", response)

        return ChatResponse(response=response, intent=intent, customer_id=customer_id)

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=traceback.format_exc())


@app.get("/health")
async def health():
    return {"status": "ok", "service": "AI Sales Agent"}


@app.get("/")
async def root():
    return {"message": "AI Sales Agent is running. Visit /docs for API reference."}
