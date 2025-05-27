import plotly.graph_objects as go
from data import (db_games, db_team_xgoals, db_game_shots)
import plotly
import json
import matplotlib.pyplot as plt

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

def plot_team_strength_donut(score):
    """
    Generates a donut chart with a discrete color based on team strength.
    """
    score = max(0, min(100, score))  # Clamp to [0, 100]
    fill_color = strength_to_color(score)

    fig = go.Figure(go.Pie(
        values=[score, 100 - score],
        hole=0.7,
        marker_colors=[fill_color, "#d3dbe3"],
        textinfo="none",
        sort=False,
        hoverinfo="skip",
        hovertemplate=None
    ))

    fig.update_layout(
        showlegend=False,
        margin=dict(t=0, b=0, l=0, r=0),
        annotations=[
            dict(
                text=f"<b>{score}</b><br><span style='font-size:14px;'>TEAM STRENGTH</span>", 
                x=0.5, y=0.5, font_size=24, showarrow=False, align='center'
            )
        ],
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=250,
        width=250
    )

    fig_json = fig.to_json()
    config = {'displayModeBar': False}
    return fig_json, config

def strength_to_color(score):
    """
    Maps strength score to one of three discrete colors.
    """
    if score <= 33:
        return "#c1121f"  # Red
    elif score <= 66:
        return "#f4a261"  # Amber
    else:
        return "#003049"  # Navy

import plotly.graph_objects as go

def get_donut_plot_for_team_results(wins, losses, draws, points):
    labels = ['Wins', 'Losses', 'Draws']
    values = [wins, losses, draws]
    colors = ['#003049', '#c1121f', '#d3dbe3']

    fig = go.Figure(go.Pie(
        labels=labels,
        values=values,
        hole=0.6,
        marker=dict(colors=colors),
        textinfo='none',
        sort=False,
        hoverinfo='skip'  # Disable all hover text
    ))

    fig.update_layout(
        showlegend=False,
        margin=dict(t=0, b=0, l=0, r=0),
        annotations=[
            dict(
                text=f"<b>{points}</b><br><span style='font-size:12px;'>POINTS</span>",
                x=0.5, y=0.5,
                font_size=22,
                showarrow=False,
                align='center'
            )
        ],
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=250,
        width=250
    )
    fig_json = fig.to_json()
    config = {'displayModeBar': False}

    return fig_json, config


def get_donut_plot_for_goals(goals_for, goals_against):
    labels = ['Goals For', 'Goals Against']
    values = [goals_for, goals_against]
    colors = ['#003049', '#c1121f']

    fig = go.Figure(go.Pie(
        labels=labels,
        values=values,
        hole=0.6,
        marker=dict(colors=colors),
        textinfo='none',
        sort=False,
        hoverinfo='skip'
    ))

    fig.update_layout(
        showlegend=False,
        margin=dict(t=0, b=0, l=0, r=0),
        annotations=[
            dict(
                text=f"<b>{goals_for}-{goals_against}</b><br><span style='font-size:12px;'>GOALS</span>",
                x=0.5, y=0.5,
                font_size=20,
                showarrow=False,
                align='center'
            )
        ],
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=250,
        width=250
    )

    fig_json = fig.to_json()
    config = {'displayModeBar': False}

    return fig_json, config

def get_donut_plot_for_pass_completion(percentage):
    percentage = max(0, min(100, percentage))  # Clamp between 0 and 100
    incomplete = 100 - percentage

    labels = ['Completed', 'Incomplete']
    values = [percentage, incomplete]
    colors = ['#003049', '#d3dbe3']  # Blue for completed, gray for incomplete

    fig = go.Figure(go.Pie(
        labels=labels,
        values=values,
        hole=0.6,
        marker=dict(colors=colors),
        textinfo='none',
        sort=False,
        hoverinfo='skip'
    ))

    fig.update_layout(
        showlegend=False,
        margin=dict(t=0, b=0, l=0, r=0),
        annotations=[
            dict(
                text=f"<b>{percentage}%</b><br><span style='font-size:12px;'>PASS</span>",
                x=0.5, y=0.5,
                font_size=20,
                showarrow=False,
                align='center'
            )
        ],
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=250,
        width=250
    )

    fig_json = fig.to_json()
    config = {'displayModeBar': False}

    return fig_json, config

def plot_bar_chart(stats_to_plot, team_data, title="Team Strength Breakdown"):
    """
    Generates a bar chart for a single team's strength-related stats.

    Args:
        team_data (sqlite3.Row or dict): Row returned by get_team_strength().
        stats_to_plot (list of str): List of stat field names to plot (e.g. ['xgoal_difference', 'points']).
        title (str): Chart title.

    Returns:
        Tuple[str, str]: JSON-encoded Plotly figure and config.
    """
    categories = []
    values = []
    bar_labels = []

    for stat in stats_to_plot:
        if stat in team_data.keys():
            val = team_data[stat]
            label = stat.replace('_', ' ').title()
            categories.append(label + "  ")
            values.append(val)
            bar_labels.append(f"{val:.2f}")

    fig = go.Figure(go.Bar(
        x=values,
        y=categories,
        orientation='h',
        marker_color='#003049',
        text=bar_labels,
        textposition='inside',
        hoverinfo='skip'
    ))

    fig.update_layout(
        title=dict(
            text=f"<b>{title}</b>",
            font=dict(
                family="Montserrat, Arial, sans-serif",
                size=27,
                color="#003049"
            ),
            x=0.5,
            xanchor="center"
        ),
        xaxis=dict(
            showline=False,
            showticklabels=False
        ),
        yaxis=dict(autorange='reversed'),
        height=40 * len(categories) + 100,
        width=1000,
        margin=dict(l=120, r=60, t=60, b=40),
        showlegend=False
    )

    fig_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    config = {
        "displayModeBar": False,
        "staticPlot": True
        }

    return fig_json, config

def add_soccer_pitch(fig):
    line_color = "white"
    line_width = 2

    pitch_shapes = [
        # Outer box (half-pitch)
        dict(type="rect", x0=50, y0=0, x1=100, y1=100, line=dict(color=line_color, width=line_width)),

        # Midfield line
        dict(type="line", x0=50, y0=0, x1=50, y1=100, line=dict(color=line_color, width=line_width)),

        # Center circle (right half only)
        # dict(type="circle", x0=50 - 9.15, y0=50 - 9.15, x1=50 + 9.15, y1=50 + 9.15, line=dict(color=line_color, width=line_width)),

        # Penalty box
        dict(type="rect", x0=83, y0=21.1, x1=100, y1=78.9, line=dict(color=line_color, width=line_width)),

        # 6-yard box
        dict(type="rect", x0=94.5, y0=36.8, x1=100, y1=63.2, line=dict(color=line_color, width=line_width)),

        # Goal line (goal mouth)
        dict(type="line", x0=100, y0=44.5, x1=100, y1=55.5, line=dict(color=line_color, width=line_width)),
    ]

    fig.update_layout(shapes=pitch_shapes)
    return fig


def generate_shot_marker_plot(game_id, game_data):
    shot_data = db_game_shots.get_shot_locations_by_game_id(game_id)
    if not shot_data:
        return None, None

    home_id = game_data["home_team_id"]
    away_id = game_data["away_team_id"]

    team_colors = {
        home_id: "blue",
        away_id: "orange"
    }

    fig = go.Figure()

    # Plot team-colored markers
    for team_id in [home_id, away_id]:
        team_shots = [s for s in shot_data if s['team_id'] == team_id]
        x = [s['x'] for s in team_shots]
        y = [s['y'] for s in team_shots]
        goals = [s['goal'] for s in team_shots]

        colors = ['red' if goal else team_colors[team_id] for goal in goals]

        fig.add_trace(go.Scatter(
            x=x,
            y=y,
            mode='markers',
            marker=dict(
                size=8,
                color=colors,
                line=dict(width=1, color='black')
            ),
            name=f"{'Home' if team_id == home_id else 'Away'} Shots"
        ))

    # Pitch layout
    fig.update_layout(
        title=f"Shot Map — Game {game_id}",
        xaxis=dict(range=[50, 101], showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(range=[0, 100], showgrid=False, zeroline=False, showticklabels=False),
        height=600,
        width=900,
        paper_bgcolor='#007f00',
        plot_bgcolor='#007f00',
        margin=dict(t=40, b=40, l=40, r=40)
    )
    fig.update_yaxes(scaleanchor="x", scaleratio=0.5)

    fig = add_soccer_pitch(fig)

    config = {
        'displayModeBar': False,
        'responsive': True
    }

    return fig.to_json(), config