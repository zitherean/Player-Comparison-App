import streamlit as st
import numpy as np
import pandas as pd
import html
from constants import LEAGUE_NAME_MAP, SEASON_NAME_MAP
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

# --------------------------- HELPER FUNCTIONS ---------------------------

def safe_index(options, value, fallback=0):
    """Safely return index of value in list; fallback to given index if missing."""
    try:
        return options.index(value)
    except Exception:
        return fallback if options else 0

# --------------------------- PLAYER SELECTION FUNCTION ---------------------------

def player_scope(df, scope_name, *, default_season=None, default_player=None):
    """
    Displays selection boxes for league, season, team, and player.
    Returns the chosen player's data row and label for chart display.
    """
    st.subheader(scope_name)

    # League
    leagues = ["All leagues"] + sorted(df['league'].unique())
    league = st.selectbox(f"League ({scope_name})", leagues, key=f"{scope_name}_league", index=0,
                        format_func=lambda x: x if x == "All leagues" else LEAGUE_NAME_MAP.get(x, x))
    df_league = df if league == "All leagues" else df[df['league'] == league]
    
    # Season
    seasons = sorted(map(str, df_league['season'].unique()), reverse=True)  # latest first
    default_season_str = str(default_season) if default_season is not None else seasons[0]
    season = st.selectbox(f"Season ({scope_name})", seasons, key=f"{scope_name}_season", index=safe_index(seasons, default_season_str, fallback=0))
    df_league_season = df_league[df_league['season'] == season]

    # Team
    teams = ["All teams"] + sorted(df_league_season['team_title'].unique())
    team = st.selectbox(f"Team ({scope_name})", teams, key=f"{scope_name}_team", index=0)
    df_league_season_team = df_league_season if team == "All teams" else df_league_season[df_league_season['team_title'] == team]
    
    # Player
    players = sorted(df_league_season_team['player_name'].unique())
    if isinstance(default_player, str):
        player_idx = safe_index(players, default_player, fallback=0)
    else:
        player_idx = 0
    player = st.selectbox(f"Player ({scope_name})", players, key=f"{scope_name}_player", index=player_idx)

    # Filter for chosen player (within selected team if applicable)
    if team == "All teams":
        rows = df_league_season[df_league_season['player_name'] == player]
    else: 
        rows = df_league_season_team[df_league_season_team['player_name'] == player]

    if rows.empty:
        st.warning(f"No data for {player} in {league} {season}.")
        st.stop()

    # Extract first record (players are unique per team-season)
    row = rows.iloc[0].copy()   

    # Format display label
    team_for_label = f", {row['team_title']}"
    label = f"{row['player_name']} ({season}{team_for_label})"

    return row, label

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
def safe_get(series, key):
    return series.get(key, 0)

def format_value(value):
    """
    Formats any metric consistently:
      - NaN -> "—"
      - Integer -> "5"
      - Float -> "0.45"
      - String -> unchanged
    """

    if value is None:
        return "—"

    # Handle pandas / numpy NaN
    if isinstance(value, float) and np.isnan(value):
        return 0

    # Try numeric conversion
    try:
        num = float(value)

        # integer-like (3.0 becomes "3")
        if num.is_integer():
            return str(int(num))

        # float -> format with 2 decimals
        return f"{num:.2f}"

    except (ValueError, TypeError):
        # Non-numeric: keep original (e.g. names, clubs)
        return str(value)



def display_key_stats(title, p1_clean, p2_clean, metrics):
    st.markdown(f"### {title}")

    col_p1, col_p2 = st.columns(2)

    # Player 1 column
    with col_p1:
        st.markdown(f"{p1_clean['player_name']}")
        for label, key in metrics:
            st.metric(f"{label} ", format_value(safe_get(p1_clean, key)))

    # Player 2 column
    with col_p2:
        st.markdown(f"{p2_clean['player_name']}")
        for label, key in metrics:
            st.metric(f"{label} ", format_value(safe_get(p2_clean, key)))

# --------------------------- SEARCH + SELECT ---------------------------

# utils/players.py

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

def get_position(df, player_name):
    rows = df[df["player_name"] == player_name]

    # If we don't have that player or no position column, return empty string
    if rows.empty or "position" not in rows.columns:
        return ""

    # Safe to access first row now
    return str(rows["position"].iloc[0])

def select_single_player(df, label="Player", key_prefix="p"):
    # --- Precompute positions for fast lookup ---
    pos_map = (
        df[["player_name", "position"]]
        .dropna(subset=["position"])
        .drop_duplicates("player_name")
        .set_index("player_name")["position"]
        .astype(str)
        .to_dict()
    )

    placeholder = "— Select a player —"
    players = [placeholder] + sorted([html.unescape(name) for name in df["player_name"].unique()]) # unescape to get rid of weird characters

    
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

    # If user hasn't selected a real player yet, stop here
    if player == placeholder:
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