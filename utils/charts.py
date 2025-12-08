import pandas as pd
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
        title=None,  # we'll set a richer title layout below
    )

    # Center title and include subtitle (if you like)
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