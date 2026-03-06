# services/customer_service.py
from database.db import SessionLocal
from database.models import Customer
from utils.logger import logger


def get_all_customers() -> list[dict]:
    db = SessionLocal()
    try:
        customers = db.query(Customer).all()
        return [
            {"id": c.id, "name": c.name, "phone": c.phone,
             "email": c.email, "channel": c.channel}
            for c in customers
        ]
    finally:
        db.close()


def update_customer_name(customer_id: int, name: str) -> bool:
    db = SessionLocal()
    try:
        c = db.query(Customer).filter(Customer.id == customer_id).first()
        if c:
            c.name = name
            db.commit()
            return True
        return False
    except Exception as e:
        logger.error(f"Customer update failed: {e}")
        db.rollback()
        return False
    finally:
        db.close()
