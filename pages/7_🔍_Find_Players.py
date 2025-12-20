import streamlit as st
from constants import PARQUET_PATH, LEAGUE_NAME_MAP, METRIC_LABELS, STAT_FILTERS, FLOAT_KEYS, RESET_KEYS
from utils.data_loader import load_understat_data
from utils.players import enrich_player_metrics
from utils.filters import multiselect_filter, number_input_persist, apply_list_filter, apply_stat_filters, get_result_dataframe
from utils.text import clean_html_entities
from utils.season import SEASON_NAME_MAP

# --------------------------- PAGE CONFIGURATION ---------------------------

st.set_page_config(page_title="Find Players", layout="wide")
st.title("🔍 Find Players")

# --------------------------- LOAD & PREP DATA -----------------------------

df = load_understat_data(PARQUET_PATH)

df = clean_html_entities(df, ["player_name", "team_title"])
df = df.replace({**LEAGUE_NAME_MAP, **SEASON_NAME_MAP})
df = enrich_player_metrics(df)

# --------------------------- FILTERS --------------------------------------

st.subheader("Filters")

col1, col2, col3, col4 = st.columns(4)

with col1:
    selected_seasons = multiselect_filter("Season(s)", df["season"], f"seasons_multifilter", sort_reverse=True)
    df_seasons = df[df["season"].isin(selected_seasons)] if selected_seasons else df

with col2:
    selected_leagues = multiselect_filter("League(s)", df_seasons["league"], f"leagues_multifilter")
    df_leagues = df_seasons[df_seasons["league"].isin(selected_leagues)] if selected_leagues else df_seasons

with col3:
    selected_teams = multiselect_filter("Team(s)", df_leagues["team_title"], f"teams_multifilter")
    df_teams = df_leagues[df_leagues["team_title"].isin(selected_teams)] if selected_teams else df_leagues

with col4:
    selected_positions = multiselect_filter("Position(s)", df_teams["position"], f"positions_multifilter")

# --------------------------- RESET BUTTON ---------------------------------

st.subheader("Stat filters")

if st.button("🔄 Reset stat filters"):
    for key in RESET_KEYS:
        st.session_state[key] = 0.0 if key in FLOAT_KEYS else 0
        st.session_state[f"__store__{key}"] = 0.0 if key in FLOAT_KEYS else 0         

# --------------------------- BASIC STAT FILTERS ---------------------------------

with st.expander("Basic stat filters"):
    col_s1, col_s2 = st.columns(2)
    
    with col_s1:
        min_games = number_input_persist(
            "Min games played",
            key="min_games",
            min_value=0,
            max_value=int(df["games"].max()),
            value=0,
        )
        min_minutes = number_input_persist(
            "Min minutes played",
            key="min_minutes",
            min_value=0,
            max_value=int(df["time"].max()),
            value=0,
            step=100,
        )

    with col_s2:
        min_goals = number_input_persist(
            "Min goals",
            key="min_goals",
            min_value=0,
            max_value=int(df["goals"].max()),
            value=0,
        )
        min_assists = number_input_persist(
            "Min assists",
            key="min_assists",
            min_value=0,
            max_value=int(df["assists"].max()),
            value=0,
        )

# --------------------------- ADVANCED STAT FILTERS ---------------------------------

with st.expander("Advanced stat filters", expanded=False):
    col_s3, col_s4, col_s5, col_s6, col_s7 = st.columns(5)

    with col_s3:
        min_goals_per90 = number_input_persist(
            "Min goals per 90",
            key="min_goals_per90",
            min_value=0.0,
            max_value=float(df["goals_per90"].max()),
            value=0.0,
            step=0.1,
        )

        min_assists_per90 = number_input_persist(
            "Min assists per 90",
            key="min_assists_per90",
            min_value=0.0,
            max_value=float(df["assists_per90"].max()),
            value=0.0,
            step=0.1,
        )

    with col_s4:
        min_xg = number_input_persist(
            "Min expected goals (xG)",
            key="min_xg",
            min_value=0.0,
            max_value=float(df["xG"].max()),
            value=0.0,
            step=1.0,
        )

        min_xa = number_input_persist(
            "Min expected assists (xA)",
            key="min_xa",
            min_value=0.0,
            max_value=float(df["xA"].max()),
            value=0.0,
            step=1.0,
        )

    with col_s5:
        min_xg_per90 = number_input_persist(
            "Min xG per 90",
            key="min_xg_per90",
            min_value=0.0,
            max_value=float(df["xG_per90"].max()),
            value=0.0,
            step=0.1,
        )

        min_xa_per90 = number_input_persist(
            "Min xA per 90",
            key="min_xa_per90",
            min_value=0.0,
            max_value=float(df["xA_per90"].max()),
            value=0.0,
            step=0.1,
        )

    with col_s6:
        min_xg_chain = number_input_persist(
            "Min xG chain",
            key="min_xg_chain",
            min_value=0.0,
            max_value=float(df["xGChain"].max()),
            value=0.0,
            step=1.0,
        )

        min_xg_buildup = number_input_persist(
            "Min xG buildup",
            key="min_xg_buildup",
            min_value=0.0,
            max_value=float(df["xGBuildup"].max()),
            value=0.0,
            step=1.0,
        )

    with col_s7:
        min_xg_chain_per90 = number_input_persist(
            "Min xG chain per 90",
            key="min_xg_chain_per90",
            min_value=0.0,
            max_value=float(df["xGChain_per90"].max()),
            value=0.0,
            step=0.1,
        )

        min_xg_buildup_per90 = number_input_persist(
            "Min xG buildup per 90",
            key="min_xg_buildup_per90",
            min_value=0.0,
            max_value=float(df["xGBuildup_per90"].max()),
            value=0.0,
            step=0.1,
        )

# --------------------------- APPLY FILTERS --------------------------------

filtered_df = df.copy()

filtered_df = apply_list_filter(filtered_df, "season", selected_seasons)
filtered_df = apply_list_filter(filtered_df, "league", selected_leagues)
filtered_df = apply_list_filter(filtered_df, "position", selected_positions)
filtered_df = apply_list_filter(filtered_df, "team_title", selected_teams)

# --------------------------- AGGREGATION LOGIC ----------------------------

result_df = get_result_dataframe(filtered_df, selected_seasons)

# --------------------------- APPLY STAT FILTERS ---------------------------

result_df = apply_stat_filters(result_df, STAT_FILTERS)

# --------------------------- CLEAN & DISPLAY ------------------------------

st.divider()
st.subheader("Results")

if result_df.empty:
    st.info("No players found for the selected criteria. Try relaxing some filters.")
else:
    desired_order = [
        "player_name",
        "position",
        "team_title",
        "games",
        "time",
        "goals",
        "assists",
        "goal_contrib",
        "xG",
        "xA",
        "xGChain",
        "xGBuildup",
        "goals_per90",
        "assists_per90",
        "xG_per90",
        "xA_per90",
        "xGChain_per90",
        "xGBuildup_per90",
    ]

    existing_cols = [c for c in desired_order if c in result_df.columns]
    clean_data = result_df[existing_cols].copy()
    clean_data = clean_data.rename(columns=METRIC_LABELS)

    st.markdown(f"Players found: {len(clean_data)}")
    st.info("Click on any column header to sort the table by that metric.")

    st.dataframe(clean_data, width="stretch", hide_index=True)