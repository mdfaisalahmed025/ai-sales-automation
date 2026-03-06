# api/webhook_router.py
from fastapi import APIRouter, Request, Response
from graph import graph
from memory.conversation_memory import save_message
from memory.customer_profile import get_or_create_customer
from api.whatsapp_api import send_whatsapp_message
from config import INSTAGRAM_VERIFY_TOKEN
from utils.logger import logger

router = APIRouter()


# ── WhatsApp Webhook (Twilio) ─────────────────────

@router.post("/webhook/whatsapp")
async def whatsapp_webhook(request: Request):
    form = await request.form()
    from_number = str(form.get("From", "")).replace("whatsapp:", "")
    body        = str(form.get("Body", "")).strip()

    if not body:
        return Response(content="", media_type="text/xml")

    logger.info(f"WhatsApp from {from_number}: {body}")

    customer_id = get_or_create_customer(from_number, channel="whatsapp")
    state  = {"message": body, "customer_id": customer_id}
    result = graph.invoke(state)
    reply  = result.get("response", "Sorry, I couldn't process that.")

    save_message(customer_id, "user",      body)
    save_message(customer_id, "assistant", reply)

    send_whatsapp_message(from_number, reply)

    # Twilio expects TwiML
    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response><Message>{reply}</Message></Response>"""
    return Response(content=twiml, media_type="text/xml")


# ── Instagram Webhook ─────────────────────────────

@router.get("/webhook/instagram")
async def instagram_verify(request: Request):
    params     = request.query_params
    mode       = params.get("hub.mode")
    token      = params.get("hub.verify_token")
    challenge  = params.get("hub.challenge")
    if mode == "subscribe" and token == INSTAGRAM_VERIFY_TOKEN:
        logger.info("Instagram webhook verified.")
        return Response(content=challenge)
    return Response(status_code=403)


@router.post("/webhook/instagram")
async def instagram_webhook(request: Request):
    data = await request.json()
    try:
        entry    = data["entry"][0]
        messaging = entry["messaging"][0]
        sender_id = messaging["sender"]["id"]
        body      = messaging.get("message", {}).get("text", "")

        if not body:
            return {"status": "no text"}

        logger.info(f"Instagram from {sender_id}: {body}")
        customer_id = get_or_create_customer(sender_id, channel="instagram")
        state  = {"message": body, "customer_id": customer_id}
        result = graph.invoke(state)
        reply  = result.get("response", "Sorry, I couldn't process that.")

        save_message(customer_id, "user",      body)
        save_message(customer_id, "assistant", reply)

        # TODO: send reply via Instagram Graph API
        logger.info(f"Instagram reply (not sent): {reply}")
    except Exception as e:
        logger.error(f"Instagram webhook error: {e}")

    return {"status": "ok"}
