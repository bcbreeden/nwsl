import plotly.graph_objects as go
from db import (db_games_xgoals, db_games, db_goalkeeper_goals_added,db_goalkeeper_xgoals,
                db_player_goals_added, db_player_info, db_player_xgoals, db_player_xpass,
                db_setup, db_team_goals_added, db_team_info, db_team_xgoals, db_team_xpass)

def plot_team_goals_points():
    rows = db_team_xgoals.get_top_team_xgoals_stat(2024, 'points')

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
                                        size=goals_data,
                                        sizemode='diameter',
                                        sizeref=max(goals_data)/85, 
                                        sizemin=5 ,
                                        color=goals_data,
                                        colorscale='sunsetdark'
                                    ),
                                    line=dict(width=3, 
                                        color='darkviolet')
                                    ))

    # Customize the layout
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