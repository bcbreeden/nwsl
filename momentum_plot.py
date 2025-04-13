import plotly.graph_objects as go
from data import db_game_flow
import plotly
import json

def generate_momentum_plot(game_id):
    rows = db_game_flow.get_game_flow_by_game_id(game_id)

    minutes = []
    net_values = []
    shapes = []
    annotations = []
    halftime_minute = None

    # Logo Configuration
    home_abbr = rows[0]['home_abbreviation']
    away_abbr = rows[0]['away_abbreviation']
    home_logo_path = f"/static/img/{home_abbr}.png"
    away_logo_path = f"/static/img/{away_abbr}.png"
    images = [
        _make_logo_image(home_logo_path, x=0.05, y=0.92),
        _make_logo_image(away_logo_path, x=0.05, y=0.3)
    ]

    # Extract data from rows
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

    # Split net values into positive and negative traces
    positive_minutes, positive_values, negative_minutes,  negative_values = _split_positive_negative(minutes, net_values)

    # Add positive (home-dominant) momentum trace
    fig.add_trace(go.Scatter(
        x=positive_minutes,
        y=positive_values,
        mode='none',
        fill='tozeroy',
        line=dict(color='blue'),
        fillcolor='rgba(0, 100, 255, 0.5)',
        name='Home Momentum',
    ))

    # Add negative (away-dominant) momentum trace
    fig.add_trace(go.Scatter(
        x=negative_minutes,
        y=negative_values,
        mode='none',
        fill='tozeroy',
        line=dict(color='red'),
        fillcolor='rgba(255, 0, 0, 0.5)',
        name='Away Momentum',
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
    if halftime_minute:
        shapes.append(dict(
            type='line',
            x0=halftime_minute,
            x1=halftime_minute,
            y0=0,
            y1=1,
            xref='x',
            yref='paper',
            line=dict(color='black', width=2, dash='dash')
        ))
        annotations.append(_halftime_annotation(halftime_minute))

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
    annotations.append(_fulltime_annotation())

    fig.update_layout(
        title=f"Momentum Chart {home_abbr} vs {away_abbr}",
        xaxis_title="Minute",
        yaxis_title="Game Momentum",
        hovermode="x unified",
        template="plotly_white",
        shapes=shapes,
        images=images,
        showlegend=False,
        yaxis=dict(
            title="Game Momentum",
            range=[-.75, .75],
            tickvals=[],
            ticks='',
            showticklabels=False,
            showgrid=False,
            zeroline=False
        )
    )

    for annotation in annotations:
        fig.add_annotation(**annotation)

    fig_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    config = json.dumps({
        "displayModeBar": False,  # Disable the toolbar
        "scrollZoom": False,      # Disable zooming with the scroll wheel
        "dragMode": False,
        "staticPlot": True        # Make the plot fully static
    })

    return fig_json, config

def _make_logo_image(path, x, y, xanchor="left", yanchor="top"):
    return dict(
        source=path,
        xref="paper",
        yref="y domain",
        x=x,
        y=y,
        sizex=0.3,
        sizey=0.3,
        xanchor=xanchor,
        yanchor=yanchor,
        opacity=0.5,
        layer="below"
    )

def _split_positive_negative(x_vals, y_vals):
    pos_x, pos_y, neg_x, neg_y = [], [], [], []
    for x, y in zip(x_vals, y_vals):
        if y >= 0:
            pos_x.append(x)
            pos_y.append(y)
            neg_x.append(x)
            neg_y.append(None)
        else:
            pos_x.append(x)
            pos_y.append(None)
            neg_x.append(x)
            neg_y.append(y)
    return pos_x, pos_y, neg_x, neg_y

def _halftime_annotation(minute):
    return dict(
        x=minute,
        y=1,
        xref='x',
        yref='paper',
        text='Halftime',
        showarrow=False,
        font=dict(color='black'),
        xanchor='left',
        yanchor='bottom'
    )

def _fulltime_annotation():
    return dict(
        x=90,
        y=1,
        xref='x',
        yref='paper',
        text='Full Time',
        showarrow=False,
        font=dict(color='black'),
        xanchor='left',
        yanchor='bottom'
    )