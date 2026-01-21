# 🎯 Consumer Intent Detector  
> AI-powered system to detect **high-intent buyers** from public marketplace listings (domain-agnostic, modular, and scalable)

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11%2B-blue" />
  <img src="https://img.shields.io/badge/FastAPI-0.109.0-009688" />
  <img src="https://img.shields.io/badge/OpenAI-GPT--4o--mini-412991" />
  <img src="https://img.shields.io/badge/Status-MVP%20Ready-success" />
</p>

---

## 📌 Overview

**Consumer Intent Detector** is a domain-agnostic AI pipeline that collects public marketplace listings and classifies them into high-intent consumer segments (example: **car buyers**).  
The system automatically ingests listing data, normalizes it into a unified schema, enriches it using OpenAI models, and exposes results via a clean **FastAPI REST API**.

✅ Use cases:
- Lead scoring & high-intent customer targeting  
- Market research and real-time demand sensing  
- High-urgency buyer discovery for sales teams  
- Competitive intelligence & trend monitoring  

---

## 🌟 Key Features

✅ **Multi-Source Data Ingestion**  
Scrapes listings from:
- Cars.com  
- AutoTrader  
- Craigslist  

✅ **AI Intent Classification**  
Uses OpenAI GPT models to infer:
- urgency (high / medium / low)
- confidence score (0–1)
- timeline & budget signals
- keywords & buyer intent indicators

✅ **Geofencing & Location Search**  
Location filtering using:
- City/state targeting  
- Radius-based search queries  

✅ **REST API with FastAPI**
- High performance  
- Automatic Swagger docs  
- Easy client integration  

✅ **Modular & Extendable Architecture**
- Add new sources without modifying core pipeline  
- Add new intent types (home buyers, rentals, etc.)  

✅ **Scalable Background Processing**
Supports ingestion via background tasks for real-time pipelines.

---

## 🧠 How It Works (Pipeline)

```text
Ingestion Request
     │
     ▼
Marketplace Connectors  (Cars.com / AutoTrader / Craigslist)
     │
     ▼
Normalization Service   (Unified schema for all sources)
     │
     ▼
AI Enrichment Layer     (Intent detection via OpenAI GPT)
     │
     ▼
Database Storage        (Firestore / PostgreSQL / MongoDB)
     │
     ▼
FastAPI Query Endpoints (Filter & serve intent signals)
```
---

## Project Structure

```text
consumer-intent-detector/
├── app/
│   ├── main.py                 # FastAPI entry point
│   ├── config.py               # Env + configuration loader
│   ├── models.py               # Pydantic models
│   └── database.py             # Firestore DB operations
├── connectors/
│   ├── base_connector.py       # Connector interface
│   ├── cars_com_connector.py
│   ├── autotrader_connector.py
│   └── craigslist_connector.py
├── services/
│   ├── normalizer.py           # Normalize listing schema
│   ├── ai_enrichment.py        # OpenAI intent classification
│   └── geofencing.py           # Location + radius filters
├── routers/
│   ├── ingestion.py            # /ingestion endpoints
│   └── intents.py              # /intents endpoints
├── utils/
│   ├── logger.py               # Logging utilities
│   └── helpers.py              # Generic helpers
├── .env.example
├── requirements.txt
├── Dockerfile
└── README.md
```

