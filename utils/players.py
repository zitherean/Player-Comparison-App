import streamlit as st
import math
import html
from constants import LEAGUE_NAME_MAP, SEASON_NAME_MAP
from utils.season import SEASON_NAME_MAP
from utils.data_loader import load_understat_data

# --------------------------- ENRICH PLAYER METRICS ---------------------------

def enrich_player_metrics(player):
    """
    Take a dict/Series-like 'player' and add derived metrics in-place.
    Returns the same object for convenience.
    """

    # Make a copy of the original
    player = player.copy()

    goals       = player.get("goals")
    assists     = player.get("assists")
    xG          = player.get("xG")
    xA          = player.get("xA")
    npg         = player.get("npg")
    npxG        = player.get("npxG")
    shots       = player.get("shots")
    key_passes  = player.get("key_passes")
    time_min    = player.get("time")
    games       = player.get("games")
    xg_buildup  = player.get("xGBuildup")
    xg_chain    = player.get("xGChain")

    goals_per90     = player.get("goals_per90")
    assists_per90   = player.get("assists_per90")
    xG_per90        = player.get("xG_per90")
    xA_per90        = player.get("xA_per90")
    key_passes_per90 = player.get("key_passes_per90")
    xg_buildup_per90  = player.get("xGBuildup_per90")
    xg_chain_per90    = player.get("xGChain_per90")
        

    yellow_cards = player.get("yellow_cards")
    red_cards    = player.get("red_cards")

    # ---------- ATTACKING OUTPUT ----------
    player["goal_contrib"] = goals + assists                        
    player["goal_contrib_per90"] = goals_per90 + assists_per90      

    # Over/underperformance
    player["goals_minus_xG"] = goals - xG
    player["npg_minus_npxG"] = npg - npxG

    # ---------- EFFICIENCY ----------
    # Conversion rate
    if shots > 0:
        player["conversion_rate"] = (goals / shots) * 100
        player["xG_per_shot"] = xG / shots
    else:
        player["conversion_rate"] = math.nan
        player["xG_per_shot"] = math.nan

    # chance quality created
    if key_passes > 0:
        player["assists_per_key_pass"] = assists / key_passes
        player["xA_per_key_pass"] = xA / key_passes
    else:
        player["assists_per_key_pass"] = math.nan        
        player["xA_per_key_pass"] = math.nan

    # ---------- USAGE / INVOLVEMENT ----------
    if games > 0:
        player["mins_per_game"] = time_min / games
        player["goal_contrib_per_game"] = (goals + assists) / games
    else:
        player["mins_per_game"] = math.nan
        player["goal_contrib_per_game"] = math.nan

    # ---------- DISCIPLINE ----------
    if time_min > 0:
        factor = 90.0 / time_min
        player["yellow_per90"] = yellow_cards * factor
        player["red_per90"] = red_cards * factor
    else:
        player["yellow_per90"] = math.nan
        player["red_per90"] = math.nan

    return player

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

def format_value(val):
    try:
        return f"{float(val):.2f}"
    except:
        return str(val)

def display_key_stats(title, p1_clean, p2_clean, metrics):
    """
    """
    st.markdown(f"### {title}")

    cols = st.columns(len(metrics))

    for col, (label, key) in zip(cols, metrics):
        with col:
            st.metric(f"{label} ({p1_clean['player_name']})", format_value(safe_get(p1_clean, key)))
            st.metric(f"{label} ({p2_clean['player_name']})", format_value(safe_get(p2_clean, key)))

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


def select_single_player(df, label="Player", key_prefix="p"):
    
    players = sorted([html.unescape(name) for name in df["player_name"].unique()]) # unescape to get rid of weird characters

    # Use previously selected value (if it exists) as default
    default_name = st.session_state.get(f"{key_prefix}_player_name")
    if default_name in players:
        default_idx = players.index(default_name)
    else:
        default_idx = 0

    player = st.selectbox(f"Select {label}", players, index=default_idx, key=f"{key_prefix}_player_select")

    # Save the selection so other pages can reuse it
    st.session_state[f"{key_prefix}_player_name"] = player

    # Filter rows for that player
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