import streamlit as st
import pandas as pd
import plotly.express as px
import glob

# --------------------------- PAGE CONFIGURATION ---------------------------
st.set_page_config(page_title="Top 5 European Leagues Player Comparison", layout="wide")

st.title("⚽ Player Comparison Dashboard")

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
    "npxG_per90": "NPxG per 90",
    "xGBuildup": "xG Buildup",
    "xGBuildup_per90": "xG Buildup per 90",
    "xGChain": "xG Chain",
    "xGChain_per90": "xG Chain per 90",
}

# --------------------------- HELPER FUNCTIONS ---------------------------

def safe_index(options, value, fallback=0):
    """Safely return index of value in list; fallback to given index if missing."""
    try:
        return options.index(value)
    except Exception:
        return fallback if options else 0

# --------------------------- SIDEBAR: DATA LOAD ---------------------------

st.sidebar.header("Data Upload")

try:
    # Find all parquet files recursively (each partition = league/season)
    paths = glob.glob(f"{PARQUET_PATH}/league=*/season=*/*.parquet")
    if not paths:
        st.sidebar.error("No data files found.")
        st.stop()
    
    # Load and combine all league/season parquet files into a single DataFrame
    dfs = []
    for p in paths:
        _df = pd.read_parquet(p)      
        _df["league"] = _df["league"].astype(str)
        _df["season"] = _df["season"].astype(str)
        dfs.append(_df)

    # Merge all data
    df = pd.concat(dfs, ignore_index=True)
    st.sidebar.success("Data file loaded successfully.") 

except Exception as e:
    st.sidebar.error(f"Error loading data file: {e}")
    st.stop()

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

# --------------------------- SIDEBAR: PLAYER COMPARISON ---------------------------

st.sidebar.header("Comparison Options")

# Two side-by-side columns in the sidebar for player 1 and player 2 selections
colA, colB = st.sidebar.columns(2)
with colA:
    player1_data, label1 = player_scope(df, "Player 1", default_season="2024", default_player="Erling Haaland")
with colB:    
    player2_data, label2 = player_scope(df, "Player 2", default_season="2024", default_player="Alexander Isak")

# --------------------------- SIDEBAR: STAT TYPE TOGGLE ---------------------------

st.sidebar.header("Stat Type")
stat_type = st.sidebar.radio("Select Stat Type", ('Total Stats', 'Per 90 mins'))

# --------------------------- PLAYER INFO DISPLAY ---------------------------

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

st.divider()

# --------------------------- COMPARISON PLOT FUNCTION ---------------------------

def plot_comparison(stats, unique_title):
    """
    Create a horizontal bar chart comparing two players for the given list of stats.
    - stats: list of column names to compare
    - unique_title: section title (e.g. "Finishing", "Creativity")
    """
    plot_df = pd.DataFrame({'stat': stats * 2,
                        'series': [label1] * len(stats) + [label2] * len(stats),
                        'value': [player1_data[stat] for stat in stats] + [player2_data[stat] for stat in stats]})
    
    # Round numeric values for cleaner display
    plot_df['value'] = plot_df['value'].round(2)

    # Replace technical column names with readable labels
    plot_df['stat_label'] = plot_df['stat'].map(lambda s: METRIC_LABELS.get(s, s))

    fig_bar = px.bar(
        plot_df,    
        x='value',
        y='stat_label',
        color='series',
        barmode='group',
        orientation='h',
        labels={'value': 'Per 90', 'stat_label': 'Metric', 'series': 'Legend'} if stat_type == 'Per 90 mins' else {'value': 'Total', 'stat_label': 'Metric', 'series': 'Legend'},
        height=max(350, 80 * len(stats)),
        title=unique_title,
        subtitle=f"{player1_data['player_name']} vs {player2_data['player_name']}"
    )
    
    # Center the title for aesthetics
    fig_bar.update_layout(title={'text': unique_title, 'x': 0.5, 'xanchor': 'center', 'yanchor': 'top'})

    st.plotly_chart(fig_bar, use_container_width=True)

# --------------------------- METRIC SECTIONS ---------------------------

# --- Finishing Metrics ---
st.subheader("🥅 Finishing")
finishing_stats = ['goals', 'xG', 'shots', 'npg', 'npxG']
finishing_stats_per_90 = ['goals_per90', 'xG_per90', 'shots_per90', 'npg_per90', 'npxG_per90']
finishing_stats.reverse() # the list shows from top to down
finishing_stats_per_90.reverse()
unique_title = "Finishing"
plot_comparison(finishing_stats_per_90 if stat_type == 'Per 90 mins' else finishing_stats, unique_title)

st.divider()

# --- Creativity Metrics ---
st.subheader("🎯 Creativity")
creativity_stats = ['assists', 'xA', 'key_passes']
creativity_stats_per_90 = ['assists_per90', 'xA_per90', 'key_passes_per90']
creativity_stats.reverse() # the list shows from top to down
creativity_stats_per_90.reverse()
unique_title = "Creativity"
plot_comparison(creativity_stats_per_90 if stat_type == 'Per 90 mins' else creativity_stats, unique_title)

st.divider()

# --- Build-Up Play Metrics ---
st.subheader("🔁 Build Up Play")
buildup_stats = ['xGChain', 'xGBuildup']
buildup_stats_per_90 = ['xGChain_per90', 'xGBuildup_per90']
unique_title = "Build Up Play"
plot_comparison(buildup_stats_per_90 if stat_type == 'Per 90 mins' else buildup_stats, unique_title)

st.divider()

# --------------------------- FOOTER ---------------------------

st.markdown("### About this App", unsafe_allow_html=True)

st.markdown("""This Streamlit app allows users to compare football players from top European 
            leagues using data sourced from [Understat.com](https://understat.com). 
            This app is intended for informational and educational purposes only. 
            The developer has no affiliation with Understat.""", unsafe_allow_html=True)

st.markdown("""© 2025 Sami Finkbeiner""", unsafe_allow_html=True) 