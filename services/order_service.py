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


def get_order(order_id: int) -> dict | None:
    """Fetch a single order by ID. Returns dict or None if not found."""
    db = SessionLocal()
    try:
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            logger.warning(f"Order #{order_id} not found")
            return None
        return {
            "id": order.id,
            "customer_id": order.customer_id,
            "product_id": order.product_id,
            "quantity": order.quantity,
            "total_price": float(order.total_price),
            "status": order.status,
            "payment_id": getattr(order, "payment_id", None)
        }
    finally:
        db.close()


def update_order_status(order_id: int, status: str, payment_id: str = None) -> dict:
    """Update order status. Optionally attach a payment_id on confirmation."""
    db = SessionLocal()
    try:
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            return {"success": False, "message": f"Order #{order_id} not found"}

        order.status = status
        if payment_id:
            order.payment_id = payment_id

        db.commit()
        logger.info(f"Order #{order_id} status updated to '{status}'")
        return {"success": True, "order_id": order_id, "status": status}
    except Exception as e:
        logger.error(f"Failed to update order #{order_id}: {e}")
        db.rollback()
        return {"success": False, "message": str(e)}
    finally:
        db.close()


def cancel_order(order_id: int) -> dict:
    """
    Cancel an order and restore stock.
    Only cancels if order is in a cancellable state (pending/awaiting_payment).
    """
    db = SessionLocal()
    try:
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            return {"success": False, "message": f"Order #{order_id} not found"}

        if order.status in ("confirmed", "shipped", "delivered"):
            return {
                "success": False,
                "message": f"Order #{order_id} is already {order.status} and cannot be cancelled."
            }

        if order.status == "cancelled":
            return {"success": False, "message": f"Order #{order_id} is already cancelled."}

        # Restore stock before cancelling
        from services.product_service import restore_stock
        restore_stock(order.product_id, order.quantity)

        order.status = "cancelled"
        db.commit()
        logger.info(f"Order #{order_id} cancelled — stock restored for product {order.product_id}")
        return {"success": True, "order_id": order_id, "message": "Order cancelled and stock restored."}

    except Exception as e:
        logger.error(f"Failed to cancel order #{order_id}: {e}")
        db.rollback()
        return {"success": False, "message": str(e)}
    finally:
        db.close()


def update_product_stock(product_id: int, quantity: int) -> dict:
    """Explicitly decrement stock — use after payment confirmation."""
    try:
        reduce_stock(product_id, quantity)
        logger.info(f"Stock updated for product {product_id} by -{quantity}")
        return {"success": True}
    except Exception as e:
        logger.error(f"Stock update failed for product {product_id}: {e}")
        return {"success": False, "message": str(e)}