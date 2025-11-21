import streamlit as st
import math
import html
from constants import LEAGUE_NAME_MAP, PARQUET_PATH, SEASON_NAME_MAP
from utils.data_loader import load_understat_data

# --------------------------- ENRICH PLAYER METRICS ---------------------------

def to_num(val, default=0.0):
    """Safely convert value to float; fallback to default on error."""
    if val is None:
        return default
    try:
        return float(val)
    except (ValueError, TypeError):
        return default


def enrich_player_metrics(player):
    """
    Take a dict/Series-like 'player' and add derived metrics in-place.
    Returns the same object for convenience.
    """

    # Make a copy of the original
    player = player.copy()

    goals       = to_num(player.get("goals"))
    assists     = to_num(player.get("assists"))
    xG          = to_num(player.get("xG"))
    xA          = to_num(player.get("xA"))
    npg         = to_num(player.get("npg"))
    npxG        = to_num(player.get("npxG"))
    shots       = to_num(player.get("shots"))
    key_passes  = to_num(player.get("key_passes"))
    time_min    = to_num(player.get("time"))   
    games       = to_num(player.get("games"))
    xg_buildup  = to_num(player.get("xGBuildup"))
    xg_chain    = to_num(player.get("xGChain"))

    goals_per90     = to_num(player.get("goals_per90"))
    assists_per90   = to_num(player.get("assists_per90"))
    xG_per90        = to_num(player.get("xG_per90"))
    xA_per90        = to_num(player.get("xA_per90"))
    key_passes_per90 = to_num(player.get("key_passes_per90"))
    xg_buildup_per90  = to_num(player.get("xGBuildup_per90"))
    xg_chain_per90    = to_num(player.get("xGChain_per90"))
        

    yellow_cards = to_num(player.get("yellow_cards"))
    red_cards    = to_num(player.get("red_cards"))

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
        player["xA_per_key_pass"] = xA / key_passes
    else:
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
def player_search(df):
    """
    Widget group to search players by:
    - Player name (optional, with text search)
    - League, Season, Team (any combination)

    Returns:
        filtered_df (pd.DataFrame): DataFrame filtered according to the selected criteria.
    """

    # --- BASE OPTIONS FROM DATAFRAME ---
    all_players = sorted(html.unescape(name) for name in df["player_name"].unique())
    all_seasons = sorted(df["season"].unique(), reverse=True)
    all_leagues = sorted(df["league"].unique())
    all_teams = sorted(df["team_title"].unique())

    # ---------------- RESET BUTTON ----------------
    reset = st.button("🔁 Reset filters")

    if reset:
        # Clear text input
        st.session_state["player_name_query"] = ""

        # Reset dropdowns to "All ..." options
      
        st.session_state["season_select"] = "All seasons"
        st.session_state["league_select"] = "All leagues"
        st.session_state["team_select"] = "All teams"

        # Clear any dynamic player select keys
        for key in list(st.session_state.keys()):
            if key.startswith("player_select_"):
                del st.session_state[key]
                st.session_state[key] = "All players"
        st.rerun()

    # ---------------- NAME SEARCH ----------------
    st.subheader("Search by player name")

    name_query = st.text_input("Type part of the player's name (optional)", value="", key="player_name_query", placeholder="e.g. Salah, De Bruyne, Messi...")

    if name_query:
        # Filter list of players shown in the selectbox
        filtered_player_options = [p for p in all_players if name_query.lower() in p.lower()]
        if not filtered_player_options:
            st.info("No players found matching that name. Try adjusting your search or using the filters below.")
            filtered_player_options = all_players  # fallback
    else:
        filtered_player_options = all_players

    # Default index for the selectbox
    default_index = 1 if (name_query and filtered_player_options) else 0

    player = st.selectbox("Select player (or leave as 'All players' to use only filters)", options=["All players"] + filtered_player_options, key=f"player_select_{name_query}", index=default_index)

    st.markdown("— or filter using league, season, and team —")

    # ---------------- FILTERS: LEAGUE / SEASON / TEAM ----------------
    col1, col2, col3 = st.columns(3)

    with col1:
        season = st.selectbox("Season", options=["All seasons"] + all_seasons, key="season_select", format_func=lambda x: SEASON_NAME_MAP.get(x, x))

    with col2:
        league = st.selectbox("League", options=["All leagues"] + all_leagues, key="league_select", format_func=lambda x: LEAGUE_NAME_MAP.get(x, x))

    with col3:
        team = st.selectbox("Team", options=["All teams"] + all_teams, key="team_select")

    # ---------------- APPLY FILTERS TO DATAFRAME ----------------
    filtered_df = df.copy()

    # Player filter (takes precedence if chosen)
    if player != "All players":
        filtered_df = filtered_df[filtered_df["player_name"] == player]

    # Additional filters (work whether or not a player is chosen)
    if season != "All seasons":
        filtered_df = filtered_df[filtered_df["season"] == season]

    if league != "All leagues":
        filtered_df = filtered_df[filtered_df["league"] == league]

    if team != "All teams":
        filtered_df = filtered_df[filtered_df["team_title"] == team]

    unique_players = filtered_df["player_name"].nunique()

    st.markdown(f"🔎 Found **{(unique_players)}** matching players.")

    return filtered_df, player

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