# automation/followup_scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from services.lead_service import get_unconverted_leads
from agents.followup_agent import generate_followup
from memory.customer_profile import get_customer
from database.db import SessionLocal
from database.models import Followup
from datetime import datetime
from utils.logger import logger


def run_followups():
    logger.info("⏰ Running scheduled follow-ups...")
    leads = get_unconverted_leads()
    db = SessionLocal()
    for lead in leads:
        customer = get_customer(lead["customer_id"])
        if not customer:
            continue
        message = generate_followup(
            customer_name=customer["name"],
            interest=lead["interest"],
            days_since=3
        )
        followup = Followup(
            customer_id=lead["customer_id"],
            message=message,
            scheduled_at=datetime.utcnow(),
            sent=True
        )
        db.add(followup)
        logger.info(f"Follow-up queued for customer {lead['customer_id']}: {message[:60]}...")
    db.commit()
    db.close()


def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(run_followups, "interval", hours=24, id="daily_followup")
    scheduler.start()
    logger.info("✅ Follow-up scheduler started (runs every 24 hours).")
    return scheduler
