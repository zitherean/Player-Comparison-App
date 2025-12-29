import streamlit as st
from utils.update_metadata import get_last_update

# --------------------------- HOME PAGE ---------------------------

st.set_page_config(page_title="Home", layout="wide")

st.title("⚽ Football Player Comparison Dashboard")

st.markdown("""Welcome to the Football Player Comparison Dashboard!
            This app allows you to compare football players from
            top European leagues using data sourced from [Understat.com](https://understat.com).""")

# --------------------------- SECTION 1: MAIN DASHBOARDS ---------------------------
st.subheader("Player Performance")

st.markdown("Use the sidebar or the buttons below to explore different aspects of player performance.")

col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    if st.button("🕸️ Player Profile"):
        st.switch_page("pages/1_🕸️_Player_Profile.py")

with col2:
    if st.button("🥅 Finishing"):
        st.switch_page("pages/1_🥅_Finishing.py")

with col3:
    if st.button("🎯 Creativity"):
        st.switch_page("pages/2_🎯_Creativity.py")

with col4:
    if st.button("🔁 Build Up Play"):
        st.switch_page("pages/3_🔁_Build_Up_Play.py")

with col5:
    if st.button("📐 Metrics"):
        st.switch_page("pages/4_📐_Metrics.py")

with col6:
    if st.button("🥇 Leaderboard"):
        st.switch_page("pages/5_🥇_Leaderboard.py")

# --------------------------- SECTION 2: MORE TOOLS ---------------------------

st.subheader("More Tools")

st.markdown("""If you’re looking for specific profiles, use **Find Players** to search and filter the dataset.""")

if st.button("🔍 Find Players"):
    st.switch_page("pages/6_🔍_Find_Players.py")

st.markdown("""If you're unsure about player positions or metrics, check the **Glossary** for short explanations.""")

if st.button("📘 Glossary"):
    st.switch_page("pages/7_📘_Glossary.py")

st.divider()

# --------------------------- FOOTER ---------------------------

st.caption("###### Disclaimer")

st.caption("""This app is intended for informational and educational purposes only. 
            The developer has no affiliation with Understat.""")

st.caption("© 2025 Sami Finkbeiner") 

meta = get_last_update()

if meta:
    st.caption(f"Data last updated: **{meta['updated_at_utc']}**")
else:
    st.caption("Data last updated: unknown")
