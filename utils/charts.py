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

# --------------------------- RADAR PLOT FUNCTION ---------------------------

def _percentile_series(values: pd.Series) -> pd.Series:
    """
    Convert raw values into percentiles [0..100] using rank.
    Higher = better.
    """
    s = pd.to_numeric(values, errors="coerce")
    # rank(pct=True) gives [0..1], multiply to [0..100]
    return s.rank(pct=True) * 100


def plot_radar(df, player1_data, player2_data, label1, label2, stats, title="Radar", fill = True):
    """
    Returns a Plotly radar chart comparing up to 2 players.
    - df is used to compute percentiles

    """
    if (player1_data is None) and (player2_data is None):
        return None

    if len(stats) < 3:
        return None

    # Axis labels
    categories = [METRIC_LABELS.get(s, s) for s in stats]

    # Compute normalization frame
    pd.DataFrame({s: _percentile_series(df[s]) for s in stats})
    r_min, r_max = 0, 100

    def player_r_values(player_row):
        raw = []
        for s in stats:
            v = player_row.get(s) if hasattr(player_row, "get") else player_row[s]
            raw.append(v)

        raw_s = pd.to_numeric(pd.Series(raw), errors="coerce")
            # For each stat, compute the percentile position of that player's value
            # by using the df-wide percentile distribution.
            # We do this by ranking within df; easiest: compute rank of value among df.
        vals = []
        for i, s in enumerate(stats):
            v = raw_s.iloc[i]
            if pd.isna(v):
                vals.append(np.nan)
            else:
                # percentile position of v relative to df[s]
                # (same logic as rank(pct=True) but for a single value)
                col = pd.to_numeric(df[s], errors="coerce").dropna().values
                if len(col) == 0:
                    vals.append(np.nan)
                else:
                    vals.append(float((col <= v).mean() * 100))
        return vals

    fig = go.Figure()

    # Add Player 1
    if player1_data is not None:
        r1 = player_r_values(player1_data)
        fig.add_trace(
            go.Scatterpolar(
                r=r1 + [r1[0]],
                theta=categories + [categories[0]],
                name=label1,
                fill="toself" if fill else None,
            )
        )

    # Add Player 2
    if player2_data is not None:
        r2 = player_r_values(player2_data)
        fig.add_trace(
            go.Scatterpolar(
                r=r2 + [r2[0]],
                theta=categories + [categories[0]],
                name=label2,
                fill="toself" if fill else None,
            )
        )

    fig.update_layout(
        title={"text": title, "x": 0.5, "xanchor": "center"},
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[r_min, r_max] if (r_min is not None and r_max is not None) else None,
            )
        ),
        showlegend=True,
        margin=dict(l=40, r=40, t=60, b=40),
    )

    return fig
