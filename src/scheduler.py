import schedule
import time
import subprocess
import os
import logging
from datetime import datetime

# Setup logging
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    filename="logs/pipeline.log",
    level=logging.INFO,
    format="%(asctime)s — %(message)s"
)

def run_script(script_name):
    """Run a Python script and log the result"""
    print(f"\n🔄 Running {script_name} at {datetime.now().strftime('%H:%M:%S')}")
    logging.info(f"Running {script_name}")
    
    try:
        result = subprocess.run(
            ["python", f"src/{script_name}"],
            capture_output=True,
            text=True,
            timeout=120
        )
        if result.returncode == 0:
            print(f"✅ {script_name} completed successfully")
            logging.info(f"✅ {script_name} success")
        else:
            print(f"❌ {script_name} failed: {result.stderr}")
            logging.error(f"❌ {script_name} failed: {result.stderr}")
    except Exception as e:
        print(f"❌ Error running {script_name}: {e}")
        logging.error(f"❌ Error: {e}")

def run_all():
    run_script("fetch_news.py")
    run_script("fetch_weather.py")
    run_script("fetch_gdelt.py")
    print(f"\n✅ All pipelines completed at {datetime.now().strftime('%H:%M:%S')}")
    print("Next run scheduled automatically...\n")

# Schedule jobs
schedule.every(6).hours.do(lambda: run_script("fetch_news.py"))
schedule.every(3).hours.do(lambda: run_script("fetch_gdelt.py"))
schedule.every(12).hours.do(lambda: run_script("fetch_weather.py"))

if __name__ == "__main__":
    print("🚀 SupplyGuard Pipeline Scheduler Started")
    print("=" * 50)
    print("Schedule:")
    print("  • News fetch    → every 6 hours")
    print("  • GDELT fetch   → every 3 hours")
    print("  • Weather fetch → every 12 hours")
    print("=" * 50)
    
    # Run everything once immediately on startup
    print("\n▶ Running all pipelines now on startup...")
    run_all()
    
    # Then keep running on schedule
    while True:
        schedule.run_pending()
        time.sleep(60)