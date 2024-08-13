from api import make_api_call
import sqlite3

def insert_player_goals_added_by_season(season):
    print('Inserting goals added by season for:', season)
    api_string = 'nwsl/players/goals-added?season_name={}'.format(str(season))
    players_data = make_api_call(api_string)[1]
    conn = sqlite3.connect('db/nwsl.db')
    cursor = conn.cursor()
    for player in players_data:
        player_id = player.get('player_id', 'Unknown Player ID')
        team_id = player.get('team_id', 'Unknown Team ID')
        general_position =  player.get('general_position', 'Unknown Position')
        minutes_played = player.get('minutes_played', 0)

        for action in player.get('data', []):
            match (action.get('action_type')):
                case 'Dribbling':
                    dribbling_goals_added_raw = action.get('goals_added_raw')
                    dribbling_goals_added_above_avg = action.get('goals_added_above_avg')
                    dribbling_count_actions = action.get('count_actions')
                case 'Fouling':
                    fouling_goals_added_raw = action.get('goals_added_raw')
                    fouling_goals_added_above_avg = action.get('goals_added_above_avg')
                    fouling_count_actions = action.get('count_actions')
                case 'Interrupting':
                    interrupting_goals_added_raw = action.get('goals_added_raw')
                    interrupting_goals_added_above_avg = action.get('goals_added_above_avg')
                    interrupting_count_actions = action.get('count_actions')
                case 'Passing':
                    passing_goals_added_raw = action.get('goals_added_raw')
                    passing_goals_added_above_avg = action.get('goals_added_above_avg')
                    passing_count_actions = action.get('count_actions')
                case 'Receiving':
                    receiving_goals_added_raw = action.get('goals_added_raw')
                    receiving_goals_added_above_avg = action.get('goals_added_above_avg')
                    receiving_count_actions = action.get('count_actions')
                case 'Shooting':
                    shooting_goals_added_raw = action.get('goals_added_raw')
                    shooting_goals_added_above_avg = action.get('goals_added_above_avg')
                    shooting_count_actions = action.get('count_actions')
                case _:
                    print('No action found!')
        
        if isinstance(team_id, list):
            team_id = team_id[-1]
        elif isinstance(team_id, str):
            pass
        else:
            print('No team associated with player:', player_id)
        cursor.execute('''
            INSERT OR REPLACE INTO player_goals_added (
                player_id,
                team_id,
                general_position,
                minutes_played,
                dribbling_goals_added_raw,
                dribbling_goals_added_above_avg,
                dribbling_count_actions,
                fouling_goals_added_raw,
                fouling_goals_added_above_avg,
                fouling_count_actions,
                interrupting_goals_added_raw,
                interrupting_goals_added_above_avg,
                interrupting_count_actions,
                passing_goals_added_raw,
                passing_goals_added_above_avg,
                passing_count_actions,
                receiving_goals_added_raw,
                receiving_goals_added_above_avg,
                receiving_count_actions,
                shooting_goals_added_raw,
                shooting_goals_added_above_avg,
                shooting_count_actions
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            player_id,
            team_id,
            general_position,
            minutes_played,
            dribbling_goals_added_raw,
            dribbling_goals_added_above_avg,
            dribbling_count_actions,
            fouling_goals_added_raw,
            fouling_goals_added_above_avg,
            fouling_count_actions,
            interrupting_goals_added_raw,
            interrupting_goals_added_above_avg,
            interrupting_count_actions,
            passing_goals_added_raw,
            passing_goals_added_above_avg,
            passing_count_actions,
            receiving_goals_added_raw,
            receiving_goals_added_above_avg,
            receiving_count_actions,
            shooting_goals_added_raw,
            shooting_goals_added_above_avg,
            shooting_count_actions
        ))
        conn.commit()
    cursor.close()
    conn.close()
