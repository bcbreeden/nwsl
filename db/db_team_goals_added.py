from api import make_asa_api_call
import sqlite3

def insert_team_goals_added_by_season(season):
    print('Inserting goals added by season (teams) for:', season)
    api_string = 'nwsl/teams/goals-added?season_name={}&stage_name=Regular Season'.format(str(season))
    teams_data = make_asa_api_call(api_string)[1]
    conn = sqlite3.connect('db/nwsl.db')
    cursor = conn.cursor()
    for team in teams_data:
        team_id = team.get('team_id', 'Unknown Team ID')
        obj_id = team_id + str(season)
        minutes = team.get('minutes', 0)

        for action in team.get('data', []):
            match (action.get('action_type')):
                case 'Dribbling':
                    dribbling_num_actions_for = action.get('num_actions_for', 0)
                    dribbling_goals_added_for = action.get('goals_added_for', 0)
                    dribbling_num_actions_against = action.get('num_actions_against', 0)
                    dribbling_goals_added_against = action.get('goals_added_against', 0)
                case 'Shooting':
                    shooting_num_actions_for = action.get('num_actions_for', 0)
                    shooting_goals_added_for = action.get('goals_added_for', 0)
                    shooting_num_actions_against = action.get('num_actions_against', 0)
                    shooting_goals_added_against = action.get('goals_added_against', 0)
                case 'Passing':
                    passing_num_actions_for = action.get('num_actions_for', 0)
                    passing_goals_added_for = action.get('goals_added_for', 0)
                    passing_num_actions_against = action.get('num_actions_against', 0)
                    passing_goals_added_against = action.get('goals_added_against', 0)
                case 'Interrupting':
                    interrupting_num_actions_for = action.get('num_actions_for', 0)
                    interrupting_goals_added_for = action.get('goals_added_for', 0)
                    interrupting_num_actions_against = action.get('num_actions_against', 0)
                    interrupting_goals_added_against = action.get('goals_added_against', 0)
                case 'Receiving':
                    receiving_num_actions_for = action.get('num_actions_for', 0)
                    receiving_goals_added_for = action.get('goals_added_for', 0)
                    receiving_num_actions_against = action.get('num_actions_against', 0)
                    receiving_goals_added_against = action.get('goals_added_against', 0)
                case 'Claiming':
                    claiming_num_actions_for = action.get('num_actions_for', 0)
                    claiming_goals_added_for = action.get('goals_added_for', 0)
                    claiming_num_actions_against = action.get('num_actions_against', 0)
                    claiming_goals_added_against = action.get('goals_added_against', 0)
                case 'Fouling':
                    fouling_num_actions_for = action.get('num_actions_for', 0)
                    fouling_goals_added_for = action.get('goals_added_for', 0)
                    fouling_num_actions_against = action.get('num_actions_against', 0)
                    fouling_goals_added_against = action.get('goals_added_against', 0)
                case _:
                    print('No action found!')

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
            dribbling_num_actions_for, dribbling_goals_added_for, dribbling_num_actions_against, dribbling_goals_added_against, 
            shooting_num_actions_for, shooting_goals_added_for, shooting_num_actions_against, shooting_goals_added_against, 
            passing_num_actions_for, passing_goals_added_for, passing_num_actions_against, passing_goals_added_against, 
            interrupting_num_actions_for, interrupting_goals_added_for, interrupting_num_actions_against, interrupting_goals_added_against, 
            receiving_num_actions_for, receiving_goals_added_for, receiving_num_actions_against, receiving_goals_added_against, 
            claiming_num_actions_for, claiming_goals_added_for, claiming_num_actions_against, claiming_goals_added_against, 
            fouling_num_actions_for, fouling_goals_added_for, fouling_num_actions_against, fouling_goals_added_against, int(season)
        ))
        conn.commit()
    cursor.close()
    conn.close()

def get_team_goals_added_by_season(team_id, season):
    print('Fetching team goals added for:{}, Season: {}'.format(team_id, season))
    obj_id = team_id + str(season)
    conn = sqlite3.connect('db/nwsl.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM team_goals_added WHERE id = ?', (obj_id,))
    row = cursor.fetchone()
    conn.commit()
    conn.close()
    print('Player goals added returned.')
    return row