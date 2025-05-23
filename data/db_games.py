from api import make_asa_api_call
from .data_util import get_db_path
import sqlite3
from datetime import datetime
import pytz

def insert_all_games_by_season(season):
    print('Inserting games by season for:', season)
    api_string = 'nwsl/games?season_name={}&stage_name=Regular Season'.format(str(season))
    games_data = make_asa_api_call(api_string)[1]
    conn = sqlite3.connect(get_db_path())
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
        status = game.get('status', 'Unknown Status')
        last_updated_utc = game.get('last_updated_utc', 'Unknown Last Updated Time')
        last_updated_est = _convert_utc_to_est(last_updated_utc)

        cursor.execute('''
        INSERT OR REPLACE INTO games (
            game_id, date_time_utc, date_time_est, home_score, away_score, 
            home_team_id, away_team_id, referee_id, stadium_id, 
            home_manager_id, away_manager_id, expanded_minutes, 
            season_name, matchday, attendance, knockout_game, status,
            last_updated_utc, last_updated_est, season
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            game_id, date_time_utc, date_time_est, home_score, away_score, 
            home_team_id, away_team_id, referee_id, stadium_id, 
            home_manager_id, away_manager_id, expanded_minutes, 
            season_name, matchday, attendance, knockout_game, status,
            last_updated_utc, last_updated_est, int(season)
        ))
        conn.commit()
    cursor.close()
    conn.close()

def get_all_games_by_season(season):
    print('Fetching games for: {}'.format(season))
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
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

    cursor.execute(query, (season,))
    rows = cursor.fetchall()
    conn.commit()
    conn.close()
    print('Games returned.')
    return rows

def get_game_by_id(game_id):
    print('Fetching game: {}'.format(game_id))
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
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
            gm.game_id = ?
    '''
    cursor.execute(query, (game_id,))
    row = cursor.fetchone()
    conn.commit()
    conn.close()
    print('Game returned.')
    return row

def get_game_ids_by_season(season):
    print('Fetching game IDs for: {}'.format(season))
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    query = '''
        SELECT
            gm.game_id
        FROM
            games AS gm
        WHERE
            gm.season = ?
    '''
    cursor.execute(query, (season,))
    rows = cursor.fetchall()
    game_ids = [row['game_id'] for row in rows]
    conn.commit()
    conn.close()
    return game_ids

def get_latest_manager_id_by_team_and_season(team_id, season):
    print(f'Fetching most recent manager for team: {team_id} in season: {season}')
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    query = '''
        SELECT
            CASE
                WHEN home_team_id = ? THEN home_manager_id
                ELSE away_manager_id
            END AS manager_id
        FROM games
        WHERE season = ?
          AND (home_team_id = ? OR away_team_id = ?)
        ORDER BY date_time_utc DESC
        LIMIT 1;
    '''
    
    cursor.execute(query, (team_id, season, team_id, team_id))
    result = cursor.fetchone()
    
    conn.close()
    
    return result[0] if result else None


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