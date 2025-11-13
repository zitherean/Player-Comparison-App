import streamlit as st
from constants import LEAGUE_NAME_MAP, PARQUET_PATH
from utils.data_loader import load_understat_data

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


# --------------------------- PLAYER INFO DISPLAY ---------------------------

def display_player_info(player1_data, player2_data):
    col1, col2 = st.columns(2)
    # --- Player 1 Info ---
    with col1:
        st.markdown(f"<h3 style='marginbottom:0'>{player1_data['player_name']} " f"<span style='font-size:0.8em;color:gray;'>({player1_data['position']})</span></h3>", unsafe_allow_html=True)
        st.markdown(f"**Team**: {player1_data['team_title']}")
        st.markdown(f"**Games played**: {player1_data['games']}")
        st.markdown(f"**Minutes played**: {player1_data['time']}")
        st.markdown(f"**Red cards**: {player1_data['red_cards']}")
        st.markdown(f"**Yellow cards**: {player1_data['yellow_cards']}")

    # --- Player 2 Info ---
    with col2:
        st.markdown(f"<h3 style='marginbottom:0'> {player2_data['player_name']} " f"<span style='font-size:0.8em;color:gray;'>({player2_data['position']})</span></h3>", unsafe_allow_html=True)   
        st.markdown(f"**Team**: {player2_data['team_title']}")
        st.markdown(f"**Games played**: {player2_data['games']}")
        st.markdown(f"**Minutes played**: {player2_data['time']}")
        st.markdown(f"**Red cards**: {player2_data['red_cards']}")
        st.markdown(f"**Yellow cards**: {player2_data['yellow_cards']}")

# --------------------------- SEARCH + SELECT ---------------------------

# utils/players.py

import streamlit as st

def select_single_player(df, label="Player", key_prefix="p"):
    
    players = sorted(df["player_name"].unique())

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

    season = st.selectbox("Filter by season (optional)", seasons, index=season_idx, key=f"{key_prefix}_season_select")

    st.session_state[f"{key_prefix}_season_value"] = season

    if season != "All seasons":
        rows = rows[rows["season"] == season]

    rows = rows.sort_values("season", ascending=False)
    row = rows.iloc[0]

    label_str = f"{row['player_name']} ({row['season']}, {row['team_title']})"

    return row, label_str

