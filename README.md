# HumanTech Intelligence

A beginner-friendly portfolio project showing how IT support tickets can be analysed using Python, psychology, AI and SaaS integrations.

## Workflow

```text
Ticket Export
→ Python Cleaning
→ Behaviour Classification
→ Insights Report
→ Claude API Summary
→ Slack Notification
→ GitHub Actions
```

## Privacy by design

Real ticket data is not uploaded to GitHub. The `.gitignore` blocks raw data, processed data, reports and `.env`.

## How to run

Put your ticket export here:

```text
data/raw/tickets.tsv
```

Then run:

```powershell
python src/run_pipeline.py
```

Open:

```text
reports/insights_report.md
```

## Optional

Claude:

```powershell
python src/claude_summary.py
```

Slack:

```powershell
python src/slack_notify.py
```

## What this demonstrates

Python, ITSM data, privacy-aware handling, behavioural analytics, Claude API, Slack webhook, GitHub Actions, and basic OAuth/SAML/token-auth awareness.
