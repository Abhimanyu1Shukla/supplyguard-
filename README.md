# SupplyGuard 🚨

An AI-powered supply chain risk intelligence platform that monitors global news, weather, and signals to alert companies about disruptions before they happen.

## Progress Log

### Day 1 — Project Setup
- GitHub repo created
- Python virtual environment configured
- All libraries installed
- Folder structure created
- API keys obtained (Mediastack, OpenWeatherMap)

### Day 2 — Data Pipeline
- Built `fetch_news.py` to pull live supply chain news
- Fetches across 5 risk keywords
- Saves results to timestamped CSV in `/data`
- Successfully pulling real articles from The Hindu, Business Line, and more

## Tech Stack
- Python 3.10+
- Pandas, Requests, SQLAlchemy
- Mediastack API, OpenWeatherMap API
- PostgreSQL (coming soon)

## Project Structure
```
supplyguard/
├── data/        # Raw fetched data
├── src/         # Python scripts
├── logs/        # Pipeline logs
├── notebooks/   # EDA and experiments
```