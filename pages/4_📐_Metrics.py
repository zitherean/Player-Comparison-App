import streamlit as st
import pandas as pd
from utils.data_loader import load_understat_data
from utils.players import select_single_player
from constants import PARQUET_PATH, METRIC_LABELS, LEAGUE_NAME_MAP, SEASON_NAME_MAP

# --------------------------- PLAYER INFO DISPLAY ---------------------------

df = load_understat_data(PARQUET_PATH)

p1_data, p1_label = select_single_player(df, label="Player 1", key_prefix="p1")
p1_clean = p1_data.replace({**LEAGUE_NAME_MAP, **SEASON_NAME_MAP})

st.divider()

with st.expander("Add Player 2"):
    p2_data, p2_label = select_single_player(df, label="Player 2", key_prefix="p2")
    p2_clean = p2_data.replace({**LEAGUE_NAME_MAP, **SEASON_NAME_MAP})

st.divider()

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

st.dataframe(comparison, width="stretch", height=len(comparison) * 37)