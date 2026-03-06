# memory/conversation_memory.py
from database.db import SessionLocal
from database.models import Conversation
from utils.logger import logger


def save_message(customer_id: int, role: str, message: str):
    db = SessionLocal()
    try:
        entry = Conversation(customer_id=customer_id, role=role, message=message)
        db.add(entry)
        db.commit()
    except Exception as e:
        logger.error(f"Failed to save message: {e}")
        db.rollback()
    finally:
        db.close()


def get_history(customer_id: int, limit: int = 10) -> list[dict]:
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
