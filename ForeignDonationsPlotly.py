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

    bar_fig_
