import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(layout="wide")
st.title("US University Foreign Donations Dashboard")
st.markdown("### Explore trends by country and see which US schools receive the most")

# Load cleaned data
df = pd.read_csv("cleaned_foreign_donations.csv", parse_dates=["Date"])

# Sidebar: Year filter
min_year = df["Date"].dt.year.min()
max_year = df["Date"].dt.year.max()
start_year, end_year = st.sidebar.slider(
    "Select year range",
    min_value=min_year,
    max_value=max_year,
    value=(2015, max_year),
    step=1
)

# Filter data by date
filtered_df = df[df["Date"].dt.year.between(start_year, end_year)]

# Tabs
tab1, tab2 = st.tabs(["🌍 Country Trends", "🏫 Top 30 Universities"])

# =======================
# 🌍 TAB 1: Country Trends
# =======================
with tab1:
    st.subheader("📊 Animated Foreign Donations by Country")

    summary = (
        filtered_df.groupby(["Date", "Country"])["Amount"]
        .sum()
        .reset_index()
    )

    bar_fig = px.bar(
        summary,
        x="Country",
        y="Amount",
        color="Country",
        animation_frame=summary["Date"].dt.year.astype(str),
        range_y=[0, summary["Amount"].max() * 1.1],
        title="Foreign Donations by Country Over Time"
    )
    st.plotly_chart(bar_fig, use_container_width=True)

    st.subheader("📈 Country Donation Trends (Line Chart)")

    line_df = summary.copy()
    line_df["Year"] = line_df["Date"].dt.year
    line_summary = line_df.groupby(["Year", "Country"])["Amount"].sum().reset_index()

    line_fig = px.line(
        line_summary,
        x="Year",
        y="Amount",
        color="Country",
        title="Donation Trends by Country Over Time"
    )
    st.plotly_chart(line_fig, use_container_width=True)

# ==========================
# 🏫 TAB 2: Top Universities
# ==========================
with tab2:
    st.subheader("🏫 Top 30 US Universities by Foreign Donations")

    school_summary = (
        filtered_df.groupby("School")["Amount"]
        .sum()
        .sort_values(ascending=False)
        .head(30)
        .reset_index()
        .rename(columns={"Amount": "Total Donations"})
    )

    school_fig = px.bar(
        school_summary,
        x="School",
        y="Total Donations",
        title="Top 30 Universities by Total Foreign Donations",
        labels={"School": "University"},
        color="Total Donations"
    )
    school_fig.update_layout(xaxis_tickangle=45)
    st.plotly_chart(school_fig, use_container_width=True)
