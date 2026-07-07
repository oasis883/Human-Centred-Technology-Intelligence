import os
from pathlib import Path
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()

def main():
    report_path = Path("reports/insights_report.md")
    if not report_path.exists():
        raise FileNotFoundError("Run python src/run_pipeline.py first.")

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise EnvironmentError("Missing ANTHROPIC_API_KEY in .env")

    report = report_path.read_text(encoding="utf-8")
    client = Anthropic(api_key=api_key)

    message = client.messages.create(
        model="claude-3-5-haiku-latest",
        max_tokens=500,
        messages=[{"role": "user", "content": f"Create a short executive summary from this IT human-behaviour analytics report:\n\n{report}"}],
    )

    output = message.content[0].text
    Path("reports/claude_summary.md").write_text(output, encoding="utf-8")
    print("Claude summary created: reports/claude_summary.md")
    print(output)

if __name__ == "__main__":
    main()
