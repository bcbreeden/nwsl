from api import make_asa_api_call
from .data_util import get_db_path
import sqlite3

def insert_team_goals_added_by_season(season):
    print('Inserting goals added by season (teams) for:', season)
    api_string = 'nwsl/teams/goals-added?season_name={}&stage_name=Regular Season'.format(str(season))
    teams_data = make_asa_api_call(api_string)[1]
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    for team in teams_data:
        team_id = team.get('team_id', 'Unknown Team ID')
        obj_id = team_id + str(season)
        minutes = team.get('minutes', 0)

        # Init default values for actions and action types
        action_types = ['Dribbling', 'Shooting', 'Passing', 'Interrupting', 'Receiving', 'Claiming', 'Fouling']
        actions = {
            action_type: {
                'num_actions_for': 0,
                'goals_added_for': 0,
                'num_actions_against': 0,
                'goals_added_against': 0
            } for action_type in action_types
        }

        # For each action type, fetch the corresponding action.
        for action in team.get('data', []):
            action_type = action.get('action_type')
            if action_type in actions:
                actions[action_type]['num_actions_for'] = action.get('num_actions_for', 0)
                actions[action_type]['goals_added_for'] = action.get('goals_added_for', 0)
                actions[action_type]['num_actions_against'] = action.get('num_actions_against', 0)
                actions[action_type]['goals_added_against'] = action.get('goals_added_against', 0)
            else:
                print(f"No action found for: {action_type}")

        cursor.execute('''
            INSERT OR REPLACE INTO team_goals_added (
                id, team_id, minutes, 
                dribbling_num_actions_for, dribbling_goals_added_for, dribbling_num_actions_against, dribbling_goals_added_against, 
                shooting_num_actions_for, shooting_goals_added_for, shooting_num_actions_against, shooting_goals_added_against, 
                passing_num_actions_for, passing_goals_added_for, passing_num_actions_against, passing_goals_added_against, 
                interrupting_num_actions_for, interrupting_goals_added_for, interrupting_num_actions_against, interrupting_goals_added_against, 
                receiving_num_actions_for, receiving_goals_added_for, receiving_num_actions_against, receiving_goals_added_against, 
                claiming_num_actions_for, claiming_goals_added_for, claiming_num_actions_against, claiming_goals_added_against, 
                fouling_num_actions_for, fouling_goals_added_for, fouling_num_actions_against, fouling_goals_added_against, season
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            obj_id, team_id, minutes,
            int(actions['Dribbling']['num_actions_for']),
            round(actions['Dribbling']['goals_added_for'], 1),
            int(actions['Dribbling']['num_actions_against']),
            round(actions['Dribbling']['goals_added_against'], 1),
            int(actions['Shooting']['num_actions_for']),
            round(actions['Shooting']['goals_added_for'], 1),
            int(actions['Shooting']['num_actions_against']),
            round(actions['Shooting']['goals_added_against'], 1),
            int(actions['Passing']['num_actions_for']),
            round(actions['Passing']['goals_added_for'], 1),
            int(actions['Passing']['num_actions_against']),
            round(actions['Passing']['goals_added_against'], 1),
            int(actions['Interrupting']['num_actions_for']),
            round(actions['Interrupting']['goals_added_for'], 1),
            int(actions['Interrupting']['num_actions_against']),
            round(actions['Interrupting']['goals_added_against'], 1),
            int(actions['Receiving']['num_actions_for']),
            round(actions['Receiving']['goals_added_for'], 1),
            int(actions['Receiving']['num_actions_against']),
            round(actions['Receiving']['goals_added_against'], 1),
            int(actions['Claiming']['num_actions_for']),
            round(actions['Claiming']['goals_added_for'], 1),
            int(actions['Claiming']['num_actions_against']),
            round(actions['Claiming']['goals_added_against'], 1),
            int(actions['Fouling']['num_actions_for']),
            round(actions['Fouling']['goals_added_for'], 1),
            int(actions['Fouling']['num_actions_against']),
            round(actions['Fouling']['goals_added_against'], 1),
            int(season)
        ))
        conn.commit()
    cursor.close()
    conn.close()

def get_team_goals_added_by_season(team_id, season):
    print('Fetching team goals added for:{}, Season: {}'.format(team_id, season))
    obj_id = team_id + str(season)
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    query = f'''
        SELECT 
            tga.*,
            ti.*
        FROM 
            team_goals_added AS tga
        JOIN 
            team_info AS ti
        ON 
            tga.team_id = ti.team_id
        WHERE
            tga.id = ?;
    '''
    cursor.execute(query, (obj_id,))
    row = cursor.fetchone()
    conn.commit()
    conn.close()
    print('Player goals added returned.')
    return row 

import sqlite3
from .data_util import get_db_path

def get_all_teams_goals_added_by_season(season):
    print(f'Fetching all team goals added stats for Season: {season}')
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    query = '''
        SELECT 
            tga.*,
            ti.*
        FROM 
            team_goals_added AS tga
        JOIN 
            team_info AS ti
        ON 
            tga.team_id = ti.team_id
        WHERE
            tga.season = ?
    '''

    cursor.execute(query, (season,))
    rows = cursor.fetchall()
    conn.commit()
    conn.close()

    print(f'{len(rows)} team goals added rows returned.')
    return rows  # List of sqlite3.Row objects
