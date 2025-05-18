
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(layout="wide")
st.title("Top 30 US Universities by Foreign Donations")
st.markdown("### Explore foreign donations from top 10 countries to U.S. universities (2024 data)")

df = pd.read_csv("top30_donations_top10countries_corrected.csv", index_col=0)

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

country_cols = [col for col in df.columns if col != "Total Foreign Donations"]
selected_countries = st.sidebar.multiselect(
    "Select countries to display (stacked in order)",
    country_cols,
    default=country_cols
)

top_n = st.sidebar.slider("Number of universities to show", 5, 30, 30)
plot_df = df.head(top_n)

fig = go.Figure()

# Plot background total bar
fig.add_trace(go.Bar(
    x=plot_df.index,
    y=plot_df["Total Foreign Donations"],
    name="Total Foreign Donations",
    marker_color="lightgray",
    opacity=0.4,
    hovertemplate='%{x}<br>Total: $%{y:,.0f}<extra></extra>'
))

# Stack each selected country
bottom = pd.Series([0] * len(plot_df), index=plot_df.index)

for country in selected_countries:
    fig.add_trace(go.Bar(
        x=plot_df.index,
        y=plot_df[country],
        name=country.title(),
        marker_color=color_map.get(country.upper(), None),
        hovertemplate=f'{{x}}<br>China: ${{y:,.0f}}<extra></extra>'
    ))

fig.update_layout(
    barmode='overlay',
    height=750,
    xaxis_tickangle=-45,
    yaxis_title='Donation Amount (USD)',
    title='Top 30 US Universities by Foreign Donations',
    legend_title_text='Country'
)

st.plotly_chart(fig, use_container_width=True)
