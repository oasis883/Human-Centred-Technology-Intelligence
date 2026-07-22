import json
import re
from pathlib import Path

import pandas as pd
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer


INPUT_FILE = Path("data/processed/behaviour_classified_tickets.csv")
OUTPUT_FILE = Path("reports/pattern_evidence.json")

MAX_CLUSTERS = 20
SAMPLE_TICKETS_PER_CLUSTER = 8


def clean_text(value: object) -> str:
    if pd.isna(value):
        return ""

    text = str(value).lower()
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def find_first_column(
    dataframe: pd.DataFrame,
    candidates: list[str],
) -> str | None:
    normalised = {
        column.lower().strip(): column
        for column in dataframe.columns
    }

    for candidate in candidates:
        if candidate.lower() in normalised:
            return normalised[candidate.lower()]

    return None


def build_issue_text(dataframe: pd.DataFrame) -> pd.Series:
    if "combined_text" in dataframe.columns:
        return dataframe["combined_text"].fillna("").astype(str)

    candidate_columns = [
        "Subject",
        "Request Detail",
        "Description",
        "Issue",
        "Ticket",
        "Summary",
    ]

    available = [
        column
        for column in candidate_columns
        if column in dataframe.columns
    ]

    if not available:
        raise ValueError(
            "Could not find ticket-description columns. "
            "Add combined_text or one of: Subject, Request Detail, "
            "Description, Issue, Ticket or Summary."
        )

    return (
        dataframe[available]
        .fillna("")
        .astype(str)
        .agg(" ".join, axis=1)
    )


def build_resolution_text(dataframe: pd.DataFrame) -> pd.Series:
    candidate_columns = [
        "resolution",
        "Resolution",
        "resolution_text",
        "Notes",
        "Close Notes",
        "Closure Notes",
        "Technician Notes",
    ]

    available = [
        column
        for column in candidate_columns
        if column in dataframe.columns
    ]

    if not available:
        return pd.Series(
            [""] * len(dataframe),
            index=dataframe.index,
        )

    return (
        dataframe[available]
        .fillna("")
        .astype(str)
        .agg(" ".join, axis=1)
    )


def extract_top_terms(
    vectorizer: TfidfVectorizer,
    cluster_center,
    number_of_terms: int = 10,
) -> list[str]:
    terms = vectorizer.get_feature_names_out()

    top_indexes = cluster_center.argsort()[-number_of_terms:][::-1]

    return [
        terms[index]
        for index in top_indexes
    ]


def main() -> None:
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Input file not found: {INPUT_FILE}"
        )

    df = pd.read_csv(INPUT_FILE)

    df["issue_text"] = build_issue_text(df).apply(clean_text)
    df["resolution_text"] = build_resolution_text(df).apply(clean_text)

    df = df[df["issue_text"].str.len() > 10].copy()

    if len(df) < 2:
        raise ValueError("Not enough ticket records to discover patterns.")

    user_column = find_first_column(
        df,
        [
            "user_id",
            "Client",
            "Requester",
            "Requested By",
            "User",
        ],
    )

    device_column = find_first_column(
        df,
        [
            "device_id",
            "Device",
            "Computer Name",
            "Asset",
            "Hostname",
        ],
    )

    department_column = find_first_column(
        df,
        [
            "department",
            "Department",
            "Business Unit",
            "Location",
        ],
    )

    number_of_clusters = min(
        MAX_CLUSTERS,
        max(2, int(len(df) ** 0.5)),
        len(df),
    )

    vectorizer = TfidfVectorizer(
        stop_words="english",
        max_features=4000,
        ngram_range=(1, 2),
        min_df=2,
        max_df=0.95,
    )

    matrix = vectorizer.fit_transform(df["issue_text"])

    model = KMeans(
        n_clusters=number_of_clusters,
        random_state=42,
        n_init=10,
    )

    df["cluster_id"] = model.fit_predict(matrix)

    evidence = []

    for cluster_id in sorted(df["cluster_id"].unique()):
        cluster_df = df[df["cluster_id"] == cluster_id].copy()

        if cluster_df.empty:
            continue

        top_terms = extract_top_terms(
            vectorizer,
            model.cluster_centers_[cluster_id],
        )

        resolution_counts = (
            cluster_df["resolution_text"]
            .replace("", pd.NA)
            .dropna()
            .value_counts()
            .head(5)
        )

        common_resolutions = [
            {
                "resolution": resolution,
                "count": int(count),
            }
            for resolution, count in resolution_counts.items()
        ]

        record = {
            "cluster_id": f"CL-{cluster_id + 1:03d}",
            "ticket_count": int(len(cluster_df)),
            "top_terms": top_terms,
            "common_resolutions": common_resolutions,
            "sample_tickets": (
                cluster_df["issue_text"]
                .drop_duplicates()
                .head(SAMPLE_TICKETS_PER_CLUSTER)
                .tolist()
            ),
            "sample_resolution_text": (
                cluster_df["resolution_text"]
                .replace("", pd.NA)
                .dropna()
                .drop_duplicates()
                .head(SAMPLE_TICKETS_PER_CLUSTER)
                .tolist()
            ),
        }

        if user_column:
            record["affected_user_count"] = int(
                cluster_df[user_column].nunique()
            )

        if device_column:
            record["affected_device_count"] = int(
                cluster_df[device_column].nunique()
            )

        if department_column:
            record["affected_departments"] = (
                cluster_df[department_column]
                .dropna()
                .astype(str)
                .value_counts()
                .head(5)
                .index
                .tolist()
            )

        evidence.append(record)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    OUTPUT_FILE.write_text(
        json.dumps(evidence, indent=2),
        encoding="utf-8",
    )

    print(f"Ticket clusters created: {len(evidence)}")
    print(f"Evidence saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()