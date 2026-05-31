import requests
import pandas as pd
from dotenv import load_dotenv
import os
from datetime import datetime
from sqlalchemy import create_engine, text

# Load API keys
load_dotenv()
API_KEY = os.getenv("MEDIASTACK_API_KEY")

# Database connection
engine = create_engine("postgresql://abhimanyushukla@localhost/supplyguard_db")

KEYWORDS = [
    "supply chain disruption",
    "port strike",
    "factory fire",
    "raw material shortage",
    "logistics delay"
]

def fetch_news():
    all_articles = []

    for keyword in KEYWORDS:
        print(f"Fetching news for: {keyword}")
        url = "http://api.mediastack.com/v1/news"
        params = {
            "access_key": API_KEY,
            "keywords": keyword,
            "languages": "en",
            "limit": 10
        }

        response = requests.get(url, params=params)
        data = response.json()

        if "data" in data:
            for article in data["data"]:
                all_articles.append({
                    "title": article.get("title", ""),
                    "description": article.get("description", ""),
                    "source": article.get("source", ""),
                    "published_at": article.get("published_at", ""),
                    "url": article.get("url", ""),
                    "keyword": keyword
                })
        else:
            print(f"  Skipped '{keyword}': {data.get('error', {}).get('message', 'unknown error')}")

    df = pd.DataFrame(all_articles)

    if df.empty:
        print("No articles fetched.")
        return df

    # Save to CSV as backup
    os.makedirs("data", exist_ok=True)
    filename = f"data/news_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    df.to_csv(filename, index=False)
    print(f"✅ Saved {len(df)} articles to CSV: {filename}")

    # Save to PostgreSQL database
    inserted = 0
    with engine.connect() as conn:
        for _, row in df.iterrows():
            try:
                conn.execute(text("""
                    INSERT INTO raw_news (title, description, source, published_at, url, keyword)
                    VALUES (:title, :description, :source, :published_at, :url, :keyword)
                    ON CONFLICT (url) DO NOTHING
                """), {
                    "title": row["title"],
                    "description": row["description"],
                    "source": row["source"],
                    "published_at": row["published_at"] if row["published_at"] else None,
                    "url": row["url"],
                    "keyword": row["keyword"]
                })
                inserted += 1
            except Exception as e:
                print(f"  Skipped duplicate: {e}")
        conn.commit()

    print(f"✅ Inserted {inserted} articles into database")
    return df

if __name__ == "__main__":
    df = fetch_news()
    if not df.empty:
        print(df[["title", "source", "keyword"]].head(10))