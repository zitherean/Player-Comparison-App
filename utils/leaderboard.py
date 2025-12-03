import streamlit as st
import pandas as pd
import numpy as np
from constants import LEAGUE_NAME_MAP, METRIC_LABELS
from utils.season import SEASON_NAME_MAP
from utils.players import enrich_player_metrics, format_value

@st.cache_data
def build_player_table(df, season=None):
    """
    Vectorized version of build_player_table.
    - For a specific season: pick one row per player and enrich.
    - For 'All seasons': aggregate stats per player and recompute per90s.
    Expects a vectorized enrich function: enrich_player_metrics_df(df).
    """

    df = df.copy()
    df["season"] = df["season"].astype(str)

    per90_suffix = "_per90"

    # ---------- 1) SPECIFIC SEASON (NO AGGREGATION) ----------
    if season is not None and season != "All seasons":
        season_str = str(season)
        season_df = df[df["season"] == season_str]

        if season_df.empty:
            # no data for that season
            return pd.DataFrame()

        # one row per player: most recent season row
        latest_per_player = season_df.loc[
            season_df.groupby("player_name")["season"].idxmax()
        ]

        # vectorized enrichment on the full DataFrame
        players_df = enrich_player_metrics(latest_per_player.reset_index(drop=True))
        return players_df

    # ---------- 2) ALL SEASONS (AGGREGATION) ----------

    # numeric columns
    num_cols = df.select_dtypes(include="number").columns

    # raw stats to aggregate: numeric columns that are NOT per90
    raw_cols = [c for c in num_cols if not c.endswith(per90_suffix)]

    # summed raw stats per player
    summed = df.groupby("player_name")[raw_cols].sum(min_count=1)

    # template row per player (for non-aggregated fields: team, league, etc.)
    templates = df.loc[df.groupby("player_name")["season"].idxmax()]
    templates = templates.set_index("player_name")

    # keep only columns we are NOT overriding with sums
    non_agg_cols = [c for c in templates.columns if c not in raw_cols]
    merged = templates[non_agg_cols].join(summed)

    merged["season"] = "All seasons"

    players_df = enrich_player_metrics(merged.reset_index())
    return players_df


def display_leaderboard(df, stat_cols, season_string, n=10):
    """Display a leaderboard of players for one or more statistics."""

    leaderboard = (
        df[["player_name"] + stat_cols]   
        .sort_values(stat_cols[0], ascending=False)
        .head(n)
        .reset_index(drop=True)
    )

    rename_map = {"player_name": METRIC_LABELS.get("player_name", "Player")}
    rename_map.update({col: METRIC_LABELS.get(col, col) for col in stat_cols})

    leaderboard = leaderboard.rename(columns=rename_map)

    first_stat_pretty = rename_map[stat_cols[0]]
    st.markdown(f"Top {n} players by {first_stat_pretty} ({season_string})")

    leaderboard = leaderboard.map(format_value)

    st.dataframe(leaderboard, width="stretch", hide_index=True)