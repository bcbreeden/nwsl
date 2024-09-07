from flask import Flask, render_template
from db import (db_games_xgoals, db_games, db_goalkeeper_goals_added,db_goalkeeper_xgoals,
                db_player_goals_added, db_player_info, db_player_xgoals, db_player_xpass,
                db_setup, db_team_goals_added, db_team_info, db_team_xgoals, db_team_xpass)
from plots import plot_team_goals_points
import plotly.graph_objects as go
import plotly.io as pio

app = Flask(__name__)
app.config["DEBUG"] = True

'''
Renders the index template.
'''
@app.route('/')
def index():
    team_points_data = db_team_xgoals.get_top_team_xgoals_stat(2024, 'points')
    top_5_goalscorers = db_player_xgoals.get_top_player_xgoals_stat(2024, 'goals', 5)
    top_5_assists = db_player_xgoals.get_top_player_xgoals_stat(2024, 'primary_assists', 5)
    shots_on_target = db_player_xgoals.player_xgoals_get_shots_on_target(2024, 'shots_on_target_perc', 5, 10)
    minutes_played_df = db_player_xgoals.player_xgoals_get_minutes_played_defender(2024, 'minutes_played', 5)
    minutes_played_non_df = db_player_xgoals.player_xgoals_get_minutes_played_non_df(2024, 'minutes_played', 5)
    plt_team_goals_points = plot_team_goals_points()
    plt_team_goals_points_html = pio.to_html(plt_team_goals_points, full_html=False)
    return render_template('index.html',
                           team_points_data = team_points_data,
                           top_scorers = top_5_goalscorers,
                           top_assists = top_5_assists,
                           shots_on_target = shots_on_target,
                           minutes_played_df = minutes_played_df,
                           minutes_played_non_df = minutes_played_non_df,
                           team_goal_point_plot = plt_team_goals_points_html)

@app.route('/teams')
def teams():
    team_data = db_team_xgoals.get_top_team_xgoals_stat(2024, 'points')
    return render_template('teams.html',
                           teams = team_data)

@app.route('/games')
def games():
    return render_template('games.html')

@app.route('/players')
def players():
    player_data = db_player_xgoals.get_all_player_xgoals(2024)
    return render_template('players.html',
                           players = player_data)

@app.route('/goalkeepers')
def goalkeepers():
    return render_template('goalkeepers.html')

if __name__ == '__main__':
    app.run(debug=True)
