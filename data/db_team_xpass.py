from api import make_asa_api_call
from .data_util import get_db_path
import sqlite3

def insert_teams_xpass_by_season(season):
    print('Inserting teams data (xpasses) for season:', season)
    api_string = 'nwsl/teams/xpass?season_name={}&stage_name=Regular Season'.format(str(season))
    teams_data = make_asa_api_call(api_string)[1]
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    for team in teams_data:
        team_id = team.get('team_id', 'Unknown Team ID')
        obj_id = team_id + str(season)
        count_games = team.get('count_games', 0)
        attempted_passes_for = team.get('attempted_passes_for', 0)
        pass_completion_percentage_for = team.get('pass_completion_percentage_for', 0.0)
        xpass_completion_percentage_for = team.get('xpass_completion_percentage_for', 0.0)
        passes_completed_over_expected_for = team.get('passes_completed_over_expected_for', 0.0)
        passes_completed_over_expected_p100_for = team.get('passes_completed_over_expected_p100_for', 0.0)
        avg_vertical_distance_for = team.get('avg_vertical_distance_for', 0.0)
        attempted_passes_against = team.get('attempted_passes_against', 0)
        pass_completion_percentage_against = team.get('pass_completion_percentage_against', 0.0)
        xpass_completion_percentage_against = team.get('xpass_completion_percentage_against', 0.0)
        passes_completed_over_expected_against = team.get('passes_completed_over_expected_against', 0.0)
        passes_completed_over_expected_p100_against = team.get('passes_completed_over_expected_p100_against', 0.0)
        avg_vertical_distance_against = team.get('avg_vertical_distance_against', 0.0)
        passes_completed_over_expected_difference = team.get('passes_completed_over_expected_difference', 0.0)
        avg_vertical_distance_difference = team.get('avg_vertical_distance_difference', 0.0)

        cursor.execute('''
            INSERT OR REPLACE INTO team_xpass (
                id, team_id, count_games, attempted_passes_for, pass_completion_percentage_for, 
                xpass_completion_percentage_for, passes_completed_over_expected_for, 
                passes_completed_over_expected_p100_for, avg_vertical_distance_for, 
                attempted_passes_against, pass_completion_percentage_against, 
                xpass_completion_percentage_against, passes_completed_over_expected_against, 
                passes_completed_over_expected_p100_against, avg_vertical_distance_against, 
                passes_completed_over_expected_difference, avg_vertical_distance_difference,
                season
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            obj_id, team_id, count_games,attempted_passes_for,
            round((pass_completion_percentage_for * 100), 1),
            round((xpass_completion_percentage_for * 100), 1),
            round(passes_completed_over_expected_for, 1),
            round(passes_completed_over_expected_p100_for, 1),
            round(avg_vertical_distance_for, 1),
            attempted_passes_against,
            round((pass_completion_percentage_against * 100), 1),
            round((xpass_completion_percentage_against * 100), 1),
            round(passes_completed_over_expected_against, 1),
            round(passes_completed_over_expected_p100_against, 1),
            round(avg_vertical_distance_against, 1),
            round(passes_completed_over_expected_difference, 1),
            round(avg_vertical_distance_difference, 1),
            int(season)
        ))

        conn.commit()
    conn.close()

def get_team_xpass_by_season(team_id, season):
    print('Fetching team xpasses for:{}, Season: {}'.format(team_id, season))
    obj_id = team_id + str(season)
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    query = f'''
        SELECT 
            txp.*,
            ti.*
        FROM 
            team_xpass AS txp
        JOIN 
            team_info AS ti
        ON 
            txp.team_id = ti.team_id
        WHERE
            txp.id = ?;
    '''
    cursor.execute(query, (obj_id,))
    row = cursor.fetchone()
    conn.commit()
    conn.close()
    print('Team xpasses returned.')
    return row

def get_all_teams_xpass_by_season(season):
    print(f'Attempting to get all teams xpass data from data base, season: {season}.')
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    query = f'''
        SELECT 
            tx.*,
            ti.*
        FROM 
            team_xpass AS tx
        JOIN 
            team_info AS ti
        ON 
            tx.team_id = ti.team_id
        WHERE
            tx.season = ?;
    '''
    cursor.execute(query, (season,))
    rows = cursor.fetchall()
    conn.commit()
    conn.close()
    print(f'All teams xpass data fetched from db for season: {season}')
    return rows
