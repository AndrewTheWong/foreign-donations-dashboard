import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")
st.title("US University Foreign Donations Dashboard")
st.markdown("### Explore trends by school and country using data from 1981–2024")

# Load cleaned data
df = pd.read_csv("cleaned_foreign_donations.csv", parse_dates=["Date"])

# Sidebar: Year filter (expanded to 1981–2024)
start_year, end_year = st.sidebar.slider(
    "Select year range",
    min_value=1981,
    max_value=2024,
    value=(2015, 2024),
    step=1
)

# Optional: Country filter
all_countries = sorted(df["Country"].unique())
selected_countries = st.sidebar.multiselect(
    "Filter by country (optional)",
    options=all_countries,
    default=all_countries
)

# Filter data by year and country
filtered_df = df[
    (df["Date"].dt.year.between(start_year, end_year)) &
    (df["Country"].isin(selected_countries))
]

# Country flag map for display
flag_map = {
    "CHINA": "🇨🇳", "QATAR": "🇶🇦", "UNITED ARAB EMIRATES": "🇦🇪", "SAUDI ARABIA": "🇸🇦",
    "UNITED KINGDOM": "🇬🇧", "CANADA": "🇨🇦", "SINGAPORE": "🇸🇬", "GERMANY": "🇩🇪",
    "FRANCE": "🇫🇷", "SOUTH KOREA": "🇰🇷", "SWITZERLAND": "🇨🇭", "HONG KONG": "🇭🇰",
    "JAPAN": "🇯🇵", "INDIA": "🇮🇳", "MEXICO": "🇲🇽", "BRAZIL": "🇧🇷"
}

# ========== TABS ==========
tab1, tab2 = st.tabs(["🏫 Top US Universities", "🌍 Country Trends"])

# === TAB 1: Universities ===
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

    bar_fig = px.bar(
        school_summary,
        x="School",
        y="Total Donations",
        title="Top 30 Universities by Total Foreign Donations",
        labels={"School": "University"},
        color="Total Donations",
        hover_data={"Total Donations": ":,.0f"},
        color_continuous_scale="Reds"
    )
    bar_fig.update_layout(xaxis_tickangle=45)
    st.plotly_chart(bar_fig, use_container_width=True)

    st.markdown("---")
    st.subheader("🌐 Donation Breakdown by Country for Selected Schools")

    top_20_schools = school_summary["School"].tolist()[:20]
    all_schools = sorted(filtered_df["School"].unique())
    selected_schools = st.multiselect(
        "Choose universities to compare",
        options=all_schools,
        default=top_20_schools
    )

    breakdown = (
        filtered_df[filtered_df["School"].isin(selected_schools)]
        .groupby(["School", "Country"])["Amount"]
        .sum()
        .reset_index()
    )

    breakdown["Country Flagged"] = breakdown["Country"].apply(
        lambda c: f"{flag_map.get(c.upper(), '')} {c.title()}"
    )

    breakdown_fig = px.bar(
        breakdown,
        x="School",
        y="Amount",
        color="Country Flagged",
        title="Foreign Donations to Selected Schools by Country",
        hover_data={"Amount": ":,.0f"},
        height=700
    )
    breakdown_fig.update_layout(barmode="stack", xaxis_tickangle=45)
    st.plotly_chart(breakdown_fig, use_container_width=True)

    st.markdown("---")
    st.subheader("🌍 Total Donations by Country (Ordered Table)")

    country_table = (
        filtered_df.groupby("Country")["Amount"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
        .rename(columns={"Amount": "Total Donations"})
    )
    country_table["Country"] = country_table["Country"].apply(
        lambda c: f"{flag_map.get(c.upper(), '')} {c.title()}"
    )

    st.dataframe(country_table)

# === TAB 2: Country Trends ===
with tab2:
    st.subheader("📈 Foreign Donations by Country Over Time (Line Chart)")

    trend_df = (
        filtered_df.copy()
        .assign(Year=filtered_df["Date"].dt.year)
        .groupby(["Year", "Country"])["Amount"]
        .sum()
        .reset_index()
    )

    line_fig = px.line(
        trend_df,
        x="Year",
        y="Amount",
        color="Country",
        title="Donation Trends by Country (1981–2024)",
        markers=True,
        labels={"Amount": "Donation ($)"}
    )
    st.plotly_chart(line_fig, use_container_width=True)
