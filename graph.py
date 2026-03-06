
# graph.py
from typing import TypedDict
from langgraph.graph import StateGraph, END
from agents.intent_agent import detect_intent
from agents.product_agent import product_agent
from agents.negotiation_agent import negotiate
from agents.recommendation_agent import recommend
from agents.order_agent import order_agent
from utils.logger import logger


class State(TypedDict, total=False):
    message:     str
    intent:      str
    response:    str
    customer_id: int


def intent_node(state: State) -> State:
    state["intent"] = detect_intent(state["message"])
    logger.info(f"Intent detected: {state['intent']}")
    return state

def product_node(state: State) -> State:
    state["response"] = product_agent(state["message"])
    return state

def negotiation_node(state: State) -> State:
    state["response"] = negotiate(state["message"])
    return state

def recommendation_node(state: State) -> State:
    state["response"] = recommend(state["message"])
    return state

def order_node(state: State) -> State:
    state["response"] = order_agent(state["message"], state.get("customer_id"))
    return state

def general_node(state: State) -> State:
    state["response"] = (
        "Hi! I'm your AI sales assistant. I can help you with:\n"
        "• Product information & specs\n"
        "• Pricing & deals\n"
        "• Price negotiation\n"
        "• Product recommendations\n"
        "• Placing orders\n\n"
        "What can I help you with today?"
    )
    return state


def route_by_intent(state: State) -> str:
    intent = state.get("intent", "general")
    routes = {
        "product_inquiry": "product",
        "pricing":         "product",
        "negotiation":     "negotiation",
        "recommendation":  "recommendation",
        "order":           "order",
        "followup":        "product",
        "general":         "general",
    }
    return routes.get(intent, "general")


builder = StateGraph(State)
builder.add_node("intent",         intent_node)
builder.add_node("product",        product_node)
builder.add_node("negotiation",    negotiation_node)
builder.add_node("recommendation", recommendation_node)
builder.add_node("order",          order_node)
builder.add_node("general",        general_node)

builder.set_entry_point("intent")
builder.add_conditional_edges("intent", route_by_intent, {
    "product":        "product",
    "negotiation":    "negotiation",
    "recommendation": "recommendation",
    "order":          "order",
    "general":        "general",
})

builder.add_edge("product",        END)
builder.add_edge("negotiation",    END)
builder.add_edge("recommendation", END)
builder.add_edge("order",          END)
builder.add_edge("general",        END)

graph = builder.compile()