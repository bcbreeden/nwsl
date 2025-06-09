from api import make_asa_api_call
from .data_util import get_db_path
import sqlite3

def insert_team_info():
    print('Attempting  to insert all teams info...')
    teams_data = make_asa_api_call('nwsl/teams')[1]
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    for team in teams_data:
        team_id = team.get('team_id', 'Unknown ID')
        team_name = team.get('team_name', 'Unknown Name')
        team_short_name = team.get('team_short_name', 'Unknown Short Name')
        team_abbreviation = team.get('team_abbreviation', 'Unknown Abbreviation')

        cursor.execute('''
        INSERT OR REPLACE INTO team_info (
            team_id, team_name, team_short_name, team_abbreviation
        ) VALUES (?, ?, ?, ?)
        ''', (
            team_id, team_name, team_short_name, team_abbreviation
        ))

        conn.commit()
    conn.close()
    print('All teams info successfully entered into the database.')

def get_all_teams_info():
    print('Fetching all teams info from the database...')
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM team_info')
    rows = cursor.fetchall()
    conn.commit()
    conn.close()
    print('All teams info returned.')
    return rows

def get_team_info_by_id(team_id):
    print('Fetching team information for team id:', team_id)
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM team_info WHERE team_id = ?', (team_id,))
    row = cursor.fetchone()
    conn.commit()
    conn.close()
    print('Team info returned.')
    return row

def get_team_name_map():
    """
    Returns a dictionary mapping team_id → team_name from team_info table.
    """
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute('SELECT team_id, team_name FROM team_info')
    rows = cursor.fetchall()
    conn.close()

    return {row['team_id']: row['team_name'] for row in rows}