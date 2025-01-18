from api import make_asa_api_call
import sqlite3
from collections import defaultdict

def insert_player_goals_added_by_season(season):
    print(f'Inserting goals added by season (players) for: {season}')
    
    # Fetch player data
    api_string = f'nwsl/players/goals-added?season_name={season}&stage_name=Regular Season'
    players_data = make_asa_api_call(api_string)[1]
    conn = sqlite3.connect('data/nwsl.db')
    cursor = conn.cursor()

    # Group by position to calculate sums and counts for averages
    position_sums = defaultdict(lambda: defaultdict(float))
    position_counts = defaultdict(int)

    for player in players_data:
        position = player.get('general_position', 'Unknown Position')
        position_counts[position] += 1

        for action in player.get('data', []):
            action_type = action.get('action_type', '').lower()
            position_sums[position][f'{action_type}_goals_added_raw'] += round(action.get('goals_added_raw', 0), 2)
            position_sums[position][f'{action_type}_goals_added_above_avg'] += round(action.get('goals_added_above_avg', 0), 2)
            position_sums[position][f'{action_type}_count_actions'] += action.get('count_actions', 0)

    # Calculate averages for each position
    position_averages = {
        position: {f"avg_{key}": round(value / position_counts[position], 2) for key, value in sums.items()}
        for position, sums in position_sums.items()
    }

    # Insert player data and calculated averages
    for player in players_data:
        player_id = player.get('player_id', 'Unknown Player ID')
        obj_id = player_id + str(season)
        team_id = player.get('team_id', 'Unknown Team ID')
        if isinstance(team_id, list):  # Handle case where team_id is a list
            team_id = team_id[-1]  # Choose the last item or another appropriate element
        elif not isinstance(team_id, str):  # Default to a string if not already
            team_id = 'Unknown Team ID'
        general_position = player.get('general_position', 'Unknown Position')
        minutes_played = player.get('minutes_played', 0)

        # Initialize stats for all action types
        dribbling_goals_added_raw = 0
        dribbling_goals_added_above_avg = 0
        dribbling_count_actions = 0
        fouling_goals_added_raw = 0
        fouling_goals_added_above_avg = 0
        fouling_count_actions = 0
        interrupting_goals_added_raw = 0
        interrupting_goals_added_above_avg = 0
        interrupting_count_actions = 0
        passing_goals_added_raw = 0
        passing_goals_added_above_avg = 0
        passing_count_actions = 0
        receiving_goals_added_raw = 0
        receiving_goals_added_above_avg = 0
        receiving_count_actions = 0
        shooting_goals_added_raw = 0
        shooting_goals_added_above_avg = 0
        shooting_count_actions = 0

        # Populate stats with actual data
        for action in player.get('data', []):
            action_type = action.get('action_type', '').lower()
            if action_type == 'dribbling':
                dribbling_goals_added_raw = round(action.get('goals_added_raw', 0), 2)
                dribbling_goals_added_above_avg = round(action.get('goals_added_above_avg', 0), 2)
                dribbling_count_actions = action.get('count_actions', 0)
            elif action_type == 'fouling':
                fouling_goals_added_raw = round(action.get('goals_added_raw', 0), 2)
                fouling_goals_added_above_avg = round(action.get('goals_added_above_avg', 0), 2)
                fouling_count_actions = action.get('count_actions', 0)
            elif action_type == 'interrupting':
                interrupting_goals_added_raw = round(action.get('goals_added_raw', 0), 2)
                interrupting_goals_added_above_avg = round(action.get('goals_added_above_avg', 0), 2)
                interrupting_count_actions = action.get('count_actions', 0)
            elif action_type == 'passing':
                passing_goals_added_raw = round(action.get('goals_added_raw', 0), 2)
                passing_goals_added_above_avg = round(action.get('goals_added_above_avg', 0), 2)
                passing_count_actions = action.get('count_actions', 0)
            elif action_type == 'receiving':
                receiving_goals_added_raw = round(action.get('goals_added_raw', 0), 2)
                receiving_goals_added_above_avg = round(action.get('goals_added_above_avg', 0), 2)
                receiving_count_actions = action.get('count_actions', 0)
            elif action_type == 'shooting':
                shooting_goals_added_raw = round(action.get('goals_added_raw', 0), 2)
                shooting_goals_added_above_avg = round(action.get('goals_added_above_avg', 0), 2)
                shooting_count_actions = action.get('count_actions', 0)

        # Get position averages
        position_avg = position_averages.get(
            general_position, {f"avg_{key}": 0 for key in position_sums['Unknown Position'].keys()}
        )

        # Insert data into database explicitly
        cursor.execute('''
            INSERT OR REPLACE INTO player_goals_added (
                id, player_id, team_id, general_position, minutes_played,
                dribbling_goals_added_raw, dribbling_goals_added_above_avg, dribbling_count_actions,
                fouling_goals_added_raw, fouling_goals_added_above_avg, fouling_count_actions,
                interrupting_goals_added_raw, interrupting_goals_added_above_avg, interrupting_count_actions,
                passing_goals_added_raw, passing_goals_added_above_avg, passing_count_actions,
                receiving_goals_added_raw, receiving_goals_added_above_avg, receiving_count_actions,
                shooting_goals_added_raw, shooting_goals_added_above_avg, shooting_count_actions,
                avg_dribbling_goals_added_raw, avg_dribbling_goals_added_above_avg, avg_dribbling_count_actions,
                avg_fouling_goals_added_raw, avg_fouling_goals_added_above_avg, avg_fouling_count_actions,
                avg_interrupting_goals_added_raw, avg_interrupting_goals_added_above_avg, avg_interrupting_count_actions,
                avg_passing_goals_added_raw, avg_passing_goals_added_above_avg, avg_passing_count_actions,
                avg_receiving_goals_added_raw, avg_receiving_goals_added_above_avg, avg_receiving_count_actions,
                avg_shooting_goals_added_raw, avg_shooting_goals_added_above_avg, avg_shooting_count_actions,
                season
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            obj_id, player_id, team_id, general_position, minutes_played,
            dribbling_goals_added_raw, dribbling_goals_added_above_avg, dribbling_count_actions,
            fouling_goals_added_raw, fouling_goals_added_above_avg, fouling_count_actions,
            interrupting_goals_added_raw, interrupting_goals_added_above_avg, interrupting_count_actions,
            passing_goals_added_raw, passing_goals_added_above_avg, passing_count_actions,
            receiving_goals_added_raw, receiving_goals_added_above_avg, receiving_count_actions,
            shooting_goals_added_raw, shooting_goals_added_above_avg, shooting_count_actions,
            position_avg.get('avg_dribbling_goals_added_raw', 0), position_avg.get('avg_dribbling_goals_added_above_avg', 0), position_avg.get('avg_dribbling_count_actions', 0),
            position_avg.get('avg_fouling_goals_added_raw', 0), position_avg.get('avg_fouling_goals_added_above_avg', 0), position_avg.get('avg_fouling_count_actions', 0),
            position_avg.get('avg_interrupting_goals_added_raw', 0), position_avg.get('avg_interrupting_goals_added_above_avg', 0), position_avg.get('avg_interrupting_count_actions', 0),
            position_avg.get('avg_passing_goals_added_raw', 0), position_avg.get('avg_passing_goals_added_above_avg', 0), position_avg.get('avg_passing_count_actions', 0),
            position_avg.get('avg_receiving_goals_added_raw', 0), position_avg.get('avg_receiving_goals_added_above_avg', 0), position_avg.get('avg_receiving_count_actions', 0),
            position_avg.get('avg_shooting_goals_added_raw', 0), position_avg.get('avg_shooting_goals_added_above_avg', 0), position_avg.get('avg_shooting_count_actions', 0),
            int(season)
        ))

    conn.commit()
    cursor.close()
    conn.close()
    print(f'Player goals added data for season {season} inserted with position-specific averages.')



def get_player_goals_added_by_season(player_id, season):
    print('Fetching player goals added for:{}, Season: {}'.format(player_id, season))
    obj_id = player_id + str(season)
    conn = sqlite3.connect('data/nwsl.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    query = f'''
        SELECT 
            pga.*,
            pi.player_name,
            pi.player_first_name,
            pi.player_last_name,
            ti.team_name
            FROM 
                player_goals_added AS pga
            JOIN 
                player_info AS pi
            ON 
                pga.player_id = pi.player_id
            JOIN
                team_info AS ti
            ON
                pga.team_id = ti.team_id   
            WHERE
                pga.id = ?;
        '''
    cursor.execute(query, (obj_id,))
    row = cursor.fetchone()
    conn.commit()
    conn.close()
    print('Player goals added returned.')
    return row