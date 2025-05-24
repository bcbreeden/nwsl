import sqlite3
from .data_util import get_db_path

def insert_team_strength(xgd_contrib, gd_contrib, xp_contrib, p_contrib, gdmxgd_contrib, gfdiff_contrib, season, team_id):
    print('Attempting to insert team strength...')
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO team_strength (
            team_id,
            season,
            xgoal_difference,
            goal_difference,
            xpoints,
            points,
            goal_diff_minus_xgoal_diff,
            goalfor_xgoalfor_diff
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        team_id,
        season,
        round((xgd_contrib * 100), 1),
        round((gd_contrib * 100), 1),
        round((xp_contrib * 100), 1),
        round((p_contrib * 100), 1),
        round((gdmxgd_contrib * 100), 1),
        round((gfdiff_contrib * 100), 1)
    ))

    conn.commit()
    conn.close()
    print(f'Team strength updated for {team_id} for the {season} season.')

def get_team_strength(team_id, season):
    print(f'Fetching team strength for {team_id} in {season}...')
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    query = '''
        SELECT *
        FROM team_strength
        WHERE team_id = ? AND season = ?
    '''
    cursor.execute(query, (team_id, season))
    row = cursor.fetchone()

    conn.close()
    return row 
