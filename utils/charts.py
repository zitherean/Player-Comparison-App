import pandas as pd
import plotly.express as px
from constants import METRIC_LABELS

# --------------------------- COMPARISON PLOT FUNCTION ---------------------------

def plot_comparison(player1_data, player2_data, label1, label2, stats, stat_type, title):
    """
    Create a horizontal bar chart comparing two players for the given list of stats.
    - stats: list of column names to compare
    - title: section title (e.g. "Finishing", "Creativity")
    """
    plot_df = pd.DataFrame({'stat': stats * 2,
                        'series': [label1] * len(stats) + [label2] * len(stats),
                        'value': [player1_data[stat] for stat in stats] + [player2_data[stat] for stat in stats]})
    
    # Round numeric values for cleaner display
    plot_df['value'] = plot_df['value'].round(2)

    # Replace technical column names with readable labels
    plot_df['stat_label'] = plot_df['stat'].map(lambda s: METRIC_LABELS.get(s, s))

    fig = px.bar(
        plot_df,    
        x='value',
        y='stat_label',
        color='series',
        barmode='group',
        orientation='h',
        labels={'value': 'Per 90', 'stat_label': 'Metric', 'series': 'Legend'} if stat_type == 'Per 90 mins' else {'value': 'Total', 'stat_label': 'Metric', 'series': 'Legend'},
        height=max(350, 80 * len(stats)),
        title=title,
        subtitle=f"{player1_data['player_name']} vs {player2_data['player_name']}"
    )
    
    # Center the title for aesthetics
    fig.update_layout(title={'text': title, 'x': 0.5, 'xanchor': 'center', 'yanchor': 'top'})

    return fig