# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from graph import graph
import traceback

app = FastAPI()

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
async def chat(req: ChatRequest):
    try:
        # ✅ Explicitly pass as plain dict with correct key
        state = {"message": req.message}
        result = graph.invoke(state)
        response = result.get("response", "Sorry, I could not generate a response.")
        return {"response": response}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=traceback.format_exc())