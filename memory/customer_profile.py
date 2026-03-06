# memory/customer_profile.py
from database.db import SessionLocal
from database.models import Customer
from utils.logger import logger


def get_or_create_customer(phone: str, name: str = "Guest", channel: str = "web") -> int:
    db = SessionLocal()
    try:
        customer = db.query(Customer).filter(Customer.phone == phone).first()
        if not customer:
            customer = Customer(name=name, phone=phone, channel=channel)
            db.add(customer)
            db.commit()
            db.refresh(customer)
            logger.info(f"New customer created: {phone}")
        return customer.id
    except Exception as e:
        logger.error(f"Customer lookup failed: {e}")
        db.rollback()
        return 0
    finally:
        db.close()


def get_customer(customer_id: int) -> dict | None:
    db = SessionLocal()
    try:
        c = db.query(Customer).filter(Customer.id == customer_id).first()
        if c:
            return {"id": c.id, "name": c.name, "phone": c.phone, "channel": c.channel}
        return None
    finally:
        db.close()
