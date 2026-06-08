# SupplyGuard 🚨
### AI-Powered Supply Chain Risk Intelligence Platform

SupplyGuard is an end-to-end machine learning system that monitors global news, weather events, and geopolitical signals to detect supply chain disruptions in real time — before they impact businesses.

---

## The Problem

Supply chain disruptions cost Indian companies an estimated ₹2.3 lakh crore annually. Procurement teams find out about port strikes, factory fires, and raw material shortages only after the damage is done. There is no affordable, automated early warning system for mid-size companies.

SupplyGuard solves this.

---

## What It Does

- Monitors **3 live data sources** continuously — global news, weather APIs, and GDELT event data
- Automatically **classifies every article** into 7 risk categories using a fine-tuned DistilBERT model
- Calculates a **real-time risk score** (0–100) based on news signals + weather alerts
- Serves everything through a **REST API** that any frontend or integration can consume
- Displays all intelligence on a **live dashboard** built for procurement managers

---

## Architecture

```
🌐 INTERNET
    │
    ├── Mediastack API       (global news)
    ├── OpenWeatherMap API   (weather data)
    └── GDELT Project        (geopolitical events)
         │
         ▼
    🐍 PYTHON DATA PIPELINE
    ├── fetch_news.py        → every 6 hours
    ├── fetch_weather.py     → every 12 hours
    └── fetch_gdelt.py       → every 3 hours
         │
         ▼
    ⏰ AUTOMATED SCHEDULER
    (runs all pipelines automatically, logs every run)
         │
         ▼
    🗄️ POSTGRESQL DATABASE
    ├── raw_news             (articles + risk classifications)
    ├── weather_alerts       (10 Indian cities)
    └── gdelt_events         (India-related global events)
         │
         ▼
    🤖 ML CLASSIFICATION ENGINE
    ├── Baseline: TF-IDF + Logistic Regression
    └── Production: Fine-tuned DistilBERT (7 risk categories)
         │
         ▼
    🔌 FASTAPI BACKEND          🖥️ LIVE DASHBOARD
    ├── /news                   ├── Risk score (0-100)
    ├── /risk-summary           ├── Weather alerts map
    ├── /weather-alerts         ├── Risk distribution
    ├── /risk-score             ├── News feed
    └── /docs (Swagger UI)      └── Intelligence summary
```

---

## Risk Categories

The ML model classifies every news article into one of 7 categories:

| Category | Example Signal |
|---|---|
| `natural_disaster` | Factory fire, earthquake, flood |
| `geopolitical` | War, sanctions, trade conflict |
| `labour_strike` | Port workers strike, union action |
| `material_shortage` | Chip shortage, steel prices surge |
| `logistics` | Port congestion, shipping delays |
| `political` | Export ban, new regulations |
| `no_risk` | Earnings reports, general news |

---

## ML Model

**Baseline:** TF-IDF vectorization + Logistic Regression — 64% accuracy

**Production:** DistilBERT fine-tuned on labelled supply chain news — 6/6 real-world headlines classified correctly

**Training data:** 70 labelled examples across 7 categories (30 real articles + 40 augmented examples)

**Why DistilBERT:** Unlike TF-IDF which counts words, DistilBERT understands context. It correctly identifies "Apple reports earnings" as `no_risk` while flagging "Apple supplier hit by Taiwan earthquake" as `natural_disaster` — even though both mention Apple.

---

## Risk Score Formula

```python
risk_ratio    = risk_articles / total_articles
weather_factor = active_weather_alerts × 5
risk_score    = min(100, risk_ratio × 70 + weather_factor)

# Risk Levels
LOW    → score < 35
MEDIUM → score 35–60
HIGH   → score > 60
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.12 |
| ML / NLP | DistilBERT, Hugging Face Transformers, PyTorch |
| Classical ML | Scikit-learn, TF-IDF |
| Database | PostgreSQL + SQLAlchemy |
| Backend API | FastAPI + Uvicorn |
| Data Sources | Mediastack API, OpenWeatherMap, GDELT Project |
| Automation | Schedule library |
| Frontend | HTML, CSS, JavaScript |
| Version Control | Git + GitHub |

---

## Project Structure

```
supplyguard/
├── src/
│   ├── fetch_news.py           # News pipeline (Mediastack)
│   ├── fetch_weather.py        # Weather pipeline (OpenWeatherMap)
│   ├── fetch_gdelt.py          # Events pipeline (GDELT)
│   ├── scheduler.py            # Automated pipeline runner
│   ├── prepare_training_data.py # Data labelling + augmentation
│   ├── train_model.py          # TF-IDF baseline model
│   ├── train_distilbert.py     # DistilBERT fine-tuning
│   ├── classify_news.py        # Auto-classify new articles
│   └── api.py                  # FastAPI backend
├── data/
│   ├── training_data.csv       # Labelled training examples
│   └── news_*.csv              # Raw fetched articles
├── logs/
│   └── pipeline.log            # Scheduler run history
├── notebooks/                  # EDA and experiments
├── dashboard.html              # Live risk dashboard
├── .env                        # API keys 
├── .gitignore
└── README.md
```

---

## Getting Started

### Prerequisites
- Python 3.10+
- PostgreSQL 15
- API keys for Mediastack and OpenWeatherMap

### Installation

```bash
# Clone the repo
git clone https://github.com/Abhimanyu1Shukla/supplyguard-.git
cd supplyguard-

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Mac/Linux
# venv\Scripts\activate   # Windows

# Install dependencies
pip install requests pandas sqlalchemy psycopg2-binary python-dotenv \
            schedule scikit-learn transformers torch datasets \
            fastapi uvicorn
```

### Configuration

Create a `.env` file in the root directory:
```
MEDIASTACK_API_KEY=your_mediastack_key
WEATHER_API_KEY=your_openweathermap_key
```

### Database Setup

```bash
createdb supplyguard_db
psql supplyguard_db

CREATE TABLE raw_news (
    id SERIAL PRIMARY KEY,
    title TEXT,
    description TEXT,
    source VARCHAR(100),
    published_at TIMESTAMP,
    url TEXT UNIQUE,
    keyword VARCHAR(100),
    risk_category VARCHAR(50),
    confidence FLOAT,
    fetched_at TIMESTAMP DEFAULT NOW()
);
```

### Running the Pipeline

```bash
# Fetch data once
python src/fetch_news.py
python src/fetch_weather.py
python src/fetch_gdelt.py

# Or run automated scheduler (runs everything on schedule)
python src/scheduler.py
```

### Training the Model

```bash
# Prepare training data
python src/prepare_training_data.py

# Train baseline model
python src/train_model.py

# Train DistilBERT model
python src/train_distilbert.py

# Classify all articles in database
python src/classify_news.py
```

### Starting the API

```bash
python -m uvicorn src.api:app --reload
```

API docs available at: **http://localhost:8000/docs**

### Opening the Dashboard

Open `dashboard.html` in your browser while the API is running.

---

## API Endpoints

| Endpoint | Description |
|---|---|
| `GET /` | Health check |
| `GET /news` | Latest classified articles |
| `GET /risk-summary` | Risk distribution by category |
| `GET /weather-alerts` | Current weather alerts for Indian cities |
| `GET /risk-score` | Overall risk score + breakdown |

---

## Business Impact

This system addresses a real gap in the market:

- **Target users:** Procurement managers at mid-size Indian manufacturers, e-commerce companies, FMCG brands
- **Value proposition:** 4–7 day early warning on supply disruptions vs finding out when it's too late
- **Monetization path:** B2B SaaS — ₹5,000–50,000/month per company depending on scale
- **Comparable products:** Resilinc, Riskmethods (both charge $50,000+/year — unaffordable for Indian SMEs)

---

## Future Roadmap

-  WhatsApp/Slack alert integration for real-time notifications
-  Supplier knowledge graph (Neo4j) mapping supplier → material → company relationships
-  Expand to 50+ cities and global port monitoring
-  Mobile app for procurement managers
-  Historical risk trend analysis and forecasting
-  Multi-language support (Hindi, Tamil, Telugu)

---

## Author

**Abhimanyu Shukla**
---

*Built to solve a real problem. Every data point is live. Every risk score is calculated in real time.*
