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
    return render_template('index.html')

@app.route('/teams')
def teams():
    team_info_data = db_team_info.get_all_teams_info()
    return render_template('teams.html',
                           teams = team_info_data)

@app.route('/games')
def games():
    return render_template('games.html')

@app.route('/players')
def players():
    return render_template('players.html')

if __name__ == '__main__':
    app.run(debug=True)
