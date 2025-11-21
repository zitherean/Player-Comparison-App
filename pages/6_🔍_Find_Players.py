import streamlit as st
from constants import PARQUET_PATH, LEAGUE_NAME_MAP, SEASON_NAME_MAP, METRIC_LABELS
from utils.data_loader import load_understat_data
from utils.players import player_search, enrich_player_metrics

# --------------------------- PAGE CONFIGURATION ---------------------------

st.set_page_config(page_title="Find Players", layout="wide")

st.title("🔍 Find Players")

# --------------------------- LOAD DATA & SELECT PLAYERS ---------------------------

df = load_understat_data(PARQUET_PATH)

filtered_df, selected_player = player_search(df)

if selected_player == "All players":
    st.divider()
    st.subheader("Results")
    st.info("Select a player to see their details.")
else:
    st.divider()

    st.subheader("Results")

    if st.session_state.get("copy_player_name") != selected_player:
        st.session_state["copy_player_name"] = selected_player

    st.text_input("Player name (click to copy)", key="copy_player_name")


# FIXME
# # Apply mapping replacements
# clean_data = filtered_data.replace({**LEAGUE_NAME_MAP, **SEASON_NAME_MAP})
# clean_data = enrich_player_metrics(clean_data)

# # Column order
# desired_order = [
#     "player_name",
#     "position",
#     "team_title",
#     "league",
#     "season",
#     "games",
#     "time",
#     "goals",
#     "assists",
#     "goal_contrib"
# ]

# clean_data = clean_data.reindex(columns=desired_order)
# clean_data = clean_data.drop_duplicates(subset=["player_name", "season", "team_title"])
# # Rename columns (not index)
# clean_data = clean_data.rename(columns=METRIC_LABELS)
