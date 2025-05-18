import streamlit as st
import pandas as pd
import plotly.express as px
import emoji

st.set_page_config(layout="wide")
st.title("US University Foreign Donations Dashboard")
st.markdown("### Explore trends by school and country using data from 1981–2024")

# Load cleaned data
df = pd.read_csv("cleaned_foreign_donations.csv", parse_dates=["Date"])

# Sidebar: Year and country filters
start_year, end_year = st.sidebar.slider(
    "Select year range",
    min_value=1981,
    max_value=2024,
    value=(2015, 2024),
    step=1
)

all_countries = sorted(df["Country"].unique())
selected_country = st.sidebar.selectbox("Filter by country (optional)", ["All"] + all_countries)
selected_countries = all_countries if selected_country == "All" else [selected_country]

filtered_df = df[
    (df["Date"].dt.year.between(start_year, end_year)) &
    (df["Country"].isin(selected_countries))
]

# Helper function to get flag emoji
def flag_emoji(country):
    try:
        return emoji.emojize(f":{country.strip().replace(' ', '_').upper()}:", language="alias")
    except:
        return "🌍"

# Create pseudo-tabs using a dropdown
tab_labels = {
    "🏫 Top Universities": "tab1",
    "🌍 Donations by Country": "tab2",
    "📈 Country Trends": "tab3",
    "🔍 School Breakdown": "tab4"
}

selected_tab = st.selectbox("Navigate to section", list(tab_labels.keys()))

# === TAB 1: Top Universities ===
if selected_tab == "🏫 Top Universities":
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

    breakdown["Country Flagged"] = breakdown["Country"].apply(lambda c: f"{flag_emoji(c)} {c.title()}")

    bar = px.bar(
        breakdown,
        x="School",
        y="Amount",
        color="Country Flagged",
        title="Foreign Donations to Selected Schools by Country",
        height=700,
        hover_data={"Amount": ":,.0f"}
    )
    bar.update_layout(barmode="stack", xaxis_tickangle=45)
    st.plotly_chart(bar, use_container_width=True)

# === TAB 2: Country Totals ===
elif selected_tab == "🌍 Donations by Country":
    st.subheader("🌍 Total Foreign Donations by Country (Ordered Table)")

    country_table = (
        filtered_df.groupby("Country")["Amount"]
