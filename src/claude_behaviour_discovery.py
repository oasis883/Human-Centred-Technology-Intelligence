"""
claude_behaviour_discovery.py

Automatically discovers recurring "issue -> trivial fix" behaviour patterns
from closed support tickets using the Claude API, and writes them to
reports/ai_behaviour_patterns.json.

Design: 50k tickets are far too large to send to an LLM directly, so we
aggregate locally first (group by subject, count repeat users, sample the
distinct phrasings), then send only the compact evidence summary to Claude.
Claude decides which groups represent genuine behavioural patterns and
returns structured JSON. Nothing about specific issue types (restarts,
temp files, etc.) is hardcoded anywhere in this file.

Usage:
    python src/claude_behaviour_discovery.py
    python src/claude_behaviour_discovery.py --input data/processed/tickets_clean.tsv
    python src/claude_behaviour_discovery.py --mock          # offline demo, no API call
    python src/claude_behaviour_discovery.py --dry-run       # print the prompt, don't call the API
"""

import json
import os
from pathlib import Path

from anthropic import Anthropic
from dotenv import load_dotenv


load_dotenv()

INPUT_FILE = Path("reports/pattern_evidence.json")
OUTPUT_FILE = Path("reports/ai_behaviour_patterns.json")


APPROVED_TELEMETRY_FIELDS = [
    "days_since_restart",
    "disk_free_percent",
    "temporary_file_size_mb",
    "application_cache_size_mb",
    "adobe_temp_size_mb",
    "teams_cache_size_mb",
    "browser_cache_size_mb",
    "pending_update_count",
    "failed_login_count",
    "account_lockout_count",
    "vpn_stale_session_count",
    "onedrive_sync_age_minutes",
    "print_queue_length",
    "device_memory_usage_percent",
    "device_cpu_usage_percent",
]


def clean_json_response(text: str) -> str:
    text = text.strip()

    if text.startswith("```json"):
        text = text.replace("```json", "", 1).strip()

    if text.startswith("```"):
        text = text.replace("```", "", 1).strip()

    if text.endswith("```"):
        text = text[:-3].strip()

    return text


def validate_pattern(pattern: dict) -> bool:
    required_fields = [
        "pattern_id",
        "pattern_name",
        "pattern_type",
        "confidence",
        "evidence",
        "behaviour_interpretation",
        "impact",
        "recommendation",
        "automation_opportunity",
    ]

    return all(field in pattern for field in required_fields)


def main() -> None:
    api_key = os.getenv("ANTHROPIC_API_KEY")

    if not api_key:
        raise EnvironmentError(
            "ANTHROPIC_API_KEY is missing from the .env file."
        )

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            "Pattern evidence is missing. Run "
            "python src/build_pattern_evidence.py first."
        )

    cluster_evidence = json.loads(
        INPUT_FILE.read_text(encoding="utf-8")
    )

    prompt = f"""
You are a human-centred technology and IT service-management analyst.

Analyse the supplied synthetic IT-support ticket clusters.

Your task is to identify recurring patterns involving:

- user habits;
- preventive-maintenance behaviour;
- training or knowledge gaps;
- repeated troubleshooting behaviour;
- technology friction;
- confusing system design;
- workflow or process problems;
- security-awareness behaviour;
- timing-related behaviour;
- repeated incidents with common successful resolutions;
- opportunities to prevent support demand.

Do not limit your analysis to restart, Adobe, passwords or any specific
technology. Discover patterns supported by the evidence.

Important rules:

1. Do not diagnose medical, psychological or cognitive conditions.
2. Describe observable behaviour carefully.
3. Ticket history may suggest a pattern but does not prove user intention.
4. Do not invent ticket counts, users, devices or resolutions.
5. Only recommend automation when a measurable condition can validate it.
6. Automation telemetry must use one of the approved fields below.
7. If no approved telemetry field is suitable, set supported to false.
8. Recommendations may include notification, training, documentation,
   workflow redesign, self-service, system improvement or automation.
9. Return the most important supported patterns, up to 10 patterns.
10. Return ONLY valid JSON. Do not use markdown fences.

Approved telemetry fields:

{json.dumps(APPROVED_TELEMETRY_FIELDS, indent=2)}

Every pattern must have this structure:

{{
  "pattern_id": "BP-001",
  "pattern_name": "Clear descriptive name",
  "pattern_type": "preventive_maintenance | training_gap | workflow_friction | system_design | security_behaviour | timing_pattern | repeated_resolution | user_habit",
  "confidence": 0.0,
  "source_cluster_ids": ["CL-001"],
  "evidence": {{
    "matching_ticket_count": 0,
    "affected_user_count": null,
    "affected_device_count": null,
    "common_issues": [],
    "common_resolutions": [],
    "evidence_summary": ""
  }},
  "behaviour_interpretation": {{
    "observed_pattern": "",
    "possible_explanation": "",
    "caution": ""
  }},
  "impact": {{
    "user_impact": "",
    "service_desk_impact": "",
    "business_impact": "",
    "severity": "low | medium | high",
    "impact_score": 0
  }},
  "recommendation": {{
    "intervention_type": "notification | training | documentation | self_service | workflow_redesign | system_improvement | monitoring",
    "recommended_action": "",
    "expected_benefit": ""
  }},
  "automation_opportunity": {{
    "supported": true,
    "telemetry_field": null,
    "operator": null,
    "suggested_threshold": null,
    "notification_template": null,
    "stop_condition": null,
    "reason": ""
  }}
}}

Impact score must be between 0 and 100.

Confidence must be between 0 and 1.

Cluster evidence:

{json.dumps(cluster_evidence, indent=2)}
"""

    client = Anthropic(api_key=api_key)

    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=8000,
        temperature=0.1,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )

    response_text = clean_json_response(
        message.content[0].text
    )

    patterns = json.loads(response_text)

    if not isinstance(patterns, list):
        raise ValueError(
            "Claude response must be a JSON list."
        )

    valid_patterns = [
        pattern
        for pattern in patterns
        if validate_pattern(pattern)
    ]

    valid_patterns = sorted(
        valid_patterns,
        key=lambda item: item["impact"]["impact_score"],
        reverse=True,
    )

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    OUTPUT_FILE.write_text(
        json.dumps(valid_patterns, indent=2),
        encoding="utf-8",
    )

    print(f"Behaviour patterns created: {len(valid_patterns)}")
    print(f"Patterns saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()