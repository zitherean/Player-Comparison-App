import streamlit as st
import numpy as np
import pandas as pd
from utils.format import to_float, format_value
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

# --------------------------- DISPLAY METRICS ---------------------------

def display_player_info(player_data):
    st.markdown(
        f"""
        <div style="
            padding: 12px 16px;
            border-radius: 10px;
            background-color: #f7f7f7;
            border: 1px solid #e0e0e0;
            margin-bottom: 12px;
        ">
            <h3 style="margin-bottom:0;">
                {player_data['player_name']}
                <span style="font-size:0.75em;color:gray;">({player_data['position']})</span>
            </h3>
            <div style="color:#666;font-size:0.9em;">
                <strong>{player_data['team_title']}</strong> · {player_data['season']}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

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
                st.markdown(f"**{p1_clean['player_name']}**")
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
                st.markdown(f"**{p2_clean['player_name']}**")
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
            st.markdown(f"**{p['player_name']}**")
            for label, key in metrics:
                st.metric(label=label, value=format_value(p.get(key, 0)))

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
    # --- Precompute positions for fast lookup ---

    placeholder = "— Select a player —"
    players = [placeholder] + sorted(df["player_name"].unique()) # unescape to get rid of weird characters

    
    # --- Default selection behaviour ---
    stored_name = st.session_state.get(f"{key_prefix}_player_name", placeholder)
    default_idx = players.index(stored_name) if stored_name in players else 0

    # --- How to display each option ---
    def fmt(name):
        if name == placeholder:
            return name
        pos = pos_map.get(name, "")
        return f"{name} ({pos})" if pos else name

    # --- Player dropdown ---
    player = st.selectbox(f"Select {label}", players, index=default_idx, key=f"{key_prefix}_player_select", format_func=fmt)

    # If user hasn't selected a real player yet, save selection and stop here
    if player == placeholder:
        st.session_state[f"{key_prefix}_player_name"] = placeholder
        st.session_state.pop(f"{key_prefix}_season_value", None)
        return None, None

    # Save valid selection
    st.session_state[f"{key_prefix}_player_name"] = player

    # --- Filter for that player ---
    rows = df[df["player_name"] == player]

    # Optional season filter...
    seasons = ["All seasons"] + sorted(rows["season"].unique(), reverse=True)
    default_season = st.session_state.get(f"{key_prefix}_season_value", "All seasons")
    if default_season in seasons:
        season_idx = seasons.index(default_season)
    else:
        season_idx = 0

    season = st.selectbox("Filter by season (optional)", seasons, index=season_idx, key=f"{key_prefix}_season_select", format_func=lambda x: SEASON_NAME_MAP.get(x, x))

    st.session_state[f"{key_prefix}_season_value"] = season

    if season == "All seasons":
        # ---- ACCUMULATED STATS ACROSS ALL SEASONS ----
        row = accumulate_player_rows(rows, minutes_col="time", per90_suffix="_per90")
    else:
        # ---- SINGLE SEASON ----
        season_rows = rows[rows["season"] == season]
        season_rows = season_rows.sort_values("season", ascending=False)
        row = season_rows.iloc[0]
    
    display_season = SEASON_NAME_MAP.get(str(row["season"]), row["season"])
    label_str = f"{row['player_name']} ({display_season}, {row['team_title']})"

    return row, label_str