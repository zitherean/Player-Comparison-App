# --------------------------- CONSTANTS/MAPS ---------------------------
# Base directory for Parquet files
PARQUET_PATH = "data/understat_players"

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
}