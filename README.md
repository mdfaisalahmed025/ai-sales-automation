# 🛍️ AI Sales Agent
### Production-Grade AI Automation Workflow System

> Built with **LangGraph** · **Groq LLaMA 3.3** · **FAISS Vector Search** · **FastAPI** · **MySQL** · **Streamlit**

[![Python](https://img.shields.io/badge/Python-3.14-blue?logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green?logo=fastapi)](https://fastapi.tiangolo.com)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.2-orange)](https://langchain-ai.github.io/langgraph)
[![Groq](https://img.shields.io/badge/Groq-LLaMA_3.3_70b-red)](https://console.groq.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.38-ff4b4b?logo=streamlit)](https://streamlit.io)
[![MySQL](https://img.shields.io/badge/MySQL-8.0-blue?logo=mysql)](https://mysql.com)

---

## 📌 Overview

A fully autonomous AI Sales Agent that handles the **complete customer journey** — from product discovery to price negotiation, order placement, and automated follow-ups — across **Web, WhatsApp, and Instagram** simultaneously.

The system is built on a **stateful LangGraph workflow** that routes each customer message to the correct specialized AI agent using zero-shot intent classification. Every agent is grounded with **real product data** from a FAISS semantic vector store, ensuring accurate and contextually relevant responses.

---

## ✨ Key Features

| Feature | Description |
|---|---|
| 🧠 **Intent Classification** | Zero-shot LLM classifies messages into 7 intents with smart routing |
| 🔍 **Vector Semantic Search** | FAISS + sentence-transformers for product similarity search |
| 💰 **Price Negotiation** | Business rule-aware discount engine with floor price protection |
| 🛒 **Order Processing** | Full order lifecycle — create, confirm, track with DB persistence |
| 🎯 **Product Recommendations** | Semantic top-k search with ranked, personalized suggestions |
| 💬 **Conversation Memory** | Full chat history per customer stored in MySQL |
| 📱 **Multi-Channel** | Web UI + WhatsApp (Twilio) + Instagram DM webhooks |
| ⏰ **Auto Follow-ups** | APScheduler runs daily to re-engage unconverted leads |
| 📊 **REST API** | FastAPI with full Swagger docs at `/docs` |

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     ENTRY POINTS                        │
│   Streamlit UI  │  FastAPI /chat  │  WhatsApp/Instagram │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│                  LANGGRAPH WORKFLOW                      │
│                                                         │
│   [intent_node] ──────────────────────────────────┐    │
│        │                                           │    │
│        ▼                                           │    │
│   ┌─────────┐  product_inquiry/pricing             │    │
│   │ Router  │──────────────► [product_node]        │    │
│   │         │  negotiation                         │    │
│   │         │──────────────► [negotiation_node]    │    │
│   │         │  recommendation                      │    │
│   │         │──────────────► [recommendation_node] │    │
│   │         │  order                               │    │
│   │         │──────────────► [order_node]          │    │
│   │         │  general/followup                    │    │
│   └─────────┘──────────────► [general_node]        │    │
│                                           │         │    │
└───────────────────────────────────────────┼─────────┘
                                            │
                         ▼                  ▼
┌─────────────────────────────────────────────────────────┐
│                   DATA LAYER                            │
│  FAISS Vector Store  │  MySQL DB  │  Conversation Memory│
└─────────────────────────────────────────────────────────┘
```

---

## 🤖 Agent Routing Table

| User Says | Detected Intent | Routed To | Action |
|---|---|---|---|
| "Tell me about iPhone 15" | `product_inquiry` | Product Agent | FAISS search + LLM response |
| "How much does MacBook cost?" | `pricing` | Product Agent | Price lookup + explanation |
| "Can I get a discount?" | `negotiation` | Negotiation Agent | Discount engine + offer |
| "What headphones are best?" | `recommendation` | Recommendation Agent | Semantic top-k ranking |
| "I want to buy Galaxy S24" | `order` | Order Agent | DB order creation |
| "Any updates on my order?" | `followup` | Product Agent | History lookup + update |
| "Hello / Thanks" | `general` | General Node | Greeting + capability list |

---

## 🗂️ Project Structure

```
ai-sales-agent/
│
├── app.py                         # Streamlit chat UI (dark luxury design)
├── main.py                        # FastAPI server with lifespan management
├── graph.py                       # LangGraph stateful workflow
├── config.py                      # Centralized config from .env
├── requirements.txt               # All dependencies
├── .env                           # Environment variables (not committed)
│
├── agents/                        # Specialized AI agents
│   ├── intent_agent.py            # Zero-shot intent classifier (7 intents)
│   ├── product_agent.py           # Product Q&A with vector grounding
│   ├── negotiation_agent.py       # Price negotiation with discount logic
│   ├── recommendation_agent.py    # Semantic product recommendations
│   ├── order_agent.py             # Order processing and confirmation
│   └── followup_agent.py          # Personalized follow-up generation
│
├── prompts/                       # Modular LLM prompt templates
│   ├── intent_prompt.py           # Intent classification prompt
│   ├── negotiation_prompt.py      # Negotiation dialogue prompt
│   ├── recommendation_prompt.py   # Recommendation prompt
│   └── followup_prompt.py         # Follow-up message prompt
│
├── database/                      # Database layer
│   ├── db.py                      # SQLAlchemy connection pool
│   ├── models.py                  # ORM models (Customer, Product, Order, Lead...)
│   └── migrations.sql             # Schema + seed data (5 sample products)
│
├── services/                      # Business logic layer
│   ├── product_service.py         # Product CRUD + stock management
│   ├── order_service.py           # Order creation + tracking
│   ├── lead_service.py            # Lead management
│   └── customer_service.py        # Customer profile management
│
├── vector_store/                  # Semantic search layer
│   ├── vector_build.py            # One-time FAISS index builder
│   ├── vector_search.py           # Real-time similarity search
│   ├── embeddings.py              # sentence-transformers wrapper
│   └── data/                      # FAISS index files (generated)
│       ├── faiss_index.faiss
│       └── faiss_index_meta.json
│
├── memory/                        # Customer memory layer
│   ├── conversation_memory.py     # Save/retrieve chat history
│   └── customer_profile.py        # Auto-create customer profiles
│
├── api/                           # External integrations
│   ├── whatsapp_api.py            # Twilio WhatsApp send
│   ├── instagram_api.py           # Instagram Graph API
│   └── webhook_router.py          # Webhook endpoints for both channels
│
├── automation/                    # Background automation
│   ├── followup_scheduler.py      # APScheduler daily follow-up job
│   └── discount_engine.py         # Discount calculation logic
│
├── utils/                         # Utilities
│   ├── logger.py                  # Loguru structured logger
│   ├── helpers.py                 # Text cleaning, currency formatting
│   └── validators.py              # Phone/email validation
│
└── logs/                          # Auto-generated log files
    └── app.log
```

---

## 🚀 Setup Guide (Step by Step)

### Prerequisites
- Python 3.11+
- MySQL 8.0+
- Groq API key → [console.groq.com](https://console.groq.com)

---

### Step 1 — Clone & Virtual Environment
```bash
git clone https://github.com/mdfaisalahmed025/ai-sales-agent-of-business-.git
cd ai-sales-agent-of-business-

python -m venv .venv
source .venv/bin/activate        # Mac/Linux
.venv\Scripts\activate           # Windows
```

### Step 2 — Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3 — Configure Environment
```bash
nano .env    # or open in any editor
```

```env
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxx        # Required
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=yourpassword                      # Required
DB_NAME=ai_sales_agent
TWILIO_ACCOUNT_SID=your_sid                  # Optional (WhatsApp)
TWILIO_AUTH_TOKEN=your_token                 # Optional (WhatsApp)
INSTAGRAM_ACCESS_TOKEN=your_token            # Optional (Instagram)
```

### Step 4 — Set Up MySQL Database
```bash
mysql -u root -pyourpassword < database/migrations.sql
```

Verify:
```
+-------------------+---------+
| name              | price   |
+-------------------+---------+
| iPhone 15 Pro     | 1199.00 |
| Samsung Galaxy S24|  999.00 |
| MacBook Air M3    | 1299.00 |
| Sony WH-1000XM5  |  349.00 |
| iPad Pro 12.9     | 1099.00 |
+-------------------+---------+
```

### Step 5 — Build Vector Index
```bash
python -m vector_store.vector_build
```

Expected:
```
✅ FAISS index built with 5 products → ./vector_store/data/faiss_index
```

### Step 6 — Start FastAPI Backend
```bash
uvicorn main:app --reload --port 8000
```

### Step 7 — Start Streamlit Frontend
```bash
streamlit run app.py
```

Open: **http://localhost:8501**
Swagger UI: **http://localhost:8000/docs**

---

## 🌐 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/chat` | Main chat endpoint |
| `GET` | `/health` | Health check |
| `GET` | `/` | Welcome message |
| `POST` | `/webhook/whatsapp` | Twilio WhatsApp webhook |
| `GET` | `/webhook/instagram` | Instagram verification |
| `POST` | `/webhook/instagram` | Instagram DM handler |
| `GET` | `/docs` | Swagger UI |

### Sample Request
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Can you give me a discount on MacBook Air M3?",
    "name": "Faisal",
    "phone": "+8801712345678",
    "customer_id": 0
  }'
```

### Sample Response
```json
{
  "response": "The MacBook Air M3 is an exceptional machine at $1,299. For you, I can offer a 10% discount bringing it to $1,169 — that's our best price. Shall I place that order?",
  "intent": "negotiation",
  "customer_id": 1
}
```

---

## 🧪 Test All Agents

```bash
# Product Inquiry
curl -X POST "http://localhost:8000/chat" -H "Content-Type: application/json" \
  -d '{"message": "Tell me about iPhone 15 Pro"}'

# Pricing
curl -X POST "http://localhost:8000/chat" -H "Content-Type: application/json" \
  -d '{"message": "How much does the MacBook Air M3 cost?"}'

# Negotiation
curl -X POST "http://localhost:8000/chat" -H "Content-Type: application/json" \
  -d '{"message": "Can I get a discount on Samsung Galaxy S24?"}'

# Recommendation
curl -X POST "http://localhost:8000/chat" -H "Content-Type: application/json" \
  -d '{"message": "What headphones would you recommend?"}'

# Order
curl -X POST "http://localhost:8000/chat" -H "Content-Type: application/json" \
  -d '{"message": "I want to buy the iPad Pro"}'
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **AI Orchestration** | LangGraph 0.2, LangChain 0.3 |
| **LLM** | Groq API — LLaMA 3.3-70b-versatile |
| **Vector Search** | FAISS (faiss-cpu), sentence-transformers |
| **Embedding Model** | all-MiniLM-L6-v2 (384 dimensions) |
| **Backend** | FastAPI 0.115, Uvicorn, Pydantic v2 |
| **Database** | MySQL 8.0, SQLAlchemy 2.0 ORM |
| **Frontend** | Streamlit 1.38 |
| **Messaging** | Twilio (WhatsApp), Instagram Graph API |
| **Scheduling** | APScheduler 3.10 |
| **Logging** | Loguru |
| **Language** | Python 3.14 |

---

## 🗄️ Database Schema

```sql
customers      — id, name, phone, email, channel, created_at
products       — id, name, category, description, price, stock, min_price
orders         — id, customer_id, product_id, quantity, total_price, status
leads          — id, customer_id, interest, status
conversations  — id, customer_id, role, message, created_at
followups      — id, customer_id, message, scheduled_at, sent
```

---

## 🔄 Automation Workflows

### Daily Follow-up Scheduler
```
Every 24 hours:
  1. Query leads with status = 'new' or 'contacted'
  2. Get customer profile for each lead
  3. Generate personalized message via followup_agent
  4. Save to followups table with sent=True
  5. Send via WhatsApp/Instagram (if configured)
```

### Discount Engine
```
Single item:       up to 10% off
Bulk (3+ units):   up to 15% off
Returning customer: +5% bonus
Floor price:       never below min_price in DB
```

---

## 🐛 Common Issues & Fixes

| Error | Fix |
|---|---|
| `Invalid API Key` | Check `GROQ_API_KEY` in `.env`, restart uvicorn |
| `Unknown column 'category'` | Re-run `migrations.sql` (has DROP + CREATE) |
| `FAISS index not found` | Run `python -m vector_store.vector_build` |
| `KeyError: 'message'` | Use `TypedDict` for State, not plain `dict` |
| `model_decommissioned` | Use `llama-3.3-70b-versatile` |
| `Access denied MySQL` | No space after `-p`: `mysql -u root -pyourpassword` |
| `label got empty value` | Set `label="Your message"` in `st.text_input` |
| `execute → invoke` | Use `graph.invoke(state)` not `graph.execute(state)` |

---

## 📄 License

MIT License — free to use, modify, and distribute.

---

## 👤 Author

**Md Faisal Ahmed**  
AI Automation Workflow Engineer  
GitHub: [@mdfaisalahmed025](https://github.com/mdfaisalahmed025)
