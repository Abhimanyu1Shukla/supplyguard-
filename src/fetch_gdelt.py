import pandas as pd
import requests
from sqlalchemy import create_engine, text
from datetime import datetime
import io

engine = create_engine("postgresql://abhimanyushukla@localhost/supplyguard_db")

def create_gdelt_table():
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS gdelt_events (
                id SERIAL PRIMARY KEY,
                event_date VARCHAR(20),
                actor1 VARCHAR(200),
                actor2 VARCHAR(200),
                event_code VARCHAR(20),
                goldstein_scale FLOAT,
                num_articles INT,
                avg_tone FLOAT,
                country_code VARCHAR(10),
                fetched_at TIMESTAMP DEFAULT NOW()
            )
        """))
        conn.commit()
    print("✅ GDELT table ready")

def fetch_gdelt():
    create_gdelt_table()
    print("Fetching GDELT events...")

    # GDELT 2.0 latest events file
    master_url = "http://data.gdeltproject.org/gdeltv2/lastupdate.txt"

    try:
        response = requests.get(master_url, timeout=30)
        lines = response.text.strip().split("\n")

        # Get the CSV export file URL
        csv_url = None
        for line in lines:
            if line.endswith(".export.CSV.zip"):
                csv_url = line.split(" ")[-1]
                break

        if not csv_url:
            print("Could not find GDELT CSV URL")
            return

        print(f"Downloading GDELT data...")
        csv_response = requests.get(csv_url, timeout=60)

        # GDELT CSV columns (partial)
        cols = [
            "GlobalEventID", "Day", "MonthYear", "Year", "FractionDate",
            "Actor1Code", "Actor1Name", "Actor1CountryCode",
            "Actor2Code", "Actor2Name", "Actor2CountryCode",
            "IsRootEvent", "EventCode", "EventBaseCode",
            "EventRootCode", "QuadClass", "GoldsteinScale",
            "NumMentions", "NumSources", "NumArticles", "AvgTone",
            "Actor1Geo_Type", "Actor1Geo_FullName", "Actor1Geo_CountryCode",
            "Actor2Geo_Type", "Actor2Geo_FullName", "Actor2Geo_CountryCode",
            "ActionGeo_Type", "ActionGeo_FullName", "ActionGeo_CountryCode",
            "DATEADDED", "SOURCEURL"
        ]

        import zipfile, io as _io
        with zipfile.ZipFile(_io.BytesIO(csv_response.content)) as z:
            with z.open(z.namelist()[0]) as f:
                df = pd.read_csv(f, sep="\t", header=None,
                               names=cols, usecols=range(len(cols)),
                               on_bad_lines='skip')

        # Filter for India-related events
        india_df = df[
            (df["Actor1CountryCode"] == "IND") |
            (df["Actor2CountryCode"] == "IND") |
            (df["ActionGeo_CountryCode"] == "IN")
        ].copy()

        print(f"Found {len(india_df)} India-related events")

        # Insert into database
        inserted = 0
        with engine.connect() as conn:
            for _, row in india_df.head(50).iterrows():
                try:
                    conn.execute(text("""
                        INSERT INTO gdelt_events
                        (event_date, actor1, actor2, event_code,
                         goldstein_scale, num_articles, avg_tone, country_code)
                        VALUES (:event_date, :actor1, :actor2, :event_code,
                                :goldstein, :num_articles, :avg_tone, :country)
                    """), {
                        "event_date": str(row["Day"]),
                        "actor1": str(row["Actor1Name"])[:200],
                        "actor2": str(row["Actor2Name"])[:200],
                        "event_code": str(row["EventCode"]),
                        "goldstein": float(row["GoldsteinScale"]) if pd.notna(row["GoldsteinScale"]) else 0.0,
                        "num_articles": int(row["NumArticles"]) if pd.notna(row["NumArticles"]) else 0,
                        "avg_tone": float(row["AvgTone"]) if pd.notna(row["AvgTone"]) else 0.0,
                        "country": str(row["ActionGeo_CountryCode"])[:10]
                    })
                    inserted += 1
                except Exception as e:
                    continue
            conn.commit()

        print(f"✅ Inserted {inserted} GDELT events into database")

    except Exception as e:
        print(f"Error fetching GDELT: {e}")

if __name__ == "__main__":
    fetch_gdelt()