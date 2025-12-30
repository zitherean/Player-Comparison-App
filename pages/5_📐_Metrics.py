import streamlit as st
import pandas as pd
import numpy as np
from utils.data_loader import load_understat_data
from utils.format import clean_html_entities
from utils.players import select_single_player, display_key_stats, enrich_player_metrics, build_pos_map
from constants import PARQUET_PATH, LEAGUE_NAME_MAP
from utils.season import SEASON_NAME_MAP

# --------------------------- PAGE CONFIGURATION ---------------------------

st.set_page_config(page_title="Metrics", layout="wide")

st.title("📐 Metrics")

# --------------------------- PLAYER SELECTION ---------------------------

df = load_understat_data(PARQUET_PATH)
df = clean_html_entities(df, ["player_name", "team_title"])
pos_map = build_pos_map(df)

col1, col2 = st.columns(2)

p1_data, p1_label, p1_clean = None, None, None
p2_data, p2_label, p2_clean = None, None, None

with col1:
    p1_data, p1_label = select_single_player(df, pos_map, label="Player 1", key_prefix="p1")

    # If no Player 1 selected, stop the page here
    if p1_data is not None:
        p1_clean = p1_data.replace({**LEAGUE_NAME_MAP, **SEASON_NAME_MAP})
        p1_clean = enrich_player_metrics(p1_clean)

with col2:
    p2_data, p2_label = select_single_player(df, pos_map, label="Player 2", key_prefix="p2")

    if p2_data is not None:
        p2_clean = p2_data.replace({**LEAGUE_NAME_MAP, **SEASON_NAME_MAP})
        p2_clean = enrich_player_metrics(p2_clean)

st.divider()

# --------------------------- PLAYER HEADER SECTION ---------------------------

if p1_clean is None and p2_clean is None:
    st.info("Select at least one player to see the key metrics.")
    st.stop()
    
# --------------------------- KEY STATS TOTAL ---------------------------

metrics_total = [
    ("Goals", "goals"),
    ("Assists", "assists"),
    ("G + A", "goal_contrib"),
]

display_key_stats(title="Attacking output (total)", p1_clean=p1_clean, p2_clean=p2_clean, metrics=metrics_total)

st.divider()

# --------------------------- KEY STATS PER 90 ---------------------------

metrics_per90 = [
    ("Goals / 90", "goals_per90"),
    ("Assists / 90", "assists_per90"),
    ("G + A / 90", "goal_contrib_per90"),
]

display_key_stats(title="Attacking output (per 90)", p1_clean=p1_clean, p2_clean=p2_clean, metrics=metrics_per90)

st.divider()

# --------------------------- FINISHING ---------------------------

metrics_finishing = [
    ("Conversion Rate (%)", "conversion_rate"),
    ("xG per Shot", "xG_per_shot"),
    ("Goals - xG", "goals_minus_xG"),
    ("NP Goals - NP xG", "npg_minus_npxG"),
]

display_key_stats(title="Finishing & shot quality", p1_clean=p1_clean, p2_clean=p2_clean, metrics=metrics_finishing)

st.divider()

# --------------------------- CREATIVITY ---------------------------

metrics_creation = [
    ("Assists per Key Pass", "assists_per_key_pass"), 
    ("xA per Key Pass", "xA_per_key_pass"),
    ("Key Passes / 90", "key_passes_per90"),
    ("xA / 90", "xA_per90"),
]

display_key_stats(title="Creativity & chance creation", p1_clean=p1_clean, p2_clean=p2_clean, metrics=metrics_creation)

st.divider()

# --------------------------- BUILD UP ---------------------------

metrics_buildup = [
    ("xG Buildup", "xGBuildup"),
    ("xG Chain", "xGChain"),
    ("xG Buildup / 90", "xGBuildup_per90"),
    ("xG Chain / 90", "xGChain_per90"),
]

display_key_stats(title="Build-up & involvement", p1_clean=p1_clean, p2_clean=p2_clean, metrics=metrics_buildup)

st.divider()

# --------------------------- USAGE ---------------------------

metrics_usage = [
    ("Games Played", "games"),
    ("Minutes Played", "time"),
    ("Minutes / Game", "mins_per_game"),
    ("G + A / Game", "goal_contrib_per_game"),
]

display_key_stats(title="Usage & Availability", p1_clean=p1_clean, p2_clean=p2_clean, metrics=metrics_usage)

st.divider()

# --------------------------- DISCIPLINE ---------------------------


metrics_discipline = [
    ("Red Cards", "red_cards"),
    ("Red / 90", "red_per90"),
    ("Yellow Cards", "yellow_cards"),
    ("Yellow / 90", "yellow_per90"),
]

display_key_stats(title="Discipline & On-Pitch Behavior", p1_clean=p1_clean, p2_clean=p2_clean, metrics=metrics_discipline)

st.divider()
