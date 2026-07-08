from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


DATA_PATH = Path("data/processed/behaviour_classified_tickets.csv")
CLAUDE_SUMMARY_PATH = Path("reports/claude_summary.md")
INSIGHTS_REPORT_PATH = Path("reports/insights_report.md")

st.set_page_config(
    page_title="Human-Centred Technology Intelligence",
    page_icon="🧠",
    layout="wide",
)

@st.cache_data
def load_data():
    return pd.read_csv(DATA_PATH)

def load_text(path):
    if path.exists():
        return path.read_text(encoding="utf-8")
    return "File not found. Run the pipeline first."

df = load_data()

st.title("🧠 Human-Centred Technology Intelligence")
st.caption("AI-powered behavioural analytics for synthetic IT support tickets")

with st.sidebar:
    st.header("🔎 Filters")

    categories = sorted(df["behaviour_category"].dropna().unique())

    selected_categories = st.multiselect(
        "Behaviour Category",
        categories,
        default=categories,
    )

    search_text = st.text_input("Search ticket text")

    st.divider()

    st.markdown("### Project Workflow")
    st.markdown("""
    Synthetic Tickets  
    → Python Pipeline  
    → Behaviour Analysis  
    → Claude Summary  
    → Slack Notification  
    → Dashboard
    """)

filtered = df[df["behaviour_category"].isin(selected_categories)]

if search_text:
    filtered = filtered[
        filtered["combined_text"]
        .fillna("")
        .str.contains(search_text, case=False, na=False)
    ]

total_tickets = len(filtered)
category_counts = filtered["behaviour_category"].value_counts()

top_category = category_counts.index[0] if len(category_counts) > 0 else "N/A"
top_count = int(category_counts.iloc[0]) if len(category_counts) > 0 else 0

st.subheader("📊 Executive Overview")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Tickets", f"{total_tickets:,}")
col2.metric("Behaviour Categories", len(category_counts))
col3.metric("Top Behaviour", top_category)
col4.metric("Top Behaviour Count", f"{top_count:,}")

st.divider()

tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Behaviour Analytics",
    "🤖 AI Summary",
    "🔎 Ticket Explorer",
    "📄 Reports",
])

with tab1:
    st.subheader("Behaviour Distribution")

    chart_df = category_counts.reset_index()
    chart_df.columns = ["Behaviour Category", "Ticket Count"]

    fig = px.bar(
        chart_df,
        x="Behaviour Category",
        y="Ticket Count",
        text="Ticket Count",
        title="Tickets by Behaviour Category",
    )

    fig.update_traces(textposition="outside")
    fig.update_layout(xaxis_tickangle=-25)

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Percentage Breakdown")

    pie_fig = px.pie(
        chart_df,
        names="Behaviour Category",
        values="Ticket Count",
        title="Behaviour Category Share",
        hole=0.4,
    )

    st.plotly_chart(pie_fig, use_container_width=True)

with tab2:
    st.subheader("Claude Executive Summary")
    st.markdown(load_text(CLAUDE_SUMMARY_PATH))

with tab3:
    st.subheader("Ticket Explorer")

    display_cols = [
        c for c in ["behaviour_category", "recommendation", "combined_text"]
        if c in filtered.columns
    ]

    st.dataframe(
        filtered[display_cols].head(200),
        use_container_width=True,
        height=500,
    )

with tab4:
    st.subheader("Download Reports")

    st.download_button(
        label="⬇ Download Insights Report",
        data=load_text(INSIGHTS_REPORT_PATH),
        file_name="human_centred_technology_insights.md",
        mime="text/markdown",
    )

    st.download_button(
        label="⬇ Download Filtered Tickets CSV",
        data=filtered.to_csv(index=False),
        file_name="filtered_tickets.csv",
        mime="text/csv",
    )

st.divider()

st.caption(
    "Built as a personal portfolio project to explore how IT support data, AI, and behavioural science can improve human-centred technology experiences."
)