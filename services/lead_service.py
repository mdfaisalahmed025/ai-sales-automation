# services/lead_service.py
from database.db import SessionLocal
from database.models import Lead
from utils.logger import logger


def create_lead(customer_id: int, interest: str) -> bool:
    db = SessionLocal()
    try:
        lead = Lead(customer_id=customer_id, interest=interest, status="new")
        db.add(lead)
        db.commit()
        return True
    except Exception as e:
        logger.error(f"Lead creation failed: {e}")
        db.rollback()
        return False
    finally:
        db.close()


def get_unconverted_leads() -> list[dict]:
    db = SessionLocal()
    try:
        leads = db.query(Lead).filter(Lead.status.in_(["new", "contacted"])).all()
        return [
            {"lead_id": l.id, "customer_id": l.customer_id,
             "interest": l.interest, "status": l.status}
            for l in leads
        ]
    finally:
        db.close()
