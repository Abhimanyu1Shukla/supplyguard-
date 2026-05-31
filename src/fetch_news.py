import requests
import pandas as pd
from dotenv import load_dotenv
import os
from datetime import datetime

# Load API key from .env file
load_dotenv()
API_KEY = os.getenv("MEDIASTACK_API_KEY")

# Keywords related to supply chain risks
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
            print(f"  No data for '{keyword}': {data}")

    # Save to CSV
    df = pd.DataFrame(all_articles)
    os.makedirs("data", exist_ok=True)
    filename = f"data/news_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    df.to_csv(filename, index=False)
    print(f"\n✅ Saved {len(df)} articles to {filename}")
    return df

if __name__ == "__main__":
    df = fetch_news()
    print(df[["title", "source", "keyword"]].head(10))