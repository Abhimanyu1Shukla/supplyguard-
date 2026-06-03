from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text as sql_text
from typing import Optional

app = FastAPI(title="SupplyGuard API", version="1.0")

# Allow frontend to talk to this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = create_engine("postgresql://abhimanyushukla@localhost/supplyguard_db")

@app.get("/")
def root():
    return {"message": "SupplyGuard API is running 🚀"}

@app.get("/news")
def get_news(category: Optional[str] = None, limit: int = 20):
    """Get latest classified news"""
    with engine.connect() as conn:
        if category:
            result = conn.execute(sql_text("""
                SELECT id, title, source, keyword, risk_category, confidence, fetched_at
                FROM raw_news
                WHERE risk_category = :category
                ORDER BY fetched_at DESC
                LIMIT :limit
            """), {"category": category, "limit": limit})
        else:
            result = conn.execute(sql_text("""
                SELECT id, title, source, keyword, risk_category, confidence, fetched_at
                FROM raw_news
                WHERE risk_category IS NOT NULL
                ORDER BY fetched_at DESC
                LIMIT :limit
            """), {"limit": limit})

        rows = result.fetchall()
        return [dict(row._mapping) for row in rows]

@app.get("/risk-summary")
def get_risk_summary():
    """Get risk distribution across all categories"""
    with engine.connect() as conn:
        result = conn.execute(sql_text("""
            SELECT risk_category, COUNT(*) as total,
                   ROUND(AVG(confidence)::numeric, 2) as avg_confidence
            FROM raw_news
            WHERE risk_category IS NOT NULL
            GROUP BY risk_category
            ORDER BY total DESC
        """))
        rows = result.fetchall()
        return [dict(row._mapping) for row in rows]

@app.get("/weather-alerts")
def get_weather_alerts():
    """Get current weather alerts"""
    with engine.connect() as conn:
        result = conn.execute(sql_text("""
            SELECT city, temperature, weather_condition,
                   wind_speed, humidity, is_alert, fetched_at
            FROM weather_alerts
            ORDER BY is_alert DESC, fetched_at DESC
        """))
        rows = result.fetchall()
        return [dict(row._mapping) for row in rows]

@app.get("/risk-score")
def get_overall_risk_score():
    """Calculate overall supply chain risk score"""
    with engine.connect() as conn:
        # Count high risk articles
        result = conn.execute(sql_text("""
            SELECT
                COUNT(*) FILTER (WHERE risk_category != 'no_risk') as risk_count,
                COUNT(*) as total,
                COUNT(*) FILTER (WHERE risk_category = 'natural_disaster') as disasters,
                COUNT(*) FILTER (WHERE risk_category = 'geopolitical') as geopolitical,
                COUNT(*) FILTER (WHERE risk_category = 'labour_strike') as strikes,
                COUNT(*) FILTER (WHERE risk_category = 'logistics') as logistics
            FROM raw_news
            WHERE risk_category IS NOT NULL
        """))
        news_stats = dict(result.fetchone()._mapping)

        # Count weather alerts
        result = conn.execute(sql_text("""
            SELECT COUNT(*) as alert_count
            FROM weather_alerts
            WHERE is_alert = TRUE
        """))
        weather_alerts = result.fetchone()[0]

    # Calculate risk score 0-100
    risk_ratio = news_stats["risk_count"] / max(news_stats["total"], 1)
    weather_factor = weather_alerts * 5
    risk_score = min(100, int(risk_ratio * 70 + weather_factor))

    risk_level = "LOW"
    if risk_score > 60:
        risk_level = "HIGH"
    elif risk_score > 35:
        risk_level = "MEDIUM"

    return {
        "risk_score": risk_score,
        "risk_level": risk_level,
        "news_stats": news_stats,
        "weather_alerts": weather_alerts
    }