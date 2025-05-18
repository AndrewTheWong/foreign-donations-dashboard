import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")
st.title("US University Foreign Donations Dashboard")
st.markdown("### Explore trends by school and country using data from 1981–2024")

# Load data
df = pd.read_csv("cleaned_foreign_donations.csv", parse_dates=["Date"])

# Sidebar filters
start_year, end_year = st.sidebar.slider(
    "Select year range",
    min_value=1981,
    max_value=2024,
    value=(2015, 2024),
    step=1
)

st.sidebar.markdown("### Country Filter")
st.sidebar.caption("🔍 Select countries to filter the data. Default shows top 10 donor countries.")
top_countries = df.groupby("Country")["Amount"].sum().sort_values(ascending=False).head(10).index.tolist()
all_countries = sorted(df["Country"].unique())
selected_countries = st.sidebar.multiselect(
    "Countries:",
    options=all_countries,
    default=top_countries
)

st.sidebar.markdown("---")
st.sidebar.markdown("### Credits")
st.sidebar.caption("Built by **Andrew Wong**  \nAll rights reserved.")
st.sidebar.markdown("📬 [Follow me on X @AndrewTheWong_](https://x.com/AndrewTheWong_)")

# Filter data
filtered_df = df[
    (df["Date"].dt.year.between(start_year, end_year)) &
    (df["Country"].isin(selected_countries))
]

# === TABS ===
tab1, tab2, tab3 = st.tabs([
    "🏫 School Breakdown",
    "📊 Compare Schools",
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
    formatted_table = school_data.copy()
    formatted_table["Total Donations"] = formatted_table["Total Donations"].map("${:,.0f}".format)
    st.dataframe(formatted_table, use_container_width=True, hide_index=True)


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
    
    st.markdown("### 📌 Donation Types Explained")
    st.markdown("""
- **Gift**: A voluntary contribution with no expectation of direct return. Often used to support general or targeted academic initiatives.
- **Restricted Gift**: A gift earmarked for a specific use—like a research center, scholarship fund, or endowed chair.
- **Contract**: A legally binding agreement where the donor (often a government or company) expects specific deliverables or outcomes in return.
    """)

    st.markdown("**📑 Breakdown of Contract vs Gift**")
    if "Type" in df.columns:
        type_breakdown = (
            filtered_df[filtered_df["School"] == selected_school]
            .groupby("Type")["Amount"]
            .sum()
            .reset_index()
        )
        pie_chart = px.pie(
            type_breakdown,
            names="Type",
            values="Amount",
            title=f"Donation Types to {selected_school} (Contracts vs Gifts)"
        )
        st.plotly_chart(pie_chart, use_container_width=True)
    else:
        st.info("No contract/gift type data available in dataset.")

# === TAB 2: Compare Schools ===
with tab2:
    st.subheader("🏛️ Top 10 US Universities by Total Foreign Donations")

    top_schools = (
        filtered_df.groupby("School")["Amount"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
        .rename(columns={"Amount": "Total Donations"})
    )
    top_schools["Total Donations"] = top_schools["Total Donations"].map("${:,.0f}".format)
    st.dataframe(top_schools, use_container_width=True, hide_index=True)

    st.markdown("**Bar Chart:**")
    top10_bar = px.bar(
        top_schools,
        x="School",
        y="Total Donations",
        title="Top 10 Universities by Total Foreign Donations",
        color="Total Donations",
        color_continuous_scale="Reds",
        hover_data={"Total Donations": True}
    )
    top10_bar.update_layout(xaxis_tickangle=45)
    st.plotly_chart(top10_bar, use_container_width=True)

    st.markdown("### 📊 Donation Breakdown by Country for Selected Schools (Ordered Table)")

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

    breakdown_table = (
        filtered_df[filtered_df["School"].isin(chosen_schools)]
        .groupby(["School", "Country"])["Amount"]
        .sum()
        .reset_index()
        .sort_values(by="Amount", ascending=False)
        .rename(columns={"Amount": "Total Donations"})
    )
    breakdown_table["Total Donations"] = breakdown_table["Total Donations"].map("${:,.0f}".format)
    st.dataframe(breakdown_table, use_container_width=True, hide_index=True)

    st.markdown("### 📊 Visual Breakdown of Foreign Donations to Selected Schools")

    chart_data = (
        filtered_df[
            (filtered_df["School"].isin(chosen_schools)) &
            (filtered_df["Country"].isin(selected_countries))
        ]
        .groupby(["School", "Country"])["Amount"]
        .sum()
        .reset_index()
    )

    school_country_bar = px.bar(
        chart_data,
        x="School",
        y="Amount",
        color="Country",
        title="Foreign Donations by Country for Selected Schools",
        height=600,
        hover_data={"Amount": ":,.0f"}
    )
    school_country_bar.update_layout(barmode="stack", xaxis_tickangle=45)
    st.plotly_chart(school_country_bar, use_container_width=True)


# === TAB 3: Donations by Country ===
with tab3:
    st.markdown("### 🌍 Total Foreign Donations by Country (Ordered Table)")
    country_table = (
        filtered_df.groupby("Country")["Amount"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
        .rename(columns={"Amount": "Total Donations"})
    )
    country_table["Total Donations"] = country_table["Total Donations"].map("${:,.0f}".format)
    st.dataframe(country_table, use_container_width=True, hide_index=True)

    st.markdown("### 📌 Donation Types Explained")
    st.markdown("""
- **Gift**: A voluntary contribution with no expectation of direct return. Often used to support general or targeted academic initiatives.
- **Restricted Gift**: A gift earmarked for a specific use—like a research center, scholarship fund, or endowed chair.
- **Contract**: A legally binding agreement where the donor (often a government or company) expects specific deliverables or outcomes in return.
    """)

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

