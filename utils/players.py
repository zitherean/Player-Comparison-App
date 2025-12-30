import streamlit as st
import numpy as np
import pandas as pd
from utils.format import to_float, format_value
from utils.filters import multiselect_filter
from constants import LOWER_IS_BETTER
from utils.season import SEASON_NAME_MAP

# --------------------------- ENRICH PLAYER METRICS ---------------------------

def enrich_player_metrics(obj):
    """
    Flexible wrapper:
    - If `obj` is a Series -> treat as a single player row.
    - If `obj` is a DataFrame -> treat as multiple rows.
    Returns the same type it receives.
    """
    if isinstance(obj, pd.Series):
        # one row -> convert to 1-row DataFrame
        df_single = obj.to_frame().T
        enriched_df = _enrich_player_metrics_df(df_single)
        # return the (only) row back as Series
        return enriched_df.iloc[0]

    elif isinstance(obj, pd.DataFrame):
        return _enrich_player_metrics_df(obj)

    else:
        raise TypeError(f"enrich_player_metrics expects a pandas Series or DataFrame, got {type(obj)}")


def _enrich_player_metrics_df(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Helpers
    def col(name, default=0):
        if name in df.columns:
            s = df[name]
            # If it's object dtype, try to convert to numeric first
            if s.dtype == "O":
                s = pd.to_numeric(s, errors="coerce")
            return s.fillna(default)
        return pd.Series(default, index=df.index, dtype="float64")


    goals       = col("goals")
    assists     = col("assists")
    xG          = col("xG")
    xA          = col("xA")
    npg         = col("npg")
    npxG        = col("npxG")
    shots       = col("shots")
    key_passes  = col("key_passes")
    time_min    = col("time")
    games       = col("games")
    yellow      = col("yellow_cards")
    red         = col("red_cards")

    goals_per90      = col("goals_per90")
    assists_per90    = col("assists_per90")
    xG_per90         = col("xG_per90")
    xA_per90         = col("xA_per90")
    key_passes_per90 = col("key_passes_per90")
    xg_buildup_per90 = col("xGBuildup_per90")
    xg_chain_per90   = col("xGChain_per90")

    # ---------- ATTACKING OUTPUT ----------
    df["goal_contrib"] = goals + assists
    df["goal_contrib_per90"] = goals_per90 + assists_per90

    # Over/underperformance
    df["goals_minus_xG"] = goals - xG
    df["npg_minus_npxG"] = npg - npxG

    # ---------- EFFICIENCY ----------
    shots_nonzero = shots > 0
    df["conversion_rate"] = np.where(shots_nonzero, (goals / shots) * 100, np.nan)
    df["xG_per_shot"] = np.where(shots_nonzero, xG / shots, np.nan)

    kp_nonzero = key_passes > 0
    df["assists_per_key_pass"] = np.where(kp_nonzero, assists / key_passes, np.nan)
    df["xA_per_key_pass"] = np.where(kp_nonzero, xA / key_passes, np.nan)

    # ---------- USAGE / INVOLVEMENT ----------
    games_nonzero = games > 0
    df["mins_per_game"] = np.where(games_nonzero, time_min / games, np.nan)
    df["goal_contrib_per_game"] = np.where(games_nonzero, (goals + assists) / games, np.nan)

    # ---------- DISCIPLINE ----------
    mins_nonzero = time_min > 0
    factor = np.where(mins_nonzero, 90.0 / time_min, np.nan)
    df["yellow_per90"] = yellow * factor
    df["red_per90"] = red * factor

    return df

# --------------------------- KPI DISPLAY METRICS ---------------------------

def display_key_stats(title, p1_clean=None, p2_clean=None, metrics=None):
    if metrics is None:
        metrics = []

    st.markdown(f"### {title}")

    # Decide layout
    if p1_clean is not None and p2_clean is not None:
        col1, col2 = st.columns(2)

        with col1:
            with st.container(border=True):
                st.markdown(f"**{p1_clean['player_name']}** ({p1_clean['team_title']})")
                for label, key in metrics:
                    v1 = round(to_float(p1_clean.get(key, 0)) or 0.0, 2)
                    v2 = round(to_float(p2_clean.get(key, 0)) or 0.0, 2)

                    d = v1 - v2
                    delta = None
                    if d != 0:
                        delta = d
                    
                    st.metric(
                        label=label,
                        value=format_value(p1_clean.get(key, 0)),
                        delta=None if delta is None else format_value(delta),
                        delta_color=("inverse" if key in LOWER_IS_BETTER else "normal"),
                    )

        with col2:
            with st.container(border=True):
                st.markdown(f"**{p2_clean['player_name']}** ({p2_clean['team_title']})")
                for label, key in metrics:
                    v1 = round(to_float(p1_clean.get(key, 0)) or 0.0, 2)
                    v2 = round(to_float(p2_clean.get(key, 0)) or 0.0, 2)

                    d = v2 - v1
                    delta = None
                    if d != 0:
                        delta = d

                    st.metric(
                        label=label,
                        value=format_value(p2_clean.get(key, 0)),
                        delta=None if delta is None else format_value(delta),
                        delta_color=("inverse" if key in LOWER_IS_BETTER else "normal"),
                    )

    else:
        # single player (left aligned)
        p = p1_clean if p1_clean is not None else p2_clean
        with st.container(border=True):
            st.markdown(f"**{p['player_name']}** ({p['team_title']})")
            for label, key in metrics:
                st.metric(label=label, value=format_value(p.get(key, 0)))

# --------------------------- DATAFRAME ---------------------------

def get_result_dataframe(df, selected_seasons):
    if len(selected_seasons) != 1:
        aggregated_rows = []

        for _, rows in df.groupby("player_name"):
            aggregated_rows.append(accumulate_player_rows(rows, minutes_col="time", per90_suffix="_per90"))

        return pd.DataFrame(aggregated_rows)

    return df.drop_duplicates(subset=["player_name", "season", "team_title"])

# --------------------------- SEARCH + SELECT ---------------------------

def accumulate_player_rows(rows, minutes_col="time", per90_suffix="_per90"):
    # Sum numeric columns
    num_cols = rows.select_dtypes(include="number").columns
    summed = rows[num_cols].sum()

    # Use most recent row as template
    base = rows.sort_values("season", ascending=False).iloc[0].copy()

    # First, set all numeric columns to summed totals (for counting stats)
    for col in num_cols:
        base[col] = summed[col]

    # Recalculate per-90s instead of using the summed values
    if summed[minutes_col] > 0:
        total_minutes = float(summed[minutes_col])
        denominator = (total_minutes / 90)
        # Detect per-90 columns by suffix (e.g. "npxG_per90")
        per90_cols = [c for c in num_cols if c.endswith(per90_suffix)]
        
        for col in per90_cols:
            raw_col = col[: -len(per90_suffix)]  # strip '_per90'
            
            if raw_col in summed:
                # per90 = (total raw stat / total minutes) * 90
                base[col] = (float(summed[raw_col]) / denominator)

    base["season"] = "All seasons"
    return base

def build_pos_map(df):
    return (
        df[["player_name", "position"]]
        .dropna(subset=["position"])
        .drop_duplicates("player_name")
        .set_index("player_name")["position"]
        .astype(str)
        .to_dict()
    )

def select_single_player(df, pos_map, label="Player", key_prefix="p"):
    placeholder = "— Select a player —"
    players = [placeholder] + sorted(df["player_name"].unique())

    stored_name = st.session_state.get(f"{key_prefix}_player_name", placeholder)
    default_idx = players.index(stored_name) if stored_name in players else 0

    def fmt(name):
        if name == placeholder:
            return name
        pos = pos_map.get(name, "")
        return f"{name} ({pos})" if pos else name

    player = st.selectbox(
        f"Select {label}",
        players,
        index=default_idx,
        key=f"{key_prefix}_player_select",
        format_func=fmt
    )

    if player == placeholder:
        st.session_state[f"{key_prefix}_player_name"] = placeholder
        st.session_state.pop(f"{key_prefix}_season_select", None)
        st.session_state.pop(f"__store__{key_prefix}_season_select", None)
        st.session_state.pop(f"{key_prefix}_prev_player", None)
        return None, None

    # ---- RESET multiselect if player changed ----
    prev_player = st.session_state.get(f"{key_prefix}_prev_player")
    if prev_player != player:
        st.session_state.pop(f"{key_prefix}_season_select", None)
        st.session_state.pop(f"__store__{key_prefix}_season_select", None)
    st.session_state[f"{key_prefix}_prev_player"] = player
    st.session_state[f"{key_prefix}_player_name"] = player

    rows = df[df["player_name"] == player].copy()

    season_key = f"{key_prefix}_season_select__{player}"
    selected_seasons = multiselect_filter(
        "Select season(s)",
        rows["season"],
        season_key,
        default_all=True,
        sort_reverse=True,
        format_func=lambda s: SEASON_NAME_MAP.get(str(s), s)
    )

    all_seasons_for_player = sorted(rows["season"].unique(), reverse=True)
    selected_is_all = (len(selected_seasons) == 0) or (set(selected_seasons) == set(all_seasons_for_player))

    if selected_is_all:
        row = accumulate_player_rows(rows, minutes_col="time", per90_suffix="_per90")
    elif len(selected_seasons) == 1:
        season = selected_seasons[0]
        row = rows[rows["season"] == season].sort_values("season", ascending=False).iloc[0]
    else:
        subset = rows[rows["season"].isin(selected_seasons)]
        row = accumulate_player_rows(subset, minutes_col="time", per90_suffix="_per90")

    label_str = f"{row['player_name']} ({row['team_title']})"

    return row, label_str
