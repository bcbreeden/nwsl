import plotly.graph_objects as go
from data import (db_games, db_team_xgoals)
import plotly
import json

def plot_spider(stats_to_plot, player_data, label_font_size = 12):
    """
    Generates an interactive spider web graph for player stats with scales based on min_ and max_ values using Plotly.

    Args:
        stats_to_plot (list): A list of stats to plot.
        player_data (sqlite3.Row): A row object containing player xGoals data, including min_ and max_ values for each stat.

    Returns:
        Tuple[str, str]: JSON-encoded Plotly figure and config.
    """
    if len(stats_to_plot) == 0:
        print('No stats provided for spider plot.')
        return [0, 0]
    
    categories = []
    normalized_values = []
    hover_values = []  # Store hover values (non-normalized stats)

    for stat in stats_to_plot:
        min_stat_key = f'min_{stat}'
        max_stat_key = f'max_{stat}'

        # Ensure the stat and its min/max values exist in the player data
        if stat in player_data.keys() and min_stat_key in player_data.keys() and max_stat_key in player_data.keys():
            min_stat = player_data[min_stat_key]
            max_stat = player_data[max_stat_key]
            player_stat = player_data[stat]

            # Skip stats with invalid ranges
            if max_stat == min_stat:
                continue

            # Normalize the player stat to a 0-1 scale
            normalized_stat = (player_stat - min_stat) / (max_stat - min_stat)

            # Append data for plotting
            categories.append(stat.replace('_', ' ').title())
            # categories.append(stat.replace('_', ' ').title().replace(' ', '<br>'))
            normalized_values.append(normalized_stat)
            hover_values.append(f"{stat.replace('_', ' ').title()}: {player_stat}")  # Add hover text
    
    # Close the radar chart loop
    try:
        categories.append(categories[0])
    except IndexError:
        print('No categories provided for spider plot')
        return [0, 0]
    
    normalized_values.append(normalized_values[0])
    hover_values.append(hover_values[0])  # Close the hover loop

    # Create the radar chart
    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=normalized_values,
        theta=categories,
        fill='toself',
        fillcolor='#003049',
        name=player_data['player_name'],
        hoverinfo='text',
        text=hover_values,  # Add hover values
        line=dict(color='#003049'),
        marker=dict(size=1)
    ))

    # Update the layout
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=False,
                range=[0, 1]  # Normalized range
            ),
            angularaxis=dict(
            tickfont=dict(size=label_font_size)  # Set font size for labels (adjust the size as needed)
            )
        ),
        showlegend=False,
    )

    # Convert the figure to JSON and add config to disable displayModeBar
    fig_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    config = json.dumps({
        "displayModeBar": False,  # Disable the toolbar
        "scrollZoom": False,      # Disable zooming with the scroll wheel
        "dragMode": False,
        "staticPlot": True        # Make the plot fully static
    })
    
    return fig_json, config


def plot_bullet_chart(stats_to_plot, player_data):
    """
    Generates a normalized bullet chart (0–1 scale) comparing player stats to min, avg, and max values.

    Args:
        stats_to_plot (list): List of stat names (e.g., 'goals', 'xgoals').
        player_data (sqlite3.Row): Row object with stat, min_, max_, and avg_ values.

    Returns:
        Tuple[str, str]: JSON-encoded Plotly figure and config.
    """
    fig = go.Figure()

    for stat in stats_to_plot:
        stat_label = stat.replace('_', ' ').title()

        val = player_data[stat]
        avg = player_data[f'avg_{stat}']
        min_val = player_data[f'min_{stat}']
        max_val = player_data[f'max_{stat}']

        # Avoid divide-by-zero
        if max_val == min_val:
            continue

        # Normalize all values to 0–1 scale
        val_norm = (val - min_val) / (max_val - min_val)
        avg_norm = (avg - min_val) / (max_val - min_val)

        # Add light gray: min → avg
        fig.add_trace(go.Bar(
            x=[avg_norm],
            y=[stat_label],
            base=0,
            orientation='h',
            marker=dict(color='lightgray'),
            showlegend=False,
            hoverinfo='skip'
        ))

        # Add dark gray: avg → max
        fig.add_trace(go.Bar(
            x=[1 - avg_norm],
            y=[stat_label],
            base=avg_norm,
            orientation='h',
            marker=dict(color='darkgray'),
            showlegend=False,
            hoverinfo='skip'
        ))

        # Player value as a vertical marker
        fig.add_trace(go.Scatter(
            x=[val_norm],
            y=[stat_label],
            mode='markers+lines',
            marker=dict(
                color='#003049',
                size=14,
                symbol='diamond'
            ),
            line=dict(
                color='#003049',
                width=2
            ),
            name=player_data['player_name'],
            hovertemplate=f"{stat_label}: {val:.2f}<extra></extra>"
        ))

    fig.update_layout(
        barmode='stack',
        xaxis=dict(range=[0, 1], showgrid=True),
        yaxis=dict(autorange="reversed", tickfont=dict(size=12)),
        height=40 * len(stats_to_plot) + 100,
        margin=dict(l=120, r=40, t=60, b=40),
        showlegend=False
    )

    fig_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    config = json.dumps({
        "displayModeBar": False,
        "staticPlot": True
    })

    return fig_json, config

def plot_deviation_from_average_chart(stats_to_plot, player_data):
    """
    Generates a horizontal bar chart showing player stat deviations from league average.

    Args:
        stats_to_plot (list): List of stat names (e.g., 'goals', 'xgoals').
        player_data (sqlite3.Row): Row object with stat, avg_, min_, and max_ values.

    Returns:
        Tuple[str, str]: JSON-encoded Plotly figure and config.
    """
    categories = []
    deltas = []
    hover_text = []
    lower_is_better_stats = {
        "goals_conceded",
        "xgoals_gk_faced",
        "goals_minus_xgoals_gk",
        "goals_divided_by_xgoals_gk"
        }

    for stat in stats_to_plot:
        val = player_data[stat]
        avg = player_data[f'avg_{stat}']
        min_val = player_data[f'min_{stat}']
        max_val = player_data[f'max_{stat}']

        if max_val == min_val:
            continue

        # Normalize values
        val_norm = (val - min_val) / (max_val - min_val)
        avg_norm = (avg - min_val) / (max_val - min_val)

        # Invert for "lower is better"
        if stat in lower_is_better_stats:
            val_norm = 1 - val_norm
            avg_norm = 1 - avg_norm

        delta = val_norm - avg_norm

        stat_label = stat.replace('_', ' ').title()

        categories.append(stat_label + "  ")
        deltas.append(delta)
        hover_text.append(f"{stat_label}: {val:.2f} (avg {avg:.2f})")

    fig = go.Figure(go.Bar(
        x=deltas,
        y=categories,
        orientation='h',
        marker_color=['#003049' if d >= 0 else '#c1121f' for d in deltas],
        textposition='auto',
        hovertext=hover_text,
        hoverinfo='text'
    ))

    fig.update_layout(
        xaxis=dict(
            zeroline=True,
            zerolinewidth=2,
            zerolinecolor='gray',
            showticklabels=False
        ),
        yaxis=dict(autorange='reversed'),
        height=40 * len(stats_to_plot) + 100,
        width=1000,
        margin=dict(l=120, r=60, t=60, b=40),
        showlegend=False
    )

    fig_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    config = json.dumps({
        "displayModeBar": False,
        "staticPlot": True
    })

    return fig_json, config

