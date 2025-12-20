import streamlit as st
from constants import PARQUET_PATH, METRIC_LABELS
from utils.data_loader import load_understat_data
from utils.players import select_single_player, build_pos_map
from utils.charts import plot_radar
from utils.text import clean_html_entities

# --------------------------- PAGE CONFIGURATION ---------------------------

st.set_page_config(page_title="Player Profile", layout="wide")

st.title("🕸️ Player Profile")

# --------------------------- LOAD DATA & SELECT PLAYERS ---------------------------

df = load_understat_data(PARQUET_PATH)
df = clean_html_entities(df, ["player_name", "team_title"])
pos_map = build_pos_map(df)

col1, col2 = st.columns(2)

with col1:
    p1_data, p1_label = select_single_player(df, pos_map, label="Player 1", key_prefix="p1")

with col2:
    p2_data, p2_label = select_single_player(df, pos_map, label="Player 2", key_prefix="p2")

st.divider()

# --------------------------- METRIC SECTIONS ---------------------------

# Only per90 metrics
RADAR_METRICS_PER90 = [
    k for k in METRIC_LABELS.keys()
    if k.endswith("_per90")
]

# Label ↔ key mapping
RADAR_LABEL_TO_KEY = {
    METRIC_LABELS[k]: k for k in RADAR_METRICS_PER90
}

RADAR_KEY_TO_LABEL = {
    k: METRIC_LABELS[k] for k in RADAR_METRICS_PER90
}

DEFAULT_RADAR_METRICS = ["goals_per90", "shots_per90", "assists_per90", "xGBuildup_per90", "xGChain_per90"]

with st.expander("Select Radar Metrics"):
    selected_labels = st.multiselect(
        "Select radar metrics (per 90)",
        options=list(RADAR_LABEL_TO_KEY.keys()),
        default=[RADAR_KEY_TO_LABEL[k] for k in DEFAULT_RADAR_METRICS],
        key="radar_stats",
    )

# Convert labels → column names
selected_stats = [RADAR_LABEL_TO_KEY[l] for l in selected_labels]

if len(selected_stats) >= 3:
    fig = plot_radar(df=df, player1_data=p1_data, player2_data=p2_data, label1=p1_label, label2=p2_label, stats=selected_stats, title="Per 90 Radar (percentile)")

    if fig is not None:
        st.plotly_chart(fig, width="stretch")
    else:
        st.info("Select at least one player to see the chart.")
else:
    st.info("Select at least 3 metrics to display the radar chart.")
