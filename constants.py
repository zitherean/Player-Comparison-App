from utils.season import get_current_understat_season, season_to_name

# --------------------------- CONSTANTS/MAPS ---------------------------
# Base directory for Parquet files
PARQUET_PATH = "data/understat_players"

CURRENT_SEASON = get_current_understat_season()
CURRENT_SEASON_NAME = season_to_name(CURRENT_SEASON)

# Friendly names for leagues as displayed in dropdowns
LEAGUE_NAME_MAP = { 
    "EPL": "Premier League",
    "La_liga": "La Liga",
    "Bundesliga": "Bundesliga",
    "Serie_A": "Serie A",
    "Ligue_1": "Ligue 1",
}

# Mapping of column names to human-readable metric labels for display
METRIC_LABELS = {
    "id": "Player ID",
    "player_name": "Player Name",
    "games": "Games Played",
    "time": "Minutes Played",
    "yellow_cards": "Yellow Cards",
    "red_cards": "Red Cards",
    "team_title": "Team",
    "position": "Position",
    "league": "League",
    "season": "Season",
    "goals": "Goals",
    "xG": "Expected Goals (xG)",
    "shots": "Shots",
    "assists": "Assists",
    "xA": "Expected Assists (xA)",
    "key_passes": "Key Passes",
    "npg": "Non-Penalty Goals",
    "npxG": "Non-Penalty xG",
    "goals_per90": "Goals per 90",
    "xG_per90": "xG per 90",
    "shots_per90": "Shots per 90",
    "assists_per90": "Assists per 90",
    "xA_per90": "xA per 90",
    "key_passes_per90": "Key Passes per 90",
    "npg_per90": "NP Goals per 90 ",
    "npxG_per90": "NP xG per 90",
    "xGBuildup": "xG Buildup",
    "xGBuildup_per90": "xG Buildup per 90",
    "xGChain": "xG Chain",
    "xGChain_per90": "xG Chain per 90",
    "goal_contrib": "Goals + Assists",
    "conversion_rate": "Conversion Rate (%)",
    "assists_per_key_pass": "Assists per Key Pass",     
}

STAT_FILTERS = [
    ("games", "min_games"),
    ("time", "min_minutes"),
    ("goals", "min_goals"),
    ("assists", "min_assists"),
    ("goals_per90", "min_goals_per90"),
    ("assists_per90", "min_assists_per90"),
    ("xG", "min_xg"),
    ("xA", "min_xa"),
    ("xG_per90", "min_xg_per90"),
    ("xA_per90", "min_xa_per90"),
    ("xGChain", "min_xg_chain"),
    ("xGBuildup", "min_xg_buildup"),
    ("xGChain_per90", "min_xg_chain_per90"),
    ("xGBuildup_per90", "min_xg_buildup_per90"),
]