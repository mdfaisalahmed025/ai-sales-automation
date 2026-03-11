# graph.py
from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END
from agents.intent_agent import detect_intent
from agents.product_agent import product_agent
from agents.negotiation_agent import negotiate
from agents.recommendation_agent import recommend
from agents.order_agent import order_agent
from agents.payment_agent import payment_agent
from utils.logger import logger


# ── State ────────────────────────────────────────────────────────────────────

class State(TypedDict, total=False):
    message:          str
    intent:           str
    response:         str
    customer_id:      Optional[int]
    customer_name:    Optional[str]
    customer_phone:   Optional[str]
    pending_order_id: Optional[int]   # set by order_node, read by payment_node


# ── Nodes ────────────────────────────────────────────────────────────────────

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
    # order_agent now takes the full state and returns updated state
    updated = order_agent(state)
    return updated


def payment_node(state: State) -> State:
    # only runs if order_node set a pending_order_id
    if not state.get("pending_order_id"):
        state["response"] = (
            "I don't see a pending order. Would you like to place one?"
        )
        return state
    updated = payment_agent(state)
    return updated


def general_node(state: State) -> State:
    state["response"] = (
        "Hi! I'm your AI sales assistant. I can help you with:\n"
        "• Product information & specs\n"
        "• Pricing & deals\n"
        "• Price negotiation\n"
        "• Product recommendations\n"
        "• Placing & paying for orders\n\n"
        "What can I help you with today?"
    )
    return state


# ── Routers ──────────────────────────────────────────────────────────────────

def route_by_intent(state: State) -> str:
    intent = state.get("intent", "general")
    routes = {
        "product_inquiry": "product",
        "pricing":         "product",
        "negotiation":     "negotiation",
        "recommendation":  "recommendation",
        "order":           "order",
        "payment":         "payment",
        "followup":        "product",
        "general":         "general",
    }
    return routes.get(intent, "general")


def route_after_order(state: State) -> str:
    """
    After order_node runs:
    - If order was created successfully → go to payment_node
    - If something went wrong (no pending_order_id) → END
    """
    if state.get("pending_order_id"):
        logger.info(f"Order #{state['pending_order_id']} created — routing to payment")
        return "payment"
    logger.warning("Order node completed but no pending_order_id in state")
    return "end"


# ── Graph ────────────────────────────────────────────────────────────────────

builder = StateGraph(State)

builder.add_node("intent",         intent_node)
builder.add_node("product",        product_node)
builder.add_node("negotiation",    negotiation_node)
builder.add_node("recommendation", recommendation_node)
builder.add_node("order",          order_node)
builder.add_node("payment",        payment_node)
builder.add_node("general",        general_node)

builder.set_entry_point("intent")

# Intent → specialized node
builder.add_conditional_edges("intent", route_by_intent, {
    "product":        "product",
    "negotiation":    "negotiation",
    "recommendation": "recommendation",
    "order":          "order",
    "payment":        "payment",   # direct payment intent (e.g. "I want to pay")
    "general":        "general",
})

# Order → payment (conditional) or END
builder.add_conditional_edges("order", route_after_order, {
    "payment": "payment",
    "end":     END,
})

# Everything else → END
builder.add_edge("product",        END)
builder.add_edge("negotiation",    END)
builder.add_edge("recommendation", END)
builder.add_edge("payment",        END)
builder.add_edge("general",        END)

graph = builder.compile()