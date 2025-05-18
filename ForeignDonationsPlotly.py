import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(layout="wide")
st.title("Top 30 US Universities by Foreign Donations")
st.markdown("### Explore foreign donations from top 10 countries to U.S. universities (2024 data)")

# Load corrected CSV
df = pd.read_csv("top30_donations_top10countries_corrected.csv", index_col=0)

# Rename misclassified countries
df.columns = [col.replace("ENGLAND", "UNITED KINGDOM") for col in df.columns]

# Flag and color maps
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
    "SOUTH KOREA": "🇰🇷",
    "SWITZERLAND": "🇨🇭",
    "HONG KONG": "🇭🇰"
}

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
    "SOUTH KOREA": "#003478",
    "SWITZERLAND": "#D52B1E",
    "HONG KONG": "#BA0C2F"
}

# Filter for country-specific columns
country_cols = [col for col in df.columns if col != "Total Foreign Donations"]

# Sidebar
selected_countries = st.sidebar.multiselect(
    "Select countries to display (stacked in order)",
    country_cols,
    default=country_cols
)
top_n = st.sidebar.slider("Number of universities to show", 5, 30, 30)
plot_df = df.head(top_n)

# Plotly figure
fig = go.Figure()

# Add background total donation bar
fig.add_trace(go.Bar(
    x=plot_df.index,
    y=plot_df["Total Foreign Donations"],
    name="Total Foreign Donations",
    marker_color="lightgray",
    opacity=0.3,
    hovertemplate='<b>%{x}</b><br>Total: $%{y:,.0f}<extra></extra>'
))

# Add each selected country as a stacked bar
for country in selected_countries:
    label = country.replace("ENGLAND", "UNITED KINGDOM")
    emoji = flag_map.get(label.upper(), "")
    color = color_map.get(label.upper(), "#888888")
    fig.add_trace(go.Bar(
        x=plot_df.index,
        y=plot_df[country],
        name=f"{emoji} {label.title()}",
        marker_color=color,
        hovertemplate='<b>%{x}</b><br>' + f'{emoji} {label.title()}: $%{{y:,.0f}}<extra></extra>'
    ))

# Add text annotation of total value
fig.add_trace(go.Scatter(
    x=plot_df.index,
    y=plot_df["Total Foreign Donations"],
    mode="text",
    text=[f"${v/1e6:.1f}M" for v in plot_df["Total Foreign Donations"]],
    textposition="top center",
    name="Total",
    showlegend=False
))

# Layout settings
fig.update_layout(
    barmode='overlay',
    height=750,
    xaxis_tickangle=-45,
    yaxis_title='Donation Amount (USD)',
    title='Top 30 US Universities by Foreign Donations',
    legend_title_text='Country',
    hovermode='x unified'
)

# Render
st.plotly_chart(fig, use_container_width=True)
