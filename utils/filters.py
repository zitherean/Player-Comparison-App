import streamlit as st
import pandas as pd
from utils.players import accumulate_player_rows


# --------------------------- FILTER ---------------------------

def multiselect_filter(label, series, key, default=None, sort_reverse=False):
    options = sorted(series.unique(), reverse=sort_reverse)

    store_key = f"__store__{key}"        
    default = st.session_state.get(store_key, default)
    # keep defaults valid
    default = [v for v in default if v in options]

    value = st.multiselect(label, options=options, default=default, key=key)

    # persist selection for next time you visit the page
    st.session_state[store_key] = value
    return value

def number_input_persist(label, key, min_value, max_value, value, step=1):
    # initialize once
    
    store_key = f"__store__{key}"
    initial = st.session_state.get(store_key, value)

    val = st.number_input(label, value=initial, min_value=min_value, max_value=max_value, step=step, key=key)

    # persist selection for next time you visit the page
    st.session_state[store_key] = val
    return val

def apply_list_filter(df, column, selected):
    if selected:
        return df[df[column].isin(selected)]
    return df

def apply_stat_filters(df, filters):
    for col, state_key in filters:
        value = st.session_state.get(state_key, 0)
        if value > 0 and col in df.columns:
            df = df[df[col] >= value]
    return df

# --------------------------- DATAFRAME ---------------------------

def get_result_dataframe(df, selected_seasons):
    if len(selected_seasons) != 1:
        aggregated_rows = []

        for _, rows in df.groupby("player_name"):
            aggregated_rows.append(accumulate_player_rows(rows, minutes_col="time", per90_suffix="_per90"))

        return pd.DataFrame(aggregated_rows)

    return df.drop_duplicates(subset=["player_name", "season", "team_title"])