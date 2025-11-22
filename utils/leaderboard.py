import streamlit as st
import pandas as pd
from constants import LEAGUE_NAME_MAP, SEASON_NAME_MAP, METRIC_LABELS
from utils.players import accumulate_player_rows, enrich_player_metrics

@st.cache_data
def build_player_table(df, season=None):
    """Aggregate all seasons per player using accumulate_player_rows."""
    if season is not None and season != "All seasons":
        df = df[df["season"] == season].copy()

    player_rows = []
    for player_name, rows in df.groupby("player_name"):
        if season is None or season == "All seasons":
            base_row = accumulate_player_rows(rows, minutes_col="time", per90_suffix="_per90")
        else:
            base_row = rows.sort_values("season", ascending=False).iloc[0]

        enriched = enrich_player_metrics(base_row)
        player_rows.append(enriched)
    players_df = pd.DataFrame(player_rows) 

    return players_df

def display_leaderboard(df, stat_col, season_string, n=10):
    leaderboard = (
        df[["player_name", stat_col]]   
        .sort_values(stat_col, ascending=False)
        .head(n)
        .reset_index(drop=True)
    )

    # change stats to int; no decimals
    leaderboard[stat_col] = leaderboard[stat_col].astype(int)

    # Make rank start at 1 and show as index
    leaderboard.index = leaderboard.index + 1
    leaderboard.index.name = "Rank"

    leaderboard = leaderboard.replace({**LEAGUE_NAME_MAP, **SEASON_NAME_MAP})

    pretty_stat_name = METRIC_LABELS.get(stat_col, stat_col)
    pretty_player_name = METRIC_LABELS.get("player_name", "player_name")

    leaderboard = leaderboard.rename(
        columns={
            "player_name": pretty_player_name,
            stat_col: pretty_stat_name,
        }
    )

    st.markdown(f"Top {n} players by {pretty_stat_name} ({season_string})")
    st.table(leaderboard)