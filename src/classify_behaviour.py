from pathlib import Path
import pandas as pd

KEYWORDS = {
    "Memory / Access": ["password", "forgot", "reset", "mfa", "login", "signin", "sign in", "account locked"],
    "Attention / Security": ["phishing", "suspicious", "spam", "clicked", "warning", "alert"],
    "Mental Model": ["onedrive", "sharepoint", "network drive", "shared mailbox", "where is", "cannot find", "can't find"],
    "Technology Anxiety": ["urgent", "asap", "help", "can't work", "blocked", "critical"],
    "Training Gap": ["how do i", "instructions", "guide", "don't know", "not sure", "need help"],
    "Communication / Collaboration": ["teams", "zoom", "meeting", "calendar", "mailbox", "email"],
}

def choose_text_columns(df):
    possible = ["subject", "summary", "request_summary", "description", "details", "request_detail", "resolution", "notes"]
    found = [c for c in df.columns if c in possible]
    if found:
        return found
    return list(df.select_dtypes(include="object").columns)[:5]

def classify_text(text):
    text = str(text).lower()
    scores = {}
    for category, words in KEYWORDS.items():
        scores[category] = sum(1 for word in words if word in text)

    best = max(scores, key=scores.get)
    if scores[best] == 0:
        best = "General IT Support"

    recommendation = {
        "Memory / Access": "Simplify login, improve MFA/password guidance, consider SSO or passwordless options.",
        "Attention / Security": "Improve cyber awareness, warning messages and phishing reporting guidance.",
        "Mental Model": "Create simple visual guides explaining how the system works.",
        "Technology Anxiety": "Improve communication, reassurance and outage/status updates.",
        "Training Gap": "Create targeted training and self-service knowledge articles.",
        "Communication / Collaboration": "Improve Teams, Outlook and meeting-room support documentation.",
        "General IT Support": "Review recurring patterns and improve documentation."
    }

    return best, recommendation[best]

def classify_file(input_path="data/processed/cleaned_tickets.csv", output_path="data/processed/behaviour_classified_tickets.csv"):
    if not Path(input_path).exists():
        raise FileNotFoundError(f"Missing cleaned file: {input_path}. Run clean_tickets.py first.")

    df = pd.read_csv(input_path)
    text_cols = choose_text_columns(df)

    if text_cols:
        df["combined_text"] = df[text_cols].fillna("").astype(str).agg(" ".join, axis=1)
    else:
        df["combined_text"] = ""

    results = df["combined_text"].apply(classify_text)
    df["behaviour_category"] = results.apply(lambda x: x[0])
    df["recommendation"] = results.apply(lambda x: x[1])

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)

    print(f"Classified file created: {output_path}")
    print(f"Rows classified: {len(df)}")
    return df

if __name__ == "__main__":
    classify_file()
