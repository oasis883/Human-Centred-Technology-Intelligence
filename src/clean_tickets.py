from pathlib import Path
import re
import pandas as pd

EMAIL_PATTERN = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_PATTERN = re.compile(r"(\+?\d[\d\s().-]{7,}\d)")
IP_PATTERN = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")

def anonymise_text(value):
    if pd.isna(value):
        return ""
    text = str(value)
    text = EMAIL_PATTERN.sub("[EMAIL_REMOVED]", text)
    text = PHONE_PATTERN.sub("[PHONE_REMOVED]", text)
    text = IP_PATTERN.sub("[IP_REMOVED]", text)
    return text

def load_file(path):
    file_path = Path(path)
    suffix = file_path.suffix.lower()

    if suffix == ".tsv":
        return pd.read_csv(file_path, sep="\t", encoding="utf-8", encoding_errors="ignore", on_bad_lines="skip")
    if suffix == ".csv":
        return pd.read_csv(file_path, encoding="utf-8", encoding_errors="ignore", on_bad_lines="skip")
    if suffix == ".xlsx":
        return pd.read_excel(file_path)

    raise ValueError("Supported files: .tsv, .csv, .xlsx")

def clean_tickets(input_path="data/raw/tickets.tsv", output_path="data/processed/cleaned_tickets.csv"):
    input_file = Path(input_path)
    if not input_file.exists():
        raise FileNotFoundError(f"Ticket file not found: {input_path}")

    df = load_file(input_path)
    df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]

    private_keywords = ["email", "phone", "mobile", "requester", "name", "user"]
    columns_to_drop = [c for c in df.columns if any(k in c for k in private_keywords)]
    df = df.drop(columns=columns_to_drop, errors="ignore")

    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].apply(anonymise_text)

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)

    print(f"Cleaned file created: {output_path}")
    print(f"Rows cleaned: {len(df)}")
    return df

if __name__ == "__main__":
    clean_tickets()
