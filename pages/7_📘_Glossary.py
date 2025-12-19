import streamlit as st

# --------------------------- PAGE CONFIGURATION ---------------------------

st.set_page_config(page_title="Glossary", layout="wide")

st.title("📘 Glossary")

st.markdown(
    """
    **General notes** 
    - **Non-penalty (NP)** metrics exclude goals and xG from penalty kicks.
    """
)

# --------------------------- GROUPED METRICS ---------------------------

# Grouped metrics: (display name, definition)
metrics = {
    "Player & match context": [
        ("Player Name", "Name of the player."),
        ("Team", "Club or team the player appeared for."),
        ("League", "Competition the matches were played in."),
        ("Season", "Season of the data shown."),
        ("Position", "Player’s primary on-pitch role (e.g. F, M, D)."),
        ("Games Played", "Number of matches in which the player appeared."),
        ("Minutes Played", "Total minutes played across all matches."),
    ],

    "Discipline": [
        ("Yellow Cards", "Total yellow cards received."),
        ("Red Cards", "Total red cards received."),
    ],

    "Scoring output": [
        ("Goals", "Total non-own goals scored (including penalties unless stated otherwise)."),
        ("Goals per 90", "Goals scored per 90 minutes played."),
        ("Non-Penalty Goals", "Goals scored from open play and non-penalty situations only."),
        ("NP Goals per 90", "Non-penalty goals per 90 minutes played."),
        ("Goals + Assists", "Combined total of goals and assists."),
        ("Conversion Rate (%)", "Percentage of shots that result in a goal (Goals ÷ Shots × 100)."),
    ],

    "Shooting & xG": [
        ("Shots", "Total shots taken (on and off target)."),
        ("Shots per 90", "Shots taken per 90 minutes played."),
        ("Expected Goals (xG)", "Total xG: sum of the chance quality of all shots taken (including penalties)."),
        ("xG per 90", "Expected goals per 90 minutes played."),
        ("Non-Penalty xG", "xG from open play and non-penalty situations only."),
        ("NP xG per 90", "Non-penalty xG per 90 minutes played."),
    ],

    "Creativity & xA": [
        ("Assists", "Passes or actions that directly lead to a teammate’s goal."),
        ("Assists per 90", "Assists per 90 minutes played."),
        ("Expected Assists (xA)", "Total xA: quality of chances created for teammates (likelihood a pass becomes a shot that is scored)."),
        ("xA per 90", "Expected assists per 90 minutes played."),
        ("Key Passes", "Passes that create a shot for a teammate."),
        ("Key Passes per 90", "Key passes played per 90 minutes."),
        ("Assists per Key Pass", "Share of key passes that result in an assist (Assists ÷ Key Passes)."),
    ],

    "Buildup & involvement": [
        ("xG Buildup", "xG value of possessions the player helps build, excluding their own shots and key passes."),
        ("xG Buildup per 90", "xG Buildup contribution per 90 minutes played."),
        ("xG Chain", "Total xG of every possession sequence in which the player is involved (including shots, passes, and involvement earlier in the move)."),
        ("xG Chain per 90", "xG Chain contribution per 90 minutes played."),
    ],
}

# --------------------------- DISPLAY ---------------------------

for group_name, group_metrics in metrics.items():
    st.subheader(group_name)
    for display_name, definition in group_metrics:
        st.markdown(f"**{display_name}**  \n{definition}")

st.info("Check how a metric behaves per 90 minutes to compare players with different playing time.")

st.divider()

# --------------------------- PLAYER POSITIONS ---------------------------

st.subheader("Player positions")

st.markdown(
    """
    Positions are shown using short letter codes.  
    Multiple letters indicate **hybrid roles**, and **S** indicates a **substitute appearance**.
    """
)

positions = [
    ("GK", "Goalkeeper"),
    ("D", "Defender"),
    ("M", "Midfielder"),
    ("F", "Forward"),
    ("S", "Substitute appearance"),
]

for code, description in positions:
    st.markdown(f"**{code}** -- {description}")

st.info("Player positions are based on Understat's classification and may not reflect exact tactical roles.")