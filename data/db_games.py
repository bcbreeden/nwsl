from api import make_asa_api_call
import sqlite3
from datetime import datetime
import pytz

def insert_all_games_by_season(season):
    print('Inserting games by season for:', season)
    api_string = 'nwsl/games?season_name={}&stage_name=Regular Season'.format(str(season))
    games_data = make_asa_api_call(api_string)[1]
    conn = sqlite3.connect('data/nwsl.db')
    cursor = conn.cursor()
    for game in games_data:
        game_id = game.get('game_id', 'Unknown Game ID')
        date_time_utc = game.get('date_time_utc', 'Unknown Date/Time')
        date_time_est = _convert_utc_to_est(date_time_utc)
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
        last_updated_est = _convert_utc_to_est(last_updated_utc)

        cursor.execute('''
        INSERT OR REPLACE INTO games (
            game_id, date_time_utc, date_time_est, home_score, away_score, 
            home_team_id, away_team_id, referee_id, stadium_id, 
            home_manager_id, away_manager_id, expanded_minutes, 
            season_name, matchday, attendance, knockout_game, 
            last_updated_utc, last_updated_est, season
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            game_id, date_time_utc, date_time_est, home_score, away_score, 
            home_team_id, away_team_id, referee_id, stadium_id, 
            home_manager_id, away_manager_id, expanded_minutes, 
            season_name, matchday, attendance, knockout_game, 
            last_updated_utc, last_updated_est, int(season)
        ))
        conn.commit()
    cursor.close()
    conn.close()

def get_all_games_by_season(season):
    print('Fetching games for: {}'.format(season))
    conn = sqlite3.connect('data/nwsl.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    query = '''
        SELECT
            gm.*,
            home_team.team_name AS home_team_name,
            home_team.team_short_name AS home_team_short_name,
            home_team.team_abbreviation AS home_team_abbreviation,
            away_team.team_name AS away_team_name,
            away_team.team_short_name AS away_team_short_name,
            away_team.team_abbreviation AS away_team_abbreviation
        FROM
            games AS gm
        JOIN
            team_info AS home_team
            ON gm.home_team_id = home_team.team_id
        JOIN
            team_info AS away_team
            ON gm.away_team_id = away_team.team_id
        WHERE
            gm.season = ?
    '''


    # cursor.execute('SELECT * FROM games WHERE season = ?', (season,))
    cursor.execute(query, (season,))
    rows = cursor.fetchall()
    # for row in rows:
    #     print(dict(row))
    conn.commit()
    conn.close()
    print('Games returned.')
    return rows

def _convert_utc_to_est(utc_str):
    if utc_str == 'Unknown Last Updated Time':
        return None

    # Parse string to datetime
    dt_utc = datetime.strptime(utc_str, "%Y-%m-%d %H:%M:%S %Z")
    # Set UTC timezone
    dt_utc = pytz.utc.localize(dt_utc)
    # Convert to US Eastern time
    dt_est = dt_utc.astimezone(pytz.timezone('US/Eastern'))

    formatted = dt_est.strftime("%A, %B %-d at %-I:%M %p")
    return formatted