
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")
st.title("Top 30 US Universities by Foreign Donations")
st.markdown("### Explore foreign donations from Qatar, PRC, UAE, and Saudi Arabia to U.S. universities (2024 data)")

# Load preprocessed data (you'll need to upload this CSV to your repo)
df = pd.read_csv("top30_donations.csv", index_col=0)
df.index.name = "University"

# Sidebar filters
selected_countries = st.sidebar.multiselect(
    "Select countries to display",
    ["Qatar Donations", "PRC Donations", "UAE Donations", "Saudi Arabia Donations"],
    default=["Qatar Donations", "PRC Donations", "UAE Donations", "Saudi Arabia Donations"]
)

top_n = st.sidebar.slider("Number of universities to show", 5, 30, 30)

# Filtered data
plot_df = df.head(top_n)

# Plot
fig, ax = plt.subplots(figsize=(16, 9))
ax.bar(plot_df.index, plot_df["Total Foreign Donations"], label="Total Foreign Donations", color="lightgray")

# Stacking logic
bottom = pd.Series([0] * len(plot_df), index=plot_df.index)
colors = {
    "Qatar Donations": "navy",
    "PRC Donations": "red",
    "UAE Donations": "gold",
    "Saudi Arabia Donations": "darkgreen"
}

for col in selected_countries:
    ax.bar(plot_df.index, plot_df[col], bottom=bottom, label=col, color=colors[col])
    bottom += plot_df[col]

# Labels
for i, school in enumerate(plot_df.index):
    height = plot_df["Total Foreign Donations"][i]
    ax.text(i, height + 1e7, f"${height/1e6:.1f}M", ha="center", va="bottom", fontsize=8, rotation=45)

ax.set_title("Foreign Donations to Top U.S. Universities", fontsize=20)
ax.set_ylabel("Donation Amount (USD)", fontsize=12)
ax.set_xticklabels(plot_df.index, rotation=45, ha='right')
ax.legend()

st.pyplot(fig)
