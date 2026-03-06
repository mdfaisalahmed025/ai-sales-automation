from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from config import DATABASE_URL
from utils.logger import logger
from typing import Generator  # Add this import

engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_recycle=3600)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:  # Updated return type
    """Yield a DB session — use as a context manager or FastAPI dependency."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_connection():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("✅ Database connected successfully.")
        return True
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False
