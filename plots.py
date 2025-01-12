import plotly.graph_objects as go
from data import (db_games_xgoals, db_games, db_goalkeeper_goals_added,db_goalkeeper_xgoals,
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

def plot_team_points_diff():
    rows = db_team_xgoals.get_top_team_xgoals_stat(2024, 'point_diff')
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

def plot_goal_vs_xgoal():
    rows = db_team_xgoals.get_top_team_xgoals_stat(2024, 'goalfor_xgoalfor_diff')
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