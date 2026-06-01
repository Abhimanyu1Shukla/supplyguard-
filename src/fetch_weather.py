import requests
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from datetime import datetime

load_dotenv()
WEATHER_KEY = os.getenv("WEATHER_API_KEY")

engine = create_engine("postgresql://abhimanyushukla@localhost/supplyguard_db")

# Major Indian industrial cities
CITIES = [
    "Mumbai", "Chennai", "Pune", "Ahmedabad", "Surat",
    "Delhi", "Kolkata", "Bengaluru", "Hyderabad", "Jaipur"
]

def create_weather_table():
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS weather_alerts (
                id SERIAL PRIMARY KEY,
                city VARCHAR(100),
                temperature FLOAT,
                weather_condition VARCHAR(200),
                wind_speed FLOAT,
                humidity INT,
                is_alert BOOLEAN DEFAULT FALSE,
                fetched_at TIMESTAMP DEFAULT NOW()
            )
        """))
        conn.commit()
    print("✅ Weather table ready")

def fetch_weather():
    create_weather_table()
    inserted = 0

    for city in CITIES:
        print(f"Fetching weather for: {city}")
        url = "http://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": f"{city},IN",
            "appid": WEATHER_KEY,
            "units": "metric"
        }

        try:
            response = requests.get(url, params=params)
            data = response.json()

            if data.get("cod") == 200:
                temp = data["main"]["temp"]
                condition = data["weather"][0]["description"]
                wind = data["wind"]["speed"]
                humidity = data["main"]["humidity"]

                # Flag as alert if extreme weather
                is_alert = (
                    temp > 42 or        # Extreme heat
                    wind > 15 or        # Strong winds
                    humidity > 90 or    # Extreme humidity
                    any(word in condition.lower() for word in
                        ["storm", "flood", "heavy rain", "tornado"])
                )

                with engine.connect() as conn:
                    conn.execute(text("""
                        INSERT INTO weather_alerts
                        (city, temperature, weather_condition, wind_speed, humidity, is_alert)
                        VALUES (:city, :temp, :condition, :wind, :humidity, :is_alert)
                    """), {
                        "city": city,
                        "temp": temp,
                        "condition": condition,
                        "wind": wind,
                        "humidity": humidity,
                        "is_alert": is_alert
                    })
                    conn.commit()
                inserted += 1

                alert_tag = "🚨 ALERT" if is_alert else "✅ Normal"
                print(f"  {city}: {temp}°C, {condition} {alert_tag}")
            else:
                print(f"  Error for {city}: {data.get('message')}")

        except Exception as e:
            print(f"  Failed for {city}: {e}")

    print(f"\n✅ Weather data saved for {inserted} cities")

if __name__ == "__main__":
    fetch_weather()