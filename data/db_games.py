from api import make_asa_api_call
import sqlite3

def insert_all_games_by_season(season):
    print('Inserting games by season for:', season)
    api_string = 'nwsl/games?season_name={}&stage_name=Regular Season'.format(str(season))
    games_data = make_asa_api_call(api_string)[1]
    conn = sqlite3.connect('data/nwsl.db')
    cursor = conn.cursor()
    for game in games_data:
        game_id = game.get('game_id', 'Unknown Game ID')
        date_time_utc = game.get('date_time_utc', 'Unknown Date/Time')
        home_score = game.get('home_score', 0)
        away_score = game.get('away_score', 0)
        home_team_id = game.get('home_team_id', 'Unknown Home Team ID')
        away_team_id = game.get('away_team_id', 'Unknown Away Team ID')
        referee_id = game.get('referee_id', 'Unknown Referee ID')
        stadium_id = game.get('stadium_id', 'Unknown Stadium ID')
        home_manager_id = game.get('home_manager_id', 'Unknown Home Manager ID')
        away_manager_id = game.get('away_manager_id', 'Unknown Away Manager ID')
        expanded_minutes = game.get('expanded_minutes', 0)
        season_name = game.get('season_name', 'Unknown Season')
        matchday = game.get('matchday', 0)
        attendance = game.get('attendance', 0)
        knockout_game = game.get('knockout_game', False)
        last_updated_utc = game.get('last_updated_utc', 'Unknown Last Updated Time')

        cursor.execute('''
        INSERT OR REPLACE INTO games (
            game_id, date_time_utc, home_score, away_score, 
            home_team_id, away_team_id, referee_id, stadium_id, 
            home_manager_id, away_manager_id, expanded_minutes, 
            season_name, matchday, attendance, knockout_game, 
            last_updated_utc, season
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            game_id, date_time_utc, home_score, away_score, 
            home_team_id, away_team_id, referee_id, stadium_id, 
            home_manager_id, away_manager_id, expanded_minutes, 
            season_name, matchday, attendance, knockout_game, 
            last_updated_utc, int(season)
        ))
        conn.commit()
    cursor.close()
    conn.close()

def get_all_games_by_season(season):
    print('Fetching games for: {}'.format(season))
    conn = sqlite3.connect('data/nwsl.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM games WHERE season = ?', (season,))
    rows = cursor.fetchall()
    # for row in rows:
    #     print(dict(row))
    conn.commit()
    conn.close()
    print('Games returned.')
    return rows