from api import make_api_call
import sqlite3

def insert_goalkeeper_goals_added_by_season(season):
    print('Inserting goals added by season for:', season)
    api_string = 'nwsl/goalkeepers/goals-added?season_name={}'.format(str(season))
    players_data = make_api_call(api_string)[1]
    conn = sqlite3.connect('db/nwsl.db')
    cursor = conn.cursor()
    for player in players_data:
        player_id = player.get('player_id', 'Unknown Player ID')
        team_id = player.get('team_id', 'Unknown Team ID')
        minutes_played = player.get('minutes_played', 0)

        for action in player.get('data', []):
            match (action.get('action_type')):
                case 'Claiming':
                    claiming_goals_added_raw = action.get('goals_added_raw')
                    claiming_goals_added_above_avg = action.get('goals_added_above_avg')
                    claiming_count_actions = action.get('count_actions')
                case 'Fielding':
                    fielding_goals_added_raw = action.get('goals_added_raw')
                    fielding_goals_added_above_avg = action.get('goals_added_above_avg')
                    fielding_count_actions = action.get('count_actions')
                case 'Handling':
                    handling_goals_added_raw = action.get('goals_added_raw')
                    handling_goals_added_above_avg = action.get('goals_added_above_avg')
                    handling_count_actions = action.get('count_actions')
                case 'Passing':
                    passing_goals_added_raw = action.get('goals_added_raw')
                    passing_goals_added_above_avg = action.get('goals_added_above_avg')
                    passing_count_actions = action.get('count_actions')
                case 'Shotstopping':
                    shotstopping_goals_added_raw = action.get('goals_added_raw')
                    shotstopping_goals_added_above_avg = action.get('goals_added_above_avg')
                    shotstopping_count_actions = action.get('count_actions')
                case 'Sweeping':
                    sweeping_goals_added_raw = action.get('goals_added_raw')
                    sweeping_goals_added_above_avg = action.get('goals_added_above_avg')
                    sweeping_count_actions = action.get('count_actions')
                case _:
                    print('No action found!')
        
        if isinstance(team_id, list):
            team_id = team_id[-1]
        elif isinstance(team_id, str):
            pass
        else:
            print('No team associated with player:', player_id)
        
        cursor.execute('''
            INSERT OR REPLACE INTO goalkeeper_goals_added (
                player_id,
                team_id,
                minutes_played,
                claiming_goals_added_raw,
                claiming_goals_added_above_avg,
                claiming_count_actions,
                fielding_goals_added_raw,
                fielding_goals_added_above_avg,
                fielding_count_actions,
                handling_goals_added_raw,
                handling_goals_added_above_avg,
                handling_count_actions,
                passing_goals_added_raw,
                passing_goals_added_above_avg,
                passing_count_actions,
                shotstopping_goals_added_raw,
                shotstopping_goals_added_above_avg,
                shotstopping_count_actions,
                sweeping_goals_added_raw,
                sweeping_goals_added_above_avg,
                sweeping_count_actions,
                season
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            player_id,
            team_id,
            minutes_played,
            claiming_goals_added_raw,
            claiming_goals_added_above_avg,
            claiming_count_actions,
            fielding_goals_added_raw,
            fielding_goals_added_above_avg,
            fielding_count_actions,
            handling_goals_added_raw,
            handling_goals_added_above_avg,
            handling_count_actions,
            passing_goals_added_raw,
            passing_goals_added_above_avg,
            passing_count_actions,
            shotstopping_goals_added_raw,
            shotstopping_goals_added_above_avg,
            shotstopping_count_actions,
            sweeping_goals_added_raw,
            sweeping_goals_added_above_avg,
            sweeping_count_actions,
            int(season)
        ))
        conn.commit()
    cursor.close()
    conn.close()

def get_goalkeeper_goals_added_by_season(player_id, season):
    print('Fetching goalkeeper xgoals for:{}, Season: {}'.format(player_id, season))
    conn = sqlite3.connect('db/nwsl.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM goalkeeper_goals_added WHERE player_id = ? AND season = ?', (player_id, season))
    row = cursor.fetchone()
    conn.commit()
    conn.close()
    print('Goalkeeper goals added returned.')
    return row