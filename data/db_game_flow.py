from api import make_asa_api_call
import sqlite3
from datetime import datetime
import pytz

def insert_flow_by_game_id(game_id):
    print('Inserting game flow for game ID:', game_id)
    api_string = 'nwsl/games/game-flow?game_id={}'.format(str(game_id))
    game_flow_data = make_asa_api_call(api_string)[1]
    conn = sqlite3.connect('data/nwsl.db')
    cursor = conn.cursor()
    for flow in game_flow_data:
        game_id = flow.get('game_id', 'Unknown Game ID')
        period_id = flow.get('period_id', 0)
        expanded_minute = flow.get('expanded_minute', 0)
        home_team_id = flow.get('home_team_id', 'Unknown Home Team ID')
        home_team_value = flow.get('home_team_value', 0.0)
        away_team_id = flow.get('away_team_id', 'Unknown Away Team ID')
        away_team_value = flow.get('away_team_value', 0.0)

        cursor.execute('''
        INSERT OR REPLACE INTO game_flow (
            game_id, period_id, expanded_minute, 
            home_team_id, home_team_value, 
            away_team_id, away_team_value
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            game_id, period_id, expanded_minute, 
            home_team_id, home_team_value, 
            away_team_id, away_team_value
        ))
        conn.commit()
    cursor.close()
    conn.close()

def get_game_flow_by_game_id(game_id):
    print('Fetching game flow for game ID:', game_id)
    conn = sqlite3.connect('data/nwsl.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    query = '''
        SELECT * FROM game_flow WHERE game_id = ?
    '''
    cursor.execute(query, (game_id,))
    rows = cursor.fetchall()
    conn.commit()
    cursor.close()
    print('Game flow fetched for game ID:', game_id)
    return rows


# PLOT STUFF, MOVE
import plotly.graph_objects as go
def plot_game_flow(game_id):
    conn = sqlite3.connect('data/nwsl.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM game_flow WHERE game_id = ? ORDER BY expanded_minute", (game_id,))
    rows = cursor.fetchall()

    # Extract data
    minutes = []
    home_values = []
    away_values = []
    home_team = None
    away_team = None

    for row in rows:
        minutes.append(row['expanded_minute'])
        home_values.append(row['home_team_value'])
        away_values.append(row['away_team_value'])
        home_team = row['home_team_id']
        away_team = row['away_team_id']

    home_values_smoothed = moving_average(home_values, window_size=5)
    away_values_smoothed = moving_average(away_values, window_size=5)

    halftime_minute = None
    for row in rows:
        if row['period_id'] == 2:
            halftime_minute = row['expanded_minute']
            break

    # Create figure
    fig = go.Figure()

    # Home team line
    fig.add_trace(go.Scatter(
        x=minutes,
        y=home_values_smoothed,
        mode='lines',
        name=f'Home ({home_team})',
        line_shape='spline',
        fill='tozeroy'
    ))

    # Away team line
    fig.add_trace(go.Scatter(
        x=minutes,
        y=away_values_smoothed,
        mode='lines',
        name=f'Away ({away_team})',
        line_shape='spline',
        fill='tozeroy'
    ))

    shapes = []
    annotations = []

    # Add halftime line and annotation
    if halftime_minute is not None:
        shapes.append(dict(
            type='line',
            x0=halftime_minute,
            x1=halftime_minute,
            y0=0,
            y1=1,
            xref='x',
            yref='paper',
            line=dict(
                color='black',
                width=2,
                dash='dash'
            )
        ))

        annotations.append(dict(
            x=halftime_minute,
            y=1,
            xref='x',
            yref='paper',
            text='Halftime',
            showarrow=False,
            font=dict(color='black'),
            xanchor='left',
            yanchor='bottom'
        ))

    
    # Full-time line at minute 90
    shapes.append(dict(
        type='line',
        x0=90,
        x1=90,
        y0=0,
        y1=1,
        xref='x',
        yref='paper',
        line=dict(
            color='black',
            width=2,
            dash='dash'
        )
    ))

    annotations.append(dict(
        x=90,
        y=1,
        xref='x',
        yref='paper',
        text='Full Time',
        showarrow=False,
        font=dict(color='black'),
        xanchor='left',
        yanchor='bottom'
    ))

    # Customize layout
    fig.update_layout(
        title=f"Game Flow for Game ID: {game_id}",
        xaxis_title="Minute",
        yaxis_title="Momentum Value",
        hovermode="x unified",
        template="plotly_white",
        shapes=shapes
    )

    for annotation in annotations:
        fig.add_annotation(**annotation)
        fig.show()
    
    return fig

def plot_net_game_flow(game_id):
    conn = sqlite3.connect('data/nwsl.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM game_flow WHERE game_id = ? ORDER BY expanded_minute", (game_id,))
    rows = cursor.fetchall()

    minutes = []
    net_values = []
    halftime_minute = None

    for row in rows:
        minute = row['expanded_minute']
        home = row['home_team_value']
        away = row['away_team_value']
        net = home - away

        minutes.append(minute)
        net_values.append(net)

        if halftime_minute is None and row['period_id'] == 2:
            halftime_minute = minute

    fig = go.Figure()

    # Plot net momentum wave
    fig.add_trace(go.Scatter(
        x=minutes,
        y=net_values,
        mode='lines',
        name='Net Momentum (Home - Away)',
        line_shape='spline',
        fill='tozeroy',
        fillcolor='rgba(0, 100, 255, 0.2)',
        line=dict(color='blue')
    ))

    # Add zero baseline
    fig.add_trace(go.Scatter(
        x=[min(minutes), max(minutes)],
        y=[0, 0],
        mode='lines',
        line=dict(color='black', dash='dash'),
        showlegend=False
    ))

    # Add halftime line
    shapes = []
    annotations = []

    if halftime_minute:
        shapes.append(dict(
            type='line',
            x0=halftime_minute,
            x1=halftime_minute,
            y0=0,
            y1=1,
            xref='x',
            yref='paper',
            line=dict(color='gray', width=2, dash='dot')
        ))

        annotations.append(dict(
            x=halftime_minute,
            y=1,
            xref='x',
            yref='paper',
            text='Halftime',
            showarrow=False,
            font=dict(color='gray'),
            xanchor='left',
            yanchor='bottom'
        ))

    # Add full-time line at 90
    shapes.append(dict(
        type='line',
        x0=90,
        x1=90,
        y0=0,
        y1=1,
        xref='x',
        yref='paper',
        line=dict(color='black', width=2, dash='dash')
    ))

    annotations.append(dict(
        x=90,
        y=1,
        xref='x',
        yref='paper',
        text='Full Time',
        showarrow=False,
        font=dict(color='black'),
        xanchor='left',
        yanchor='bottom'
    ))

    fig.update_layout(
        title=f"Net Momentum for Game ID: {game_id}",
        xaxis_title="Minute",
        yaxis_title="Net Momentum (Home - Away)",
        hovermode="x unified",
        template="plotly_white",
        shapes=shapes
    )

    for annotation in annotations:
        fig.add_annotation(**annotation)

    fig.show()


def moving_average(data, window_size=3):
    return [
        sum(data[max(0, i - window_size + 1):i + 1]) / (i - max(0, i - window_size + 1) + 1)
        for i in range(len(data))
    ]

