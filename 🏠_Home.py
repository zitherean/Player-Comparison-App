import streamlit as st

# --------------------------- HOME PAGE ---------------------------

st.set_page_config(page_title="Home", layout="wide")

st.title("⚽ Football Player Comparison Dashboard")

st.markdown("""Welcome to the Football Player Comparison Dashboard!
            This app allows you to compare football players from
            top European leagues using data sourced from [Understat.com](https://understat.com).""")
st.markdown("Use the sidebar or the buttons below to explore different aspects of player performance.")

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("🥅 Finishing"):
        st.switch_page("pages/1_🥅_Finishing.py")

with col2:
    if st.button("🎯 Creativity"):
        st.switch_page("pages/2_🎯_Creativity.py")

with col3:
    if st.button("🔁 Build Up Play"):
        st.switch_page("pages/3_🔁_Build_Up_Play.py")

with col4:
    if st.button("🔍 Find Players"):
        st.switch_page("pages/4_🔍_Find_Players.py")

st.divider()

st.markdown("##### Disclaimer")

st.markdown("""This app is intended for informational and educational purposes only. 
            The developer has no affiliation with Understat.""")

st.markdown("© 2025 Sami Finkbeiner") 