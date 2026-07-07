from pathlib import Path
import pandas as pd

def generate_report(input_path="data/processed/behaviour_classified_tickets.csv", output_path="reports/insights_report.md"):
    if not Path(input_path).exists():
        raise FileNotFoundError(f"Missing classified file: {input_path}. Run classify_behaviour.py first.")

    df = pd.read_csv(input_path)
    total = len(df)

    lines = [
        "# HumanTech Intelligence Report",
        "",
        "## Summary",
        "",
        f"Total tickets analysed: **{total}**",
        "",
        "## Behaviour Categories",
        ""
    ]

    counts = df["behaviour_category"].value_counts()
    for category, count in counts.items():
        percent = round((count / total) * 100, 1) if total else 0
        lines.append(f"- **{category}**: {count} tickets ({percent}%)")

    lines.extend(["", "## Practical Improvements", ""])

    recs = df["recommendation"].value_counts().head(10)
    for rec, count in recs.items():
        lines.append(f"- {rec} ({count} related tickets)")

    lines.extend([
        "",
        "## Project Meaning",
        "",
        "This report shows how IT tickets can reveal human behaviour patterns such as memory load, technology anxiety, mental model gaps, training needs and security awareness.",
        "",
        "The aim is not to blame users. The aim is to improve systems, documentation, communication and employee experience."
    ])

    report = "\n".join(lines)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    Path(output_path).write_text(report, encoding="utf-8")

    print(f"Report created: {output_path}")
    return report

if __name__ == "__main__":
    print(generate_report())
