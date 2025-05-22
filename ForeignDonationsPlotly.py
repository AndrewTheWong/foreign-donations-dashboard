import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(layout="wide")
st.title("US University Foreign Donations Dashboard")
st.markdown("### Explore trends by school and country using data from 1981–2024")

# Load and clean data
df = pd.read_csv("cleaned_foreign_donations.csv", parse_dates=["Date"])
df.columns = df.columns.str.strip()
if "Country" not in df.columns:
    raise ValueError("Missing 'Country' column in the dataset.")
df = df[df["Country"].notna()]

# Sidebar filters
start_year, end_year = st.sidebar.slider("Select year range", 1981, 2024, (2015, 2024), step=1)

st.sidebar.markdown("### Country Filter")
st.sidebar.caption("🔍 Select countries to filter the data.")
top_countries = df.groupby("Country")["Amount"].sum().sort_values(ascending=False).head(5).index.tolist()
all_countries = sorted(df["Country"].unique())

if "selected_countries" not in st.session_state:
    st.session_state.selected_countries = top_countries

if st.sidebar.button("Select All Countries"):
    st.session_state.selected_countries = all_countries
if st.sidebar.button("Top 5 Countries"):
    st.session_state.selected_countries = top_countries
if st.sidebar.button("Clear Selection"):
    st.session_state.selected_countries = []

selected_countries = st.sidebar.multiselect("Countries:", options=all_countries, default=st.session_state.selected_countries, key="selected_countries")

st.sidebar.markdown("---")
st.sidebar.markdown("### Credits")
st.sidebar.caption("Built by **Andrew Wong** All rights reserved.")
st.sidebar.markdown("📬 [Follow me on X @AndrewTheWong_](https://x.com/AndrewTheWong_)")

# Filter data
filtered_df = df[(df["Date"].dt.year.between(start_year, end_year)) & (df["Country"].isin(selected_countries))]

tab1, tab2, tab3 = st.tabs(["🏫 School Breakdown", "📊 Compare Schools", "🌍 Donations by Country"])

# TAB 1
with tab1:
    st.subheader("🔍 Donations to a Specific School by Country")
    selected_school = st.selectbox("Choose a university", sorted(filtered_df["School"].unique()))
    school_data = filtered_df[filtered_df["School"] == selected_school].groupby("Country")["Amount"].sum().sort_values(ascending=False).reset_index().rename(columns={"Amount": "Total Donations"})
    st.markdown("**Ordered Table of Donations by Country:**")
    formatted_table = school_data.copy()
    formatted_table["Total Donations"] = formatted_table["Total Donations"].map("${:,.0f}".format)
    st.dataframe(formatted_table, use_container_width=True, hide_index=True)
    st.markdown("**Bar Chart:**")
    school_fig = px.bar(school_data, x="Country", y="Total Donations", title=f"Donations to {selected_school} by Country", hover_data={"Total Donations": ":,.0f"})
    school_fig.update_layout(xaxis_tickangle=45)
    st.plotly_chart(school_fig, use_container_width=True)
    st.markdown("**Line Chart (Donations Over Time):**")
    school_trend = filtered_df[filtered_df["School"] == selected_school].assign(Year=filtered_df["Date"].dt.year).groupby("Year")["Amount"].sum().reset_index()
    school_line = px.line(school_trend, x="Year", y="Amount", title=f"{selected_school} Foreign Donations Over Time", markers=True, labels={"Amount": "Donation ($)"})
    st.plotly_chart(school_line, use_container_width=True)
    st.markdown("### 📌 Donation Types Explained")
    st.markdown("""- **Gift**: A voluntary contribution with no expectation of direct return.
- **Restricted Gift**: A gift earmarked for a specific use.
- **Contract**: A legally binding agreement with expected outcomes.""")
    st.markdown("**📑 Breakdown of Contract vs Gift**")
    if "Type" in df.columns:
        type_breakdown = filtered_df[filtered_df["School"] == selected_school].groupby("Type")["Amount"].sum().reset_index()
        pie_chart = px.pie(type_breakdown, names="Type", values="Amount", title=f"Donation Types to {selected_school}")
        st.plotly_chart(pie_chart, use_container_width=True)
    else:
        st.info("No contract/gift type data available.")

# TAB 2
with tab2:
    st.subheader("🏛️ Top 10 US Universities by Total Foreign Donations")

    top_schools_bar = filtered_df.groupby("School")["Amount"].sum().sort_values(ascending=False).head(10).reset_index()
    top10_schools_list = top_schools_bar["School"].tolist()

    chosen_schools = st.multiselect("Choose universities to compare", sorted(df["School"].unique()), default=top10_schools_list)

    school_totals = df[df["School"].isin(chosen_schools)].groupby("School")["Amount"].sum().reset_index()
    country_breakdowns = filtered_df[(filtered_df["School"].isin(chosen_schools)) & (filtered_df["Country"].isin(selected_countries))].groupby(["School", "Country"])["Amount"].sum().reset_index()

    color_map = {
        "CHINA": "#de2910", "QATAR": "#8A1538", "ENGLAND": "#00247d",
        "SAUDI ARABIA": "#006C35", "CANADA": "#ff0000"
    }

    sorted_schools = school_totals.sort_values("Amount", ascending=False)["School"].tolist()
    fig = go.Figure()

    # Reference total bar
    fig.add_trace(go.Bar(
        x=sorted_schools,
        y=school_totals.set_index("School").loc[sorted_schools]["Amount"],
        name="Total Donations (Reference)",
        marker_color="lightgray",
        opacity=0.3,
        hoverinfo="skip",
        showlegend=True,
        offsetgroup="reference"
    ))

    # Maintain a tracker for the current top of the stack per school
    current_height = {school: 0 for school in sorted_schools}

    for school in sorted_schools:
        school_data = country_breakdowns[country_breakdowns["School"] == school].sort_values("Amount", ascending=False)
        for _, row in school_data.iterrows():
            y_val = row["Amount"]
            base_val = current_height[school]

            fig.add_trace(go.Bar(
                x=[school],
                y=[y_val],
                name=row["Country"],
                marker_color=color_map.get(row["Country"].upper(), None),
                hovertemplate=f"{row['Country']}: $%{{y:,.0f}}<extra></extra>",
                offsetgroup="schools",
                base=base_val,
                showlegend=(school == sorted_schools[0])
            ))

            current_height[school] += y_val  # update stack height

    fig.update_layout(
        title="Foreign Donations by Country for Selected Schools",
        barmode="relative",
        xaxis_tickangle=45,
        height=600
    )

    st.plotly_chart(fig, use_container_width=True)

# TAB 3
with tab3:
    st.markdown("### 🌍 Total Foreign Donations by Country (Ordered Table)")
    country_table = filtered_df.groupby("Country")["Amount"].sum().sort_values(ascending=False).reset_index().rename(columns={"Amount": "Total Donations"})
    country_table["Total Donations"] = country_table["Total Donations"].map("${:,.0f}".format)
    st.dataframe(country_table, use_container_width=True, hide_index=True)
    st.markdown("### 📈 Foreign Donations by Country Over Time")
    trend_data = filtered_df.copy().assign(Year=filtered_df["Date"].dt.year).groupby(["Year", "Country"])["Amount"].sum().reset_index()
    trend_fig = px.line(trend_data, x="Year", y="Amount", color="Country", title="Donation Trends by Country (1981–2024)", markers=True, labels={"Amount": "Donation ($)"})
    st.plotly_chart(trend_fig, use_container_width=True)
