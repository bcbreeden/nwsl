from api import make_asa_api_call
from .data_util import get_db_path
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
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    query = '''
        SELECT 
            gf.*,
            home_team.team_abbreviation AS home_abbreviation,
            home_team.team_name AS home_team_name,
            away_team.team_abbreviation AS away_abbreviation,
            away_team.team_name AS away_team_name
        FROM
            game_flow AS gf
        JOIN
            team_info AS home_team 
        ON
            gf.home_team_id = home_team.team_id
        JOIN 
            team_info AS away_team 
        ON 
            gf.away_team_id = away_team.team_id
        WHERE gf.game_id = ?
        ORDER BY gf.expanded_minute
    '''
    cursor.execute(query, (game_id,))
    rows = cursor.fetchall()
    conn.commit()
    cursor.close()
    print('Game flow fetched for game ID:', game_id)
    return rows
