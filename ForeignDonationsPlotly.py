import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")
st.title("US University Foreign Donations Dashboard")
st.markdown("### Explore trends by school and country using data from 1981–2024")

# Load data
df = pd.read_csv("cleaned_foreign_donations.csv", parse_dates=["Date"])

# Sidebar: Filters
start_year, end_year = st.sidebar.slider(
    "Select year range",
    min_value=1981,
    max_value=2024,
    value=(2015, 2024),
    step=1
)

all_countries = sorted(df["Country"].unique())
default_countries = [
    "QATAR", "CHINA", "CANADA", "GERMANY",
    "UNITED KINGDOM", "SOUTH KOREA", "JAPAN", "FRANCE",
    "UNITED ARAB EMIRATES", "SAUDI ARABIA"
]
selected_countries = st.sidebar.multiselect(
    "Filter by country",
    options=all_countries,
    default=[c for c in all_countries if c.upper() in default_countries]
)

# Filter dataset
filtered_df = df[
    (df["Date"].dt.year.between(start_year, end_year)) &
    (df["Country"].isin(selected_countries))
]

# Tabs
tab1, tab2 = st.tabs([
    "🏫 School Breakdown",
    "🌍 Donations by Country"
])

# === TAB 1: School Breakdown ===
with tab1:
    st.subheader("🔍 Donations to a Specific School by Country")

    selected_school = st.selectbox("Choose a university", sorted(filtered_df["School"].unique()))

    school_data = (
        filtered_df[filtered_df["School"] == selected_school]
        .groupby("Country")["Amount"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
        .rename(columns={"Amount": "Total Donations"})
    )

    st.markdown("**Ordered Table of Donations by Country:**")
    st.dataframe(school_data)

    st.markdown("**Bar Chart:**")
    school_fig = px.bar(
        school_data,
        x="Country",
        y="Total Donations",
        title=f"Donations to {selected_school} by Country",
        hover_data={"Total Donations": ":,.0f"}
    )
    school_fig.update_layout(xaxis_tickangle=45)
    st.plotly_chart(school_fig, use_container_width=True)

    st.markdown("**Line Chart (Donations Over Time):**")
    school_trend = (
        filtered_df[filtered_df["School"] == selected_school]
        .assign(Year=filtered_df["Date"].dt.year)
        .groupby("Year")["Amount"]
        .sum()
        .reset_index()
    )
    school_line = px.line(
        school_trend,
        x="Year",
        y="Amount",
        title=f"{selected_school} Foreign Donations Over Time",
        markers=True,
        labels={"Amount": "Donation ($)"}
    )
    st.plotly_chart(school_line, use_container_width=True)

    st.markdown("---")
    st.subheader("📊 Donation Breakdown by Country for Selected Schools")

    default_schools = [
        "Harvard University", "Yale University", "Princeton University", "Columbia University",
        "University of Pennsylvania", "Brown University", "Dartmouth College", "Cornell University",
        "Stanford University", "University of California-Berkeley", "University of California-Los Angeles",
        "Duke University", "Georgetown University"
    ]

    chosen_schools = st.multiselect(
        "Choose universities to compare",
        sorted(filtered_df["School"].unique()),
        default=[s for s in default_schools if s in filtered_df["School"].unique()]
    )

    breakdown = (
        filtered_df[filtered_df["School"].isin(chosen_schools)]
        .groupby(["School", "Country"])["Amount"]
        .sum()
        .reset_index()
    )

    comparison_bar = px.bar(
        breakdown,
        x="School",
        y="Amount",
        color="Country",
        title="Foreign Donations to Selected Schools by Country",
        height=700,
        hover_data={"Amount": ":,.0f"}
    )
    comparison_bar.update_layout(barmode="stack", xaxis_tickangle=45)
    st.plotly_chart(comparison_bar, use_container_width=True)

# === TAB 2: Donations by Country ===
with tab2:
    st.subheader("🏛️ Top 30 US Universities by Total Foreign Donations")

    school_summary = (
        filtered_df.groupby("School")["Amount"]
        .sum()
        .sort_values(ascending=False)
        .head(30)
        .reset_index()
        .rename(columns={"Amount": "Total Donations"})
    )

    fig = px.bar(
        school_summary,
        x="School",
        y="Total Donations",
        color="Total Donations",
        title="Top 30 Universities by Total Foreign Donations",
        hover_data={"Total Donations": ":,.0f"},
        color_continuous_scale="Reds"
    )
    fig.update_layout(xaxis_tickangle=45)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 🌍 Total Foreign Donations by Country (Ordered Table)")
    country_table = (
        filtered_df.groupby("Country")["Amount"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
        .rename(columns={"Amount": "Total Donations"})
    )
    st.dataframe(country_table)

    st.markdown("### 📈 Foreign Donations by Country Over Time")
    trend_data = (
        filtered_df.copy()
        .assign(Year=filtered_df["Date"].dt.year)
        .groupby(["Year", "Country"])["Amount"]
        .sum()
        .reset_index()
    )

    trend_fig = px.line(
        trend_data,
        x="Year",
        y="Amount",
        color="Country",
        title="Donation Trends by Country (1981–2024)",
        markers=True,
        labels={"Amount": "Donation ($)"}
    )
    st.plotly_chart(trend_fig, use_container_width=True)
