import streamlit as st
import pandas as pd
import numpy as np
from utils.data_loader import load_understat_data
from utils.players import select_single_player, display_player_info
from constants import PARQUET_PATH, METRIC_LABELS, LEAGUE_NAME_MAP, SEASON_NAME_MAP

# --------------------------- HELPER FUNCTIONS ---------------------------

def format_value(x):
    # pretty format numbers to 2 decimal places
    if isinstance(x, (int, float, np.floating)):
        return f"{x:.2f}"
    return x

def safe_get(series, key):
    return series.get(key, 0)

# --------------------------- PAGE CONFIGURATION ---------------------------

st.set_page_config(page_title="Metrics", layout="wide")

st.title("📐 Metrics")

# --------------------------- PLAYER SELECTION ---------------------------

df = load_understat_data(PARQUET_PATH)

p1_data, p1_label = select_single_player(df, label="Player 1", key_prefix="p1")
p1_clean = p1_data.replace({**LEAGUE_NAME_MAP, **SEASON_NAME_MAP})

st.divider()

with st.expander("Add Player 2"):
    p2_data, p2_label = select_single_player(df, label="Player 2", key_prefix="p2")
    p2_clean = p2_data.replace({**LEAGUE_NAME_MAP, **SEASON_NAME_MAP})

st.divider()

# --------------------------- TAB ---------------------------

overview_tab, table_tab = st.tabs(["Overview", "Detailed table"])

# --------------------------- PLAYER HEADER SECTION ---------------------------
with overview_tab:
    col_p1, col_p2 = st.columns(2)

    with col_p1:
        display_player_info(p1_clean)

    with col_p2:
        if p2_label is not None:
            display_player_info(p2_clean)
        else:
            st.info("Add a second player from the expander above to compare.")

    st.divider()

# --------------------------- KEY STATS TOTAL ---------------------------

    st.markdown("### Key stats (total)")

    kpi_cols_total = st.columns(3)

    with kpi_cols_total[0]:
        st.metric("Goals (P1)", f"{safe_get(p1_clean, 'goals'):.2f}")
        if p2_label is not None:
            st.metric("Goals (P2)", f"{safe_get(p2_clean, 'goals'):.2f}")

    with kpi_cols_total[1]:
        st.metric("xG (P1)", f"{safe_get(p1_clean, 'xG'):.2f}")
        if p2_label is not None:
            st.metric("xG (P2)", f"{safe_get(p2_clean, 'xG'):.2f}")

    with kpi_cols_total[2]:
        st.metric("Assists (P1)", f"{safe_get(p1_clean, 'assists'):.2f}")
        if p2_label is not None:
            st.metric("Assists (P2)", f"{safe_get(p2_clean, 'assists'):.2f}")

    st.divider()

# --------------------------- KEY STATS PER 90 ---------------------------

    st.markdown("### Key stats (per 90)")

    kpi_cols_per90 = st.columns(3)

    with kpi_cols_per90[0]:
        st.metric("Goals / 90 (P1)", f"{safe_get(p1_clean, 'goals_per90'):.2f}")
        if p2_label is not None:
            st.metric("Goals / 90 (P2)", f"{safe_get(p2_clean, 'goals_per90'):.2f}")

    with kpi_cols_per90[1]:
        st.metric("xG / 90 (P1)", f"{safe_get(p1_clean, 'xG_per90'):.2f}")
        if p2_label is not None:
            st.metric("xG / 90 (P2)", f"{safe_get(p2_clean, 'xG_per90'):.2f}")

    with kpi_cols_per90[2]:
        st.metric("Assists / 90 (P1)", f"{safe_get(p1_clean, 'assists_per90'):.2f}")
        if p2_label is not None:
            st.metric("Assists / 90 (P2)", f"{safe_get(p2_clean, 'assists_per90'):.2f}")

    st.divider()

# --------------------------- PLAYER TABLE ---------------------------

rows_to_drop = ['id']
comparison = pd.DataFrame({"Player 1": p1_clean, "Player 2": p2_clean}).rename_axis("Metrics")
comparison = comparison.drop(index=rows_to_drop, errors="ignore")

desired_order = [
    "player_name",
    "position",
    "team_title",
    "league",
    "season",
    "games",
    "time",
    "red_cards",
    "yellow_cards",
    "goals",
    "xG",
    "shots",
    "npg",
    "npxG",
    "assists",
    "xA",
    "key_passes",
    "xGBuildup",
    "xGChain",
    "goals_per90",
    "xG_per90",
    "shots_per90",
    "npg_per90",
    "npxG_per90",
    "assists_per90",
    "xA_per90",
    "key_passes_per90",
    "xGBuildup_per90",
    "xGChain_per90",
]

comparison = comparison.reindex(desired_order)
comparison = comparison.rename(index=METRIC_LABELS)

comparison_display = comparison.map(format_value).astype(str)

with table_tab:
    st.markdown("### Full metric comparison")
    st.table(comparison_display)
