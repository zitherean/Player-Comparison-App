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

def display_leaderboard(df, stat_cols, season_string, n=10):
    """Display a leaderboard of players for one or more statistics."""

    leaderboard = (
        df[["player_name"] + stat_cols]   
        .sort_values(stat_cols[0], ascending=False)
        .head(n)
        .reset_index(drop=True)
    )

    leaderboard = leaderboard.replace({**LEAGUE_NAME_MAP, **SEASON_NAME_MAP})

    rename_map = {"player_name": METRIC_LABELS.get("player_name", "Player")}
    rename_map.update({col: METRIC_LABELS.get(col, col) for col in stat_cols})

    leaderboard = leaderboard.rename(columns=rename_map)

    # make player name text column
    col_config = {rename_map["player_name"]: st.column_config.TextColumn(rename_map["player_name"])}

    for col in stat_cols:
        pretty = rename_map[col]

        if col in {"goals", "assists", "goal_contrib"}:
            fmt = "%d"
        else:
            fmt = "%.2f"
        # make ints and floats show 0 decimals or 2 decimals
        col_config[pretty] = st.column_config.NumberColumn(pretty, format=fmt)

    first_stat_pretty = rename_map[stat_cols[0]]
    st.markdown(f"Top {n} players by {first_stat_pretty} ({season_string})")

    st.dataframe(leaderboard, width="stretch", hide_index=True, column_config=col_config)