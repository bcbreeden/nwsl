from flask import Flask, render_template
from db import (db_games_xgoals, db_games, db_goalkeeper_goals_added,db_goalkeeper_xgoals,
                db_player_goals_added, db_player_info, db_player_xgoals, db_player_xpass,
                db_setup, db_team_goals_added, db_team_info, db_team_xgoals, db_team_xpass)
app = Flask(__name__)
app.config["DEBUG"] = True

'''
Renders the index template.
'''
@app.route('/')
def index():
    team_data = db_team_xgoals.get_all_teams_xgoals_by_season(2024)
    top_5_goalscorers = db_player_xgoals.get_top_player_xgoals(2024, 'goals', 5)
    top_5_assists = db_player_xgoals.get_top_player_xgoals(2024, 'primary_assists', 5)
    return render_template('index.html',
                           teams = team_data,
                           top_scorers = top_5_goalscorers,
                           top_assists = top_5_assists)

@app.route('/teams')
def teams():
    team_data = db_team_xgoals.get_all_teams_xgoals_by_season(2024)
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
