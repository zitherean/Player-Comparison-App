import streamlit as st
import pandas as pd

# --------------------------- FILTER ---------------------------

def multiselect_filter(label, series, key, default=None, sort_reverse=False, default_all=False, format_func=None):
    options = sorted(series.dropna().unique(), reverse=sort_reverse)

    store_key = f"__store__{key}"

    # Load persisted selection first (if any)
    persisted = st.session_state.get(store_key, None)

    # Decide default_value
    if persisted is not None:
        default_value = list(persisted)
    else:
        if default_all:
            default_value = list(options)
        elif default is None:
            default_value = []
        else:
            default_value = list(default)

    # Keep only valid defaults that exist in options
    default_value = [v for v in default_value if v in options]

    if format_func is None:
        value = st.multiselect(label, options=options, default=default_value, key=key)
    else:
        value = st.multiselect(label, options=options, default=default_value, key=key, format_func=format_func)

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

