# services/product_service.py
from database.db import SessionLocal
from database.models import Product
from utils.logger import logger


def get_all_products() -> list[dict]:
    db = SessionLocal()
    try:
        products = db.query(Product).filter(Product.stock > 0).all()
        return [
            {
                "id": p.id, "name": p.name, "category": p.category,
                "description": p.description, "price": float(p.price),
                "stock": p.stock, "min_price": float(p.min_price) if p.min_price else None
            }
            for p in products
        ]
    finally:
        db.close()


def get_product_by_id(product_id: int) -> dict | None:
    db = SessionLocal()
    try:
        p = db.query(Product).filter(Product.id == product_id).first()
        if p:
            return {
                "id": p.id, "name": p.name, "price": float(p.price),
                "stock": p.stock, "description": p.description
            }
        return None
    finally:
        db.close()


def reduce_stock(product_id: int, quantity: int = 1) -> bool:
    db = SessionLocal()
    try:
        p = db.query(Product).filter(Product.id == product_id).first()
        if p and p.stock >= quantity:
            p.stock -= quantity
            db.commit()
            return True
        return False
    except Exception as e:
        logger.error(f"Stock update failed: {e}")
        db.rollback()
        return False
    finally:
        db.close()
