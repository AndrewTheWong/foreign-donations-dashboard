import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")
st.title("US University Foreign Donations Dashboard")
st.markdown("### Explore trends by school and country using data from 1981–2024")

# Load cleaned data
df = pd.read_csv("cleaned_foreign_donations.csv", parse_dates=["Date"])

# Sidebar filters
start_year, end_year = st.sidebar.slider(
    "Select year range",
    min_value=1981,
    max_value=2024,
    value=(2015, 2024),
    step=1
)

# Country multiselect with Gulf states added
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

# Filter data
filtered_df = df[
    (df["Date"].dt.year.between(start_year, end_year)) &
    (df["Country"].isin(selected_countries))
]

# ==== Tabs ====
tab1, tab2, tab3, tab4 = st.tabs([
    "🏫 Top Universities",
    "🌍 Donations by Country",
    "📈 Country Trends",
    "🔍 School Breakdown"
])

# === TAB 1: Top Universities ===
with tab1:
    st.subheader("🏫 Top 30 US Universities by Total Foreign Donations")

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

    st.markdown("---")
    st.subheader("🌐 Donation Breakdown by Country for Selected Schools")

    top_20 = school_summary["School"].tolist()[:20]
    chosen_schools = st.multiselect(
        "Choose universities",
        sorted(filtered_df["School"].unique()),
        default=top_20
    )

    breakdown = (
        filtered_df[filtered_df["School"].isin(chosen_schools)]
        .groupby(["School", "Country"])["Amount"]
        .sum()
        .reset_index()
    )

    bar = px.bar(
        breakdown,
        x="School",
        y="Amount",
        color="Country",
        title="Foreign Donations to Selected Schools by Country",
        height=700,
        hover_data={"Amount": ":,.0f"}
    )
    bar.update_layout(barmode="stack", xaxis_tickangle=45)
    st.plotly_chart(bar, use_container_width=True)

# === TAB 2: Country Table ===
with tab2:
    st.subheader("🌍 Total Foreign Donations by Country (Ordered Table)")

    country_table = (
        filtered_df.groupby("Country")["Amount"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
        .rename(columns={"Amount": "Total Donations"})
    )
    st.dataframe(country_table)

# === TAB 3: Country Trends ===
with tab3:
    st.subheader("📈 Foreign Donations by Country Over Time")

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

# === TAB 4: School Breakdown ===
with tab4:
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
