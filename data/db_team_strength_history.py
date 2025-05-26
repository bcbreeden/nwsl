import sqlite3
from .data_util import get_db_path

def get_team_strength_history_by_season(season):
    print('Attempting to get team strength history with team info for season:', season)
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute('''
        SELECT team_strength_history.*, team_info.*
        FROM team_strength_history
        JOIN team_info ON team_strength_history.team_id = team_info.team_id
        WHERE season = ?
        ORDER BY count_games, team_rank
    ''', (season,))
    
    rows = cursor.fetchall()
    conn.close()

    if rows:
        print(f'{len(rows)} row(s) successfully retrieved for season:', season)
    else:
        print('No data found for season:', season)

    return rows
