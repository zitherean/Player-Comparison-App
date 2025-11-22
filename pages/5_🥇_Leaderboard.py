import streamlit as st
from constants import PARQUET_PATH, CURRENT_SEASON
from utils.data_loader import load_understat_data
from utils.leaderboard import display_leaderboard, build_player_table

CURRENT_SEASON_STRING = "2024/25"
ALL_SEASON_STRING = "all seasons"

# --------------------------- PAGE CONFIGURATION ---------------------------

st.set_page_config(page_title="Leaderboard", layout="wide")

st.title("🥇 Leaderboard")

# --------------------------- LOAD DATA ---------------------------

df = load_understat_data(PARQUET_PATH)

# --------------------------- CURRENT SEASON LEADERBOARD ---------------------------

st.subheader(f"Top Performers in the {CURRENT_SEASON_STRING} Season")

with st.spinner("Crunching the numbers… hang tight! ⏳"):
    current_season_players = build_player_table(df, season=CURRENT_SEASON)

col1, col2 = st.columns(2)

with col1:
    display_leaderboard(current_season_players, "goals", CURRENT_SEASON_STRING)
    display_leaderboard(current_season_players, "goal_contrib", CURRENT_SEASON_STRING)

with col2:
    display_leaderboard(current_season_players, "assists", CURRENT_SEASON_STRING)
    display_leaderboard(current_season_players, "conversion_rate", CURRENT_SEASON_STRING)

# --------------------------- ALL TIME LEADERBOARD  ---------------------------

st.subheader("All-Time Leaderboards (data starts from 2014/15)")

with st.spinner("Crunching the numbers… hang tight! ⏳"):
    all_players = build_player_table(df, season="All seasons")

col1, col2 = st.columns(2)
with col1:
    display_leaderboard(all_players, "goals", ALL_SEASON_STRING)
    display_leaderboard(all_players, "goal_contrib", ALL_SEASON_STRING)
with col2:
    display_leaderboard(all_players, "assists", ALL_SEASON_STRING)
