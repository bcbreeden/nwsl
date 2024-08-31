from api import make_asa_api_call
import sqlite3

def insert_all_games_xgoals_by_season(season):
    print('Inserting games by season for:', season)
    api_string = 'nwsl/games/xgoals?season_name={}'.format(str(season))
    games_data = make_asa_api_call(api_string)[1]
    conn = sqlite3.connect('db/nwsl.db')
    cursor = conn.cursor()
    for game in games_data:
        game_id = game.get('game_id', 'Unknown Game ID')
        date_time_utc = game.get('date_time_utc', 'Unknown Date/Time')
        home_team_id = game.get('home_team_id', 'Unknown Home Team ID')
        home_goals = game.get('home_goals', 0)
        home_team_xgoals = game.get('home_team_xgoals', 0.0)
        home_player_xgoals = game.get('home_player_xgoals', 0.0)
        away_team_id = game.get('away_team_id', 'Unknown Away Team ID')
        away_goals = game.get('away_goals', 0)
        away_team_xgoals = game.get('away_team_xgoals', 0.0)
        away_player_xgoals = game.get('away_player_xgoals', 0.0)
        goal_difference = game.get('goal_difference', 0)
        team_xgoal_difference = game.get('team_xgoal_difference', 0.0)
        player_xgoal_difference = game.get('player_xgoal_difference', 0.0)
        final_score_difference = game.get('final_score_difference', 0)
        home_xpoints = game.get('home_xpoints', 0.0)
        away_xpoints = game.get('away_xpoints', 0.0)
    
        cursor.execute('''
        INSERT OR REPLACE INTO games_xgoals (
            game_id, date_time_utc, home_team_id, home_goals, home_team_xgoals,
            home_player_xgoals, away_team_id, away_goals, away_team_xgoals,
            away_player_xgoals, goal_difference, team_xgoal_difference,
            player_xgoal_difference, final_score_difference, home_xpoints, away_xpoints, season
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            game_id, date_time_utc, home_team_id, home_goals, home_team_xgoals,
            home_player_xgoals, away_team_id, away_goals, away_team_xgoals,
            away_player_xgoals, goal_difference, team_xgoal_difference,
            player_xgoal_difference, final_score_difference, home_xpoints, away_xpoints, int(season)
        ))
        conn.commit()
    cursor.close()
    conn.close()

def get_all_games_xgoals_by_season(season):
    print('Fetching games xgoals for: {}'.format(season))
    conn = sqlite3.connect('db/nwsl.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM games_xgoals WHERE season = ?', (season,))
    rows = cursor.fetchall()
    conn.commit()
    conn.close()
    print('Games xgoals returned.')
    return rows