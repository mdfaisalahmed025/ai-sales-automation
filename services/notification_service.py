# services/notification_service.py
from sqlalchemy import text
from database.db import SessionLocal
from api.whatsapp_api import send_whatsapp_message
from utils.logger import logger


def notify_customer(customer_id: int, message: str):
    db = SessionLocal()
    try:
        result = db.execute(
            text("SELECT phone, channel FROM customers WHERE id = :id"),
            {"id": customer_id}
        ).fetchone()

        if not result:
            logger.error(f"Customer {customer_id} not found for notification")
            return

        phone   = result[0]
        channel = result[1]

        if channel == "whatsapp" and phone:
            send_whatsapp_message(phone, message)
            logger.info(f"WhatsApp notification sent to {phone}")
        elif channel == "instagram":
            logger.info(f"Instagram DM queued for customer {customer_id}")
        else:
            db.execute(
                text("INSERT INTO notifications (customer_id, message, channel) "
                     "VALUES (:customer_id, :message, 'web')"),
                {"customer_id": customer_id, "message": message}
            )
            db.commit()
            logger.info(f"Web notification stored for customer {customer_id}")

    except Exception as e:
        logger.error(f"notify_customer failed: {e}")
        db.rollback()
    finally:
        db.close()


def notify_order_created(customer_id: int, order_id: int, product_name: str, total: float, payment_url: str):
    message = (
        f"✅ Order #{order_id} Received!\n\n"
        f"Product: {product_name}\n"
        f"Total: ${total:.2f}\n\n"
        f"Please make payment to confirm your order:\n{payment_url}"
    )
    notify_customer(customer_id, message)


def notify_order_confirmed(customer_id: int, order_id: int, product_name: str):
    message = (
        f"🎉 Payment Confirmed! Order #{order_id}\n\n"
        f"Your {product_name} order is confirmed and being processed.\n"
        f"We'll notify you once it ships."
    )
    notify_customer(customer_id, message)


def notify_payment_failed(customer_id: int, order_id: int, payment_url: str):
    message = (
        f"❌ Payment Failed for Order #{order_id}\n\n"
        f"Your payment didn't go through. Please retry:\n{payment_url}"
    )
    notify_customer(customer_id, message)