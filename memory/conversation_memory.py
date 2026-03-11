# memory/conversation_memory.py
from database.db import SessionLocal
from database.models import Conversation, Customer
from utils.logger import logger


def save_message(customer_id: int, role: str, message: str):
    if not customer_id or customer_id <= 0:
        logger.warning("save_message skipped — invalid customer_id")
        return

    db = SessionLocal()
    try:
        # Guard: verify customer exists before inserting
        exists = db.query(Customer.id).filter(Customer.id == customer_id).first()
        if not exists:
            logger.warning(f"save_message skipped — customer_id {customer_id} not in DB")
            return

        entry = Conversation(customer_id=customer_id, role=role, message=message)
        db.add(entry)
        db.commit()

    except Exception as e:
        logger.error(f"Failed to save message: {e}")
        db.rollback()
    finally:
        db.close()


def get_history(customer_id: int, limit: int = 10) -> list[dict]:
    if not customer_id or customer_id <= 0:
        return []

    db = SessionLocal()
    try:
        rows = (
            db.query(Conversation)
            .filter(Conversation.customer_id == customer_id)
            .order_by(Conversation.created_at.desc())
            .limit(limit)
            .all()
        )
        return [{"role": r.role, "message": r.message} for r in reversed(rows)]

    except Exception as e:
        logger.error(f"Failed to fetch history: {e}")
        return []
    finally:
        db.close()