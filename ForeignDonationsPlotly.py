import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(layout="wide")
st.title("Top 30 US Universities by Foreign Donations")
st.markdown("### Explore foreign donations from top 10 countries to U.S. universities (2024 data)")

# Load corrected data
df = pd.read_csv("top30_donations_top10countries_corrected.csv", index_col=0)

# Flag emoji map (cover all top 10 countries)
flag_map = {
    "CHINA": "🇨🇳",
    "QATAR": "🇶🇦",
    "UNITED ARAB EMIRATES": "🇦🇪",
    "SAUDI ARABIA": "🇸🇦",
    "UNITED KINGDOM": "🇬🇧",
    "CANADA": "🇨🇦",
    "SINGAPORE": "🇸🇬",
    "GERMANY": "🇩🇪",
    "FRANCE": "🇫🇷",
    "SOUTH KOREA": "🇰🇷"
}

# Color map (flag-inspired)
color_map = {
    "CHINA": "#de2910",
    "QATAR": "#8D1B3D",
    "UNITED ARAB EMIRATES": "#00732F",
    "SAUDI ARABIA": "#006C35",
    "UNITED KINGDOM": "#00247D",
    "CANADA": "#FF0000",
    "SINGAPORE": "#EF3340",
    "GERMANY": "#000000",
    "FRANCE": "#0055A4",
    "SOUTH KOREA": "#003478"
}

# Filter for country columns
country_cols = [col for col in df.columns if col != "Total Foreign Donations"]

# Sidebar filters
selected_countries = st.sidebar.multiselect(
    "Select countries to display (stacked in order)",
    country_cols,
    default=country_cols
)

top_n = st.sidebar.slider("Number of universities to show", 5, 30, 30)
plot_df = df.head(top_n)

# Initialize figure
fig = go.Figure()

# Add background total bar (light gray)
fig.add_trace(go.Bar(
    x=plot_df.index,
    y=plot_df["Total Foreign Donations"],
    name="Total Foreign Donations",
    marker_color="lightgray",
    opacity=0.3,
    hovertemplate='<b>%{x}</b><br>Total: $%{y:,.0f}<extra></extra>'
))

# Add stacked country bars
for country in selected_countries:
    emoji = flag_map.get(country.upper(), "")
    fig.add_trace(go.Bar(
        x=plot_df.index,
        y=plot_df[country],
        name=f"{emoji} {country.title()}",
        marker_color=color_map.get(country.upper(), "#888888"),
        hovertemplate='<b>%{x}</b><br>' + f'{emoji} {country.title()}: $%{{y:,.0f}}<extra></extra>'
    ))

# Add total as text labels above bars
fig.add_trace(go.Scatter(
    x=plot_df.index,
    y=plot_df["Total Foreign Donations"],
    mode="text",
    text=[f"${v/1e6:.1f}M" for v in plot_df["Total Foreign Donations"]],
    textposition="top center",
    name="Total",
    showlegend=False
))

# Final layout tweaks
fig.update_layout(
    barmode='overlay',
    height=750,
    xaxis_tickangle=-45,
    yaxis_title='Donation Amount (USD)',
    title='Top 30 US Universities by Foreign Donations',
    legend_title_text='Country',
    hovermode='x unified'
)

st.plotly_chart(fig, use_container_width=True)
