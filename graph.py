# graph.py
from typing import TypedDict
from langgraph.graph import StateGraph, END
from agents.intent_agent import detect_intent
from agents.product_agent import product_agent
from agents.negotiation_agent import negotiate

# ✅ Use TypedDict instead of plain dict
class State(TypedDict, total=False):
    message: str
    intent: str
    response: str

def intent_node(state: State) -> State:
    state["intent"] = detect_intent(state["message"])
    return state

def product_node(state: State) -> State:
    state["response"] = product_agent(state["message"])
    return state

def negotiation_node(state: State) -> State:
    state["response"] = negotiate(state["message"])
    return state

def route_by_intent(state: State) -> str:
    intent = state.get("intent", "product")
    if intent == "negotiation":
        return "negotiation"
    return "product"

builder = StateGraph(State)
builder.add_node("intent", intent_node)
builder.add_node("product", product_node)
builder.add_node("negotiation", negotiation_node)

builder.set_entry_point("intent")
builder.add_conditional_edges("intent", route_by_intent, {
    "product": "product",
    "negotiation": "negotiation"
})
builder.add_edge("product", END)
builder.add_edge("negotiation", END)

graph = builder.compile()