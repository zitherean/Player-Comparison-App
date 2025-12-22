import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from constants import METRIC_LABELS

# --------------------------- COMPARISON PLOT FUNCTION ---------------------------

def plot_comparison(player1_data, player2_data, label1, label2, stats, stat_type, title):
    """
    Create a horizontal bar chart comparing one or two players for the given list of stats.
    - stats: list of column names to compare
    - title: section title (e.g. "Finishing", "Creativity")
    """

    # If absolutely no players, don't plot
    if player1_data is None and player2_data is None:
        return None

    rows = []

    # Add Player 1 rows if available 
    if player1_data is not None:
        for stat in stats:
            rows.append({
                "stat": stat,
                "series": label1,
                "value": player1_data[stat],
            })

    # Add Player 2 rows if available
    if player2_data is not None:
        for stat in stats:
            rows.append({
                "stat": stat,
                "series": label2,
                "value": player2_data[stat],
            })

    plot_df = pd.DataFrame(rows)

    # Round numeric values for cleaner display
    plot_df["value"] = plot_df["value"].round(2)

    # Replace technical column names with readable labels
    plot_df["stat_label"] = plot_df["stat"].map(lambda s: METRIC_LABELS.get(s, s))

    # Axis labels depending on stat_type
    if stat_type == "Per 90 mins":
        labels = {"value": "Per 90", "stat_label": "Metric", "series": "Legend"}
    else:
        labels = {"value": "Total", "stat_label": "Metric", "series": "Legend"}

    # Subtitle text (for info, optional)
    if player1_data is not None and player2_data is not None:
        subtitle = f"{player1_data['player_name']} vs {player2_data['player_name']}"
    elif player1_data is not None:
        subtitle = f"{player1_data['player_name']}"
    else:
        subtitle = f"{player2_data['player_name']}"

    # Build figure
    fig = px.bar(
        plot_df,
        x="value",
        y="stat_label",
        color="series",
        barmode="group",
        orientation="h",
        labels=labels,
        height=max(350, 80 * len(stats)),
        title=None,
        color_discrete_map={
            label1: "#0068c9",  # blue
            label2: "#d62728",  # red
        },
    )

    # Center title and include subtitle
    title_text = title if not subtitle else f"{title}<br><sup>{subtitle}</sup>"
    fig.update_layout(
        title={
            "text": title_text,
            "x": 0.5,
            "xanchor": "center",
            "yanchor": "top",
        }
    )

    return fig

# --------------------------- RADAR PLOT FUNCTION ---------------------------

def player_r_values(player_row, stats, df_stats):
    vals = []
    for s in stats:
        v = player_row.get(s, np.nan)

        if pd.isna(v):
            vals.append(np.nan)
            continue

        col = df_stats[s].dropna().values
        if len(col) == 0:
            vals.append(np.nan)
        else:
            vals.append(float((col <= v).mean() * 100))

    return vals


def plot_radar(df, player1_data, player2_data, label1, label2, stats, title):
    if (player1_data is None) and (player2_data is None):
        return None
    if len(stats) < 3:
        return None

    categories = [METRIC_LABELS.get(s, s) for s in stats]
    r_min = 0
    r_max = 100

    df_stats = df[stats]

    fig = go.Figure()

    if player1_data is not None:
        r1 = player_r_values(player1_data, stats, df_stats)
        fig.add_trace(
            go.Scatterpolar(
                r=r1 + [r1[0]], 
                theta=categories + [categories[0]], 
                name=label1, 
                line=dict(color="#1f77b4"),
                fill="toself",
                fillcolor="rgba(31,119,180,0.35)"

            )
        )

    if player2_data is not None:
        r2 = player_r_values(player2_data, stats, df_stats)
        fig.add_trace(
            go.Scatterpolar(
                r=r2 + [r2[0]], 
                theta=categories + [categories[0]], 
                name=label2, 
                line=dict(color="#d62728"),
                fill="toself",
                fillcolor="rgba(214,39,40,0.35)"

            )
        )

    if player1_data is not None and player2_data is not None:
        subtitle = f"{player1_data['player_name']} vs {player2_data['player_name']}"
    elif player1_data is not None:
        subtitle = f"{player1_data['player_name']}"
    else:
        subtitle = f"{player2_data['player_name']}"

    title_text = f"{title}<br><sup>{subtitle}</sup>"
    fig.update_layout(
        title={"text": title_text, "x": 0.5, "xanchor": "center"}, 
        polar=dict(radialaxis=dict(visible=True, range=[r_min, r_max])), 
        showlegend=True, 
        margin=dict(l=40, r=40, t=60, b=40),
        width=650,
        height=650
    )

    return fig