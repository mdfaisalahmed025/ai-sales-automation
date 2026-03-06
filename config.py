import os
from dotenv import load_dotenv

load_dotenv()

# ── LLM ───────────────────────────────────────────
GROQ_API_KEY        = os.getenv("GROQ_API_KEY")
LLM_MODEL           = "llama-3.3-70b-versatile"

# ── Database ──────────────────────────────────────
DB_HOST             = os.getenv("DB_HOST", "localhost")
DB_PORT             = int(os.getenv("DB_PORT", 3306))
DB_USER             = os.getenv("DB_USER", "root")
DB_PASSWORD         = os.getenv("DB_PASSWORD", "")
DB_NAME             = os.getenv("DB_NAME", "ai_sales_agent")

DATABASE_URL = (
    f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# ── Vector Store ──────────────────────────────────
EMBEDDING_MODEL     = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
VECTOR_DB_PATH      = os.getenv("VECTOR_DB_PATH", "./vector_store/data/faiss_index")

# ── WhatsApp ──────────────────────────────────────
TWILIO_ACCOUNT_SID      = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN       = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER  = os.getenv("TWILIO_WHATSAPP_NUMBER")

# ── Instagram ─────────────────────────────────────
INSTAGRAM_ACCESS_TOKEN  = os.getenv("INSTAGRAM_ACCESS_TOKEN")
INSTAGRAM_VERIFY_TOKEN  = os.getenv("INSTAGRAM_VERIFY_TOKEN")

# ── App ───────────────────────────────────────────
APP_ENV             = os.getenv("APP_ENV", "development")
LOG_LEVEL           = os.getenv("LOG_LEVEL", "INFO")
FASTAPI_PORT        = int(os.getenv("FASTAPI_PORT", 8000))
