import streamlit as st
from constants import PARQUET_PATH
from utils.data_loader import load_understat_data
from utils.players import select_single_player, build_pos_map
from utils.charts import plot_comparison

# --------------------------- PAGE CONFIGURATION ---------------------------

st.set_page_config(page_title="Creativity", layout="wide")

st.title("🎯 Creativity Comparison")

# --------------------------- LOAD DATA & SELECT PLAYERS ---------------------------

df = load_understat_data(PARQUET_PATH)
pos_map = build_pos_map(df)

col1, col2 = st.columns(2)

with col1:
    p1_data, p1_label = select_single_player(df, pos_map, label="Player 1", key_prefix="p1")

with col2:
    p2_data, p2_label = select_single_player(df, pos_map, label="Player 2", key_prefix="p2")

st.divider()

# --------------------------- STAT TYPE TOGGLE ---------------------------

default_toggle = st.session_state.get("use_per90", False)
use_per90 = st.toggle("Per 90 mins", value=default_toggle)
st.session_state["use_per90"] = use_per90
stat_type = "Per 90 mins" if use_per90 else "Total Stats"

# --------------------------- METRIC SECTIONS ---------------------------

creativity_stats = ['assists', 'xA', 'key_passes']
creativity_stats_per_90 = ['assists_per90', 'xA_per90', 'key_passes_per90']
creativity_stats.reverse() # the list shows from top to down
creativity_stats_per_90.reverse()

stats = creativity_stats_per_90 if stat_type == 'Per 90 mins' else creativity_stats
title = "Creativity"

fig = plot_comparison(p1_data, p2_data, p1_label, p2_label, stats, stat_type, title)
if fig is not None:
    st.plotly_chart(fig, width="stretch")
else:
    st.info("Select at least one player to see the chart.")