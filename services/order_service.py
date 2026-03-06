# services/order_service.py
from database.db import SessionLocal
from database.models import Order
from services.product_service import get_product_by_id, reduce_stock
from utils.logger import logger


def create_order(customer_id: int, product_id: int, quantity: int = 1) -> dict:
    product = get_product_by_id(product_id)
    if not product:
        return {"success": False, "message": "Product not found."}
    if product["stock"] < quantity:
        return {"success": False, "message": "Insufficient stock."}

    total_price = product["price"] * quantity
    db = SessionLocal()
    try:
        order = Order(
            customer_id=customer_id,
            product_id=product_id,
            quantity=quantity,
            total_price=total_price,
            status="pending"
        )
        db.add(order)
        reduce_stock(product_id, quantity)
        db.commit()
        db.refresh(order)
        logger.info(f"Order #{order.id} created for customer {customer_id}")
        return {"success": True, "order_id": order.id, "total_price": total_price}
    except Exception as e:
        logger.error(f"Order creation failed: {e}")
        db.rollback()
        return {"success": False, "message": str(e)}
    finally:
        db.close()


def get_orders_by_customer(customer_id: int) -> list[dict]:
    db = SessionLocal()
    try:
        orders = db.query(Order).filter(Order.customer_id == customer_id).all()
        return [
            {"order_id": o.id, "product_id": o.product_id,
             "quantity": o.quantity, "total": float(o.total_price), "status": o.status}
            for o in orders
        ]
    finally:
        db.close()
