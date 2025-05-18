import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")
st.title("US University Foreign Donations Dashboard")
st.markdown("### Explore trends, filter by school, and profile top donor countries")

# Load cleaned data (ensure it's in the same folder)
df = pd.read_csv("cleaned_foreign_donations.csv", parse_dates=["Date"])

# Sidebar: Year range slider
min_year = df["Date"].dt.year.min()
max_year = df["Date"].dt.year.max()
start_year, end_year = st.sidebar.slider(
    "Select year range",
    min_value=min_year,
    max_value=max_year,
    value=(2015, max_year),
    step=1
)

# Sidebar: University search
unique_schools = sorted(df["School"].unique())
selected_school = st.sidebar.selectbox(
    "Highlight a university (optional)",
    ["All"] + unique_schools
)

# Filter by date range
filtered_df = df[df["Date"].dt.year.between(start_year, end_year)]

# Filter by selected university
if selected_school != "All":
    filtered_df = filtered_df[filtered_df["School"] == selected_school]

# =====================
# 📊 Animated Chart
# =====================
st.subheader("📊 Foreign Donation Flow by Country (Animated)")
summary = (
    filtered_df.groupby(["Date", "Country"])["Amount"]
    .sum()
    .reset_index()
)

fig = px.bar(
    summary,
    x="Country",
    y="Amount",
    color="Country",
    animation_frame=summary["Date"].dt.year.astype(str),
    range_y=[0, summary["Amount"].max() * 1.1],
    title="Foreign Donations by Country Over Time"
)
st.plotly_chart(fig, use_container_width=True)

# =====================
# 🌐 Country Profile
# =====================
st.subheader("🌐 Country Profile")
selected_country = st.selectbox("Select a country to view profile", sorted(df["Country"].unique()))

country_data = df[df["Country"] == selected_country]
total = country_data["Amount"].sum()
top_schools = (
    country_data.groupby("School")["Amount"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
)

st.markdown(f"**Total Donations from {selected_country.title()}:** ${total:,.0f}")
st.markdown("**Top Recipient Schools:**")
st.dataframe(top_schools.reset_index().rename(columns={"Amount": "Total Donations"}))
