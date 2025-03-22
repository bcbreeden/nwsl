import plotly.graph_objects as go
from data import (db_games_xgoals, db_games, db_goalkeeper_goals_added,db_goalkeeper_xgoals,
                db_player_goals_added, db_player_info, db_player_xgoals, db_player_xpass,
                db_setup, db_team_goals_added, db_team_info, db_team_xgoals, db_team_xpass)
import plotly
import json

def plot_team_goals_points(season):
    rows = db_team_xgoals.get_top_team_xgoals_stat(season, 'points')

    goals_data = [row['goals_for'] for row in rows]
    points_data = [row['points'] for row in rows]
    team_labels = [row['team_name'] for row in rows]
    team_abbr = [row['team_abbreviation'] for row in rows]
    hover_text = [f'{label}<br>Points: {x}<br>Goals: {y}' for label, x, y in zip(team_labels, points_data, goals_data)]

    fig = go.Figure(data=go.Scatter(x=points_data,
                                    y=goals_data,
                                    mode='markers+text', 
                                    text=team_abbr,
                                    textposition="top center",
                                    hovertext=hover_text,
                                    hoverinfo='text',
                                    marker=dict(
                                        size=points_data,
                                        sizemode='diameter',
                                        sizeref=max(points_data)/85, 
                                        sizemin=5 ,
                                        color=points_data,
                                        colorscale=[
                                            [0, '#c1121f'],
                                            [1, '#003049']
                                        ],
                                        cmin=min(points_data),
                                        cmax=max(points_data)
                                    ),
                                    ))
    fig.update_layout(
        title='Goals/Points for NWSL Teams',
        xaxis_title='Points',
        yaxis_title='Goals For',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=40, b=0),
        width=1600,
        height=800
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=False)

    return fig

def plot_team_points_diff(season):
    rows = db_team_xgoals.get_top_team_xgoals_stat(season, 'point_diff')
    point_diff_data = [row['point_diff'] for row in rows]
    team_labels = [row['team_name'] for row in rows]
    team_abbr = [row['team_abbreviation'] for row in rows]
    hover_text = [f'{label}<br>Point_Diff: {x}' for label, x in zip(team_labels, point_diff_data)]
    fig = go.Figure(
            data=[
                go.Bar(
                        x=team_abbr,
                        y=point_diff_data,
                        text=team_abbr,
                        hovertext=hover_text,
                        hoverinfo='text',
                        marker=dict(
                            color=point_diff_data,
                            colorscale=[
                                    [0, '#c1121f'],
                                    [1, '#003049']
                        ],
                        cmin=min(point_diff_data),
                        cmax=max(point_diff_data)
                    )
                )
            ]
        )
    fig.update_layout(
        title='Point Difference for NWSL Teams',
        yaxis_title='Point Diff',
        xaxis=dict(showticklabels=False),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=40, b=0),
        width=1600,
        height=800
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=False)
    return fig

def plot_goal_vs_xgoal(season):
    rows = db_team_xgoals.get_top_team_xgoals_stat(season, 'goalfor_xgoalfor_diff')
    goals_for = [row['goals_for'] for row in rows]
    xgoals_for = [row['xgoals_for'] for row in rows]
    goals_xgoals_for_diff = [row['goalfor_xgoalfor_diff'] for row in rows]
    team_labels = [row['team_name'] for row in rows]
    team_abbr = [row['team_abbreviation'] for row in rows]

    fig = go.Figure()

    # Add the line connecting the two values
    for i in range(len(team_labels)):
        fig.add_trace(go.Scatter(
            x=[goals_for[i], xgoals_for[i]],
            y=[team_abbr[i], team_abbr[i]],
            mode='lines',
            line=dict(color='black', width=5),
            showlegend=False
        ))

    # Add the points for the actual goals
    fig.add_trace(go.Scatter(
        x=goals_for, y=team_abbr, 
        mode='markers',
        marker=dict(color='#003049', size=25),
        name='Goals'
    ))

    # Add the points for the expected goals
    fig.add_trace(go.Scatter(
        x=xgoals_for, y=team_abbr, 
        mode='markers',
        marker=dict(color='#c1121f', size=25),
        name='Expected Goals'
    ))

    fig.update_layout(
        title="Goals vs Expected Goals",
        xaxis_title="Number of Goals",
        showlegend=True,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=40, b=0),
        width=1600,
        height=800
    )
    return fig

import plotly.graph_objects as go

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

