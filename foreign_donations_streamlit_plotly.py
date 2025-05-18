
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(layout="wide")
st.title("Top 30 US Universities by Foreign Donations")
st.markdown("### Explore foreign donations from all countries to U.S. universities (2024 data)")

# Load the enhanced data file
df = pd.read_csv("top30_donations_all_countries.csv", index_col=0)

# Sidebar filters
country_cols = [col for col in df.columns if col not in ["Total Foreign Donations"]]
selected_countries = st.sidebar.multiselect(
    "Select countries to display (stacked in order)",
    country_cols,
    default=["QATAR", "CHINA", "UNITED ARAB EMIRATES", "SAUDI ARABIA"]
)

top_n = st.sidebar.slider("Number of universities to show", 5, 30, 30)
plot_df = df.head(top_n)

# Build stacked bar chart
fig = go.Figure()

# Stacked base
bottom = pd.Series([0] * len(plot_df), index=plot_df.index)

for country in selected_countries:
    fig.add_trace(go.Bar(
        x=plot_df.index,
        y=plot_df[country],
        name=country.title(),
        hovertemplate='%{x}<br>' + country.title() + ': $%{y:,.0f}<extra></extra>'
    ))

# Add total as reference line
fig.add_trace(go.Scatter(
    x=plot_df.index,
    y=plot_df["Total Foreign Donations"],
    mode="markers+text",
    text=[f"${val/1e6:.1f}M" for val in plot_df["Total Foreign Donations"]],
    textposition="top center",
    name="Total",
    marker=dict(color="lightgray", size=1),
    showlegend=False
))

fig.update_layout(
    barmode='stack',
    height=700,
    xaxis_tickangle=-45,
    yaxis_title='Donation Amount (USD)',
    title='Top 30 US Universities by Foreign Donations',
    legend_title_text='Country'
)

st.plotly_chart(fig, use_container_width=True)
