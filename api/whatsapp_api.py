# api/whatsapp_api.py
from twilio.rest import Client
from config import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_WHATSAPP_NUMBER
from utils.logger import logger


def send_whatsapp_message(to_number: str, message: str) -> bool:
    """Send a WhatsApp message via Twilio."""
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        msg = client.messages.create(
            from_=TWILIO_WHATSAPP_NUMBER,
            to=f"whatsapp:{to_number}",
            body=message
        )
        logger.info(f"WhatsApp sent to {to_number}: SID={msg.sid}")
        return True
    except Exception as e:
        logger.error(f"WhatsApp send failed: {e}")
        return False
