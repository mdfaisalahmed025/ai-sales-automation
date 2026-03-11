from sqlalchemy import Column, Integer, String, Text, DECIMAL, Boolean, DateTime, Enum, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()


class Customer(Base):
    __tablename__ = "customers"
    id         = Column(Integer, primary_key=True, autoincrement=True)
    name       = Column(String(255))
    phone      = Column(String(50), unique=True)
    email      = Column(String(255))
    channel    = Column(Enum("whatsapp", "instagram", "web"), default="web")
    created_at = Column(DateTime, default=datetime.utcnow)

    orders        = relationship("Order", back_populates="customer")
    conversations = relationship("Conversation", back_populates="customer")
    leads         = relationship("Lead", back_populates="customer")
    followups     = relationship("Followup", back_populates="customer")


class Product(Base):
    __tablename__ = "products"
    id          = Column(Integer, primary_key=True, autoincrement=True)
    name        = Column(String(255), nullable=False)
    category    = Column(String(100))
    description = Column(Text)
    price       = Column(DECIMAL(10, 2), nullable=False)
    stock       = Column(Integer, default=0)
    min_price   = Column(DECIMAL(10, 2))
    created_at  = Column(DateTime, default=datetime.utcnow)

    orders = relationship("Order", back_populates="product")



class Lead(Base):
    __tablename__ = "leads"
    id          = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    interest    = Column(Text)
    status      = Column(Enum("new", "contacted", "converted", "lost"), default="new")
    created_at  = Column(DateTime, default=datetime.utcnow)

    customer = relationship("Customer", back_populates="leads")


class Conversation(Base):
    __tablename__ = "conversations"
    id          = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    role        = Column(Enum("user", "assistant"), nullable=False)
    message     = Column(Text, nullable=False)
    created_at  = Column(DateTime, default=datetime.utcnow)

    customer = relationship("Customer", back_populates="conversations")


class Followup(Base):
    __tablename__ = "followups"
    id           = Column(Integer, primary_key=True, autoincrement=True)
    customer_id  = Column(Integer, ForeignKey("customers.id"))
    message      = Column(Text)
    scheduled_at = Column(DateTime)
    sent         = Column(Boolean, default=False)
    created_at   = Column(DateTime, default=datetime.utcnow)

    customer = relationship("Customer", back_populates="followups")


class Order(Base):
    __tablename__ = "orders"

    id          = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    product_id  = Column(Integer, ForeignKey("products.id"))
    quantity    = Column(Integer, default=1)
    total_price = Column(DECIMAL(10, 2))
    status      = Column(
                    Enum("pending", "awaiting_payment", "paid",
                         "confirmed", "failed", "cancelled",
                         "shipped", "delivered"),
                    default="pending"
                  )
    payment_id  = Column(String(255), nullable=True)
    payment_url = Column(String(500), nullable=True)
    notified_at = Column(DateTime, nullable=True)
    created_at  = Column(DateTime, default=datetime.utcnow)

    customer = relationship("Customer", back_populates="orders")
    product  = relationship("Product",  back_populates="orders")


# Add Notification model at the bottom
class Notification(Base):
    __tablename__ = "notifications"

    id          = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    message     = Column(Text)
    channel     = Column(Enum("web", "whatsapp", "instagram"), default="web")
    is_read     = Column(Boolean, default=False)
    created_at  = Column(DateTime, default=datetime.utcnow)