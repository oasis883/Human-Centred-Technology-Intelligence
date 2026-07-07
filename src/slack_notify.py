import os
from pathlib import Path
import requests
from dotenv import load_dotenv

load_dotenv()

def main():
    webhook = os.getenv("SLACK_WEBHOOK_URL")
    if not webhook:
        raise EnvironmentError("Missing SLACK_WEBHOOK_URL in .env")

    report_path = Path("reports/insights_report.md")
    if not report_path.exists():
        raise FileNotFoundError("Run python src/run_pipeline.py first.")

    report = report_path.read_text(encoding="utf-8")
    message = report[:2500]

    response = requests.post(webhook, json={"text": message}, timeout=15)
    response.raise_for_status()
    print("Slack notification sent.")

if __name__ == "__main__":
    main()
