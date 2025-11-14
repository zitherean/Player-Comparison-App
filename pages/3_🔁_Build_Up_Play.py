import streamlit as st
from constants import PARQUET_PATH
from utils.data_loader import load_understat_data
from utils.players import select_single_player
from utils.charts import plot_comparison

# --------------------------- PAGE CONFIGURATION ---------------------------

st.set_page_config(page_title="Build Up Play", layout="wide")

st.title("🔁 Build Up Play Comparison")

# --------------------------- LOAD DATA & SELECT PLAYERS ---------------------------

df = load_understat_data(PARQUET_PATH)

p1_data, p1_label = select_single_player(df, label="Player 1", key_prefix="p1")

st.divider()

with st.expander("Add Player 2"):
    p2_data, p2_label = select_single_player(df, label="Player 2", key_prefix="p2")

st.divider()

# --------------------------- STAT TYPE TOGGLE ---------------------------

default_toggle = st.session_state.get("use_per90", False)
use_per90 = st.toggle("Per 90 mins", value=default_toggle)
st.session_state["use_per90"] = use_per90
stat_type = "Per 90 mins" if use_per90 else "Total Stats"

# --------------------------- METRIC SECTIONS ---------------------------

buildup_stats = ['xGChain', 'xGBuildup']
buildup_stats_per_90 = ['xGChain_per90', 'xGBuildup_per90']

stats = buildup_stats_per_90 if stat_type == 'Per 90 mins' else buildup_stats
title = "Build Up Play"

fig = plot_comparison(p1_data, p2_data, p1_label, p2_label, stats, stat_type, title)
st.plotly_chart(fig, width="stretch")