import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Human-Centred Technology Intelligence",
    page_icon="🧠",
    layout="wide"
)

st.title("🧠 Human-Centred Technology Intelligence")

st.caption("AI-powered behavioural analytics for IT support tickets")

df = pd.read_csv("data/processed/behaviour_classified_tickets.csv")

total = len(df)

memory = len(df[df["behaviour_category"] == "Memory / Access"])
communication = len(df[df["behaviour_category"] == "Communication / Collaboration"])
mental = len(df[df["behaviour_category"] == "Mental Model"])
security = len(df[df["behaviour_category"] == "Attention / Security"])

col1,col2,col3,col4,col5 = st.columns(5)

col1.metric("Tickets", total)
col2.metric("Memory", memory)
col3.metric("Communication", communication)
col4.metric("Mental Models", mental)
col5.metric("Security", security)

st.divider()

st.subheader("Behaviour Categories")

counts = df["behaviour_category"].value_counts()

st.bar_chart(counts)

st.divider()

st.subheader("Claude Executive Summary")

with open("reports/claude_summary.md","r",encoding="utf-8") as f:
    st.markdown(f.read())