from api import make_asa_api_call
from .data_util import generate_player_season_id, aggregate_position_data, MINIMUM_MINUTES, get_db_path
import sqlite3

def get_goalkeeper_goals_added_by_season(player_id, season):
    print('Fetching goalkeeper xgoals for:{}, Season: {}'.format(player_id, season))
    obj_id = generate_player_season_id(player_id=player_id, season=str(season))
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    query = '''
        SELECT 
            gkga.*,
            pi.*,
            ti.*
            FROM 
                goalkeeper_goals_added AS gkga
            JOIN 
                player_info AS pi
            ON 
                gkga.player_id = pi.player_id
            JOIN
                team_info AS ti
            ON
                gkga.team_id = ti.team_id
            WHERE
                gkga.id = ?;
    '''
    cursor.execute(query, (obj_id,))
    row = cursor.fetchone()
    if row is None:
        print(f"WARNING: No goalkeeper goals added data found for player_id={player_id} season={season}.")
    conn.commit()
    conn.close()
    print('Goalkeeper goals added returned.')
    return row

'''
INSERT GOALS ADDED DATA
'''
def insert_goalkeeper_goals_added_by_season(season): # pragma: no cover
    print(f'Inserting data for goalkeepers (goals added) for season: {season}')
    conn = sqlite3.connect('data/nwsl.db')

    stats_to_track = [
        'claiming_goals_added_raw',
        'claiming_goals_added_above_avg',
        'claiming_count_actions',

        'fielding_goals_added_raw',
        'fielding_goals_added_above_avg',
        'fielding_count_actions',

        'handling_goals_added_raw',
        'handling_goals_added_above_avg',
        'handling_count_actions',

        'passing_goals_added_raw',
        'passing_goals_added_above_avg',
        'passing_count_actions',

        'shotstopping_goals_added_raw',
        'shotstopping_goals_added_above_avg',
        'shotstopping_count_actions',

        'sweeping_goals_added_raw',
        'sweeping_goals_added_above_avg',
        'sweeping_count_actions',
    ]

    keepers_data = fetch_keeper_goals_added_data(season)
    filtered_players = calculate_player_statistics(keepers_data)
    position_data = aggregate_position_data(filtered_players, stats_to_track)
    insert_keeper_data(conn, keepers_data, position_data, stats_to_track, season)

    conn.close()
    print(f'Keeper goals added data for season {season} inserted successfully.')

def fetch_keeper_goals_added_data(season: int):
    """
    Fetch keeper data from the API for a specific season.

    Args:
        season (int): The season year.

    Returns:
        list: A list of keeper data dictionaries.
    """

    api_string = 'nwsl/goalkeepers/goals-added?season_name={}&stage_name=Regular Season'.format(str(season))
    keepers_data = make_asa_api_call(api_string)[1]

    for keeper in keepers_data:
        for action in keeper.get('data', []):
            action_type = action['action_type'].lower()  # Lowercase the action type for key consistency
            keeper[f"{action_type}_goals_added_raw"] = action['goals_added_raw']
            keeper[f"{action_type}_goals_added_above_avg"] = action['goals_added_above_avg']
            keeper[f"{action_type}_count_actions"] = action['count_actions']

    data = [keeper for keeper in keepers_data]

    if len(data) == 0:
        print('WARNING: No data returned when fetching api data for goalkeeper goals added.')

    return data

def calculate_player_statistics(keepers_data: list):
    """
    Return a list of player statistics. Any custom filtering should be done in this function.

    Args:
        keepers_data (list): List of keeper data dictionaries.

    Returns:
        list: Filtered list of player data dictionaries with calculated statistics.
    """

    data = [player for player in keepers_data if player.get('minutes_played', 0) >= MINIMUM_MINUTES]

    if len(data) == 0:
        print('WARNING: No data returned when calculating player statistics in goalkeeper goals added.')

    return data

def insert_keeper_data(conn, keepers_data, position_data, stats_to_track, season): # pragma: no cover
    """
    Insert keeper data into the database, rounding all REAL values to two decimal places.

    Args:
        conn (sqlite3.Connection): Database connection.
        keepers_data (list): List of keeper data dictionaries.
        position_data (dict): Aggregated position data.
        stats_to_track (list): List of stats to track.
        season (int): The season year.
    """
    cursor = conn.cursor()
    for keeper in keepers_data:
        player_id = keeper.get('player_id', 'Unknown Player ID')
        obj_id = generate_player_season_id(player_id=player_id, season=str(season))
        team_id = keeper.get('team_id', 'Unknown Team ID')

        if isinstance(team_id, list):  # Handle case where team_id is a list
            team_id = team_id[-1]  # Choose the last item or another appropriate element
        elif not isinstance(team_id, str):
            team_id = 'Unknown Team ID'
        general_position = keeper.get('general_position', 'Unknown General Position')
        minutes_played = keeper.get('minutes_played', 0)

        # Initialize stats for all goalkeeper action types
        claiming_goals_added_raw = 0
        claiming_goals_added_above_avg = 0
        claiming_count_actions = 0

        fielding_goals_added_raw = 0
        fielding_goals_added_above_avg = 0
        fielding_count_actions = 0

        handling_goals_added_raw = 0
        handling_goals_added_above_avg = 0
        handling_count_actions = 0

        passing_goals_added_raw = 0
        passing_goals_added_above_avg = 0
        passing_count_actions = 0

        shotstopping_goals_added_raw = 0
        shotstopping_goals_added_above_avg = 0
        shotstopping_count_actions = 0

        sweeping_goals_added_raw = 0
        sweeping_goals_added_above_avg = 0
        sweeping_count_actions = 0

        # Populate stats with actual data
        for action in keeper.get('data', []):
            action_type = action.get('action_type', '').lower()
            if action_type == 'claiming':
                claiming_goals_added_raw = round(action.get('goals_added_raw', 0), 2)
                claiming_goals_added_above_avg = round(action.get('goals_added_above_avg', 0), 2)
                claiming_count_actions = action.get('count_actions', 0)
            elif action_type == 'fielding':
                fielding_goals_added_raw = round(action.get('goals_added_raw', 0), 2)
                fielding_goals_added_above_avg = round(action.get('goals_added_above_avg', 0), 2)
                fielding_count_actions = action.get('count_actions', 0)
            elif action_type == 'handling':
                handling_goals_added_raw = round(action.get('goals_added_raw', 0), 2)
                handling_goals_added_above_avg = round(action.get('goals_added_above_avg', 0), 2)
                handling_count_actions = action.get('count_actions', 0)
            elif action_type == 'passing':
                passing_goals_added_raw = round(action.get('goals_added_raw', 0), 2)
                passing_goals_added_above_avg = round(action.get('goals_added_above_avg', 0), 2)
                passing_count_actions = action.get('count_actions', 0)
            elif action_type == 'shotstopping':
                shotstopping_goals_added_raw = round(action.get('goals_added_raw', 0), 2)
                shotstopping_goals_added_above_avg = round(action.get('goals_added_above_avg', 0), 2)
                shotstopping_count_actions = action.get('count_actions', 0)
            elif action_type == 'sweeping':
                sweeping_goals_added_raw = round(action.get('goals_added_raw', 0), 2)
                sweeping_goals_added_above_avg = round(action.get('goals_added_above_avg', 0), 2)
                sweeping_count_actions = action.get('count_actions', 0)


        position_avg = {f"avg_{stat}": round(position_data.get(general_position, {}).get(f"avg_{stat}", 0), 2) for stat in stats_to_track}
        position_min = {f"min_{stat}": round(position_data.get(general_position, {}).get(f"min_{stat}", 0), 2) for stat in stats_to_track}
        position_max = {f"max_{stat}": round(position_data.get(general_position, {}).get(f"max_{stat}", 0), 2) for stat in stats_to_track}

        cursor.execute('''
            INSERT OR REPLACE INTO goalkeeper_goals_added (
                id,
                player_id,
                team_id,
                season,
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
                avg_claiming_goals_added_raw,
                avg_claiming_goals_added_above_avg,
                avg_claiming_count_actions,
                avg_fielding_goals_added_raw,
                avg_fielding_goals_added_above_avg,
                avg_fielding_count_actions,
                avg_handling_goals_added_raw,
                avg_handling_goals_added_above_avg,
                avg_handling_count_actions,
                avg_passing_goals_added_raw,
                avg_passing_goals_added_above_avg,
                avg_passing_count_actions,
                avg_shotstopping_goals_added_raw,
                avg_shotstopping_goals_added_above_avg,
                avg_shotstopping_count_actions,
                avg_sweeping_goals_added_raw,
                avg_sweeping_goals_added_above_avg,
                avg_sweeping_count_actions,
                min_claiming_goals_added_raw,
                min_claiming_goals_added_above_avg,
                min_claiming_count_actions,
                min_fielding_goals_added_raw,
                min_fielding_goals_added_above_avg,
                min_fielding_count_actions,
                min_handling_goals_added_raw,
                min_handling_goals_added_above_avg,
                min_handling_count_actions,
                min_passing_goals_added_raw,
                min_passing_goals_added_above_avg,
                min_passing_count_actions,
                min_shotstopping_goals_added_raw,
                min_shotstopping_goals_added_above_avg,
                min_shotstopping_count_actions,
                min_sweeping_goals_added_raw,
                min_sweeping_goals_added_above_avg,
                min_sweeping_count_actions,
                max_claiming_goals_added_raw,
                max_claiming_goals_added_above_avg,
                max_claiming_count_actions,
                max_fielding_goals_added_raw,
                max_fielding_goals_added_above_avg,
                max_fielding_count_actions,
                max_handling_goals_added_raw,
                max_handling_goals_added_above_avg,
                max_handling_count_actions,
                max_passing_goals_added_raw,
                max_passing_goals_added_above_avg,
                max_passing_count_actions,
                max_shotstopping_goals_added_raw,
                max_shotstopping_goals_added_above_avg,
                max_shotstopping_count_actions,
                max_sweeping_goals_added_raw,
                max_sweeping_goals_added_above_avg,
                max_sweeping_count_actions
            ) VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            obj_id,
            player_id,
            team_id,
            int(season),
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

            position_avg['avg_claiming_goals_added_raw'],
            position_avg['avg_claiming_goals_added_above_avg'],
            position_avg['avg_claiming_count_actions'],
            position_avg['avg_fielding_goals_added_raw'],
            position_avg['avg_fielding_goals_added_above_avg'],
            position_avg['avg_fielding_count_actions'],
            position_avg['avg_handling_goals_added_raw'],
            position_avg['avg_handling_goals_added_above_avg'],
            position_avg['avg_handling_count_actions'],
            position_avg['avg_passing_goals_added_raw'],
            position_avg['avg_passing_goals_added_above_avg'],
            position_avg['avg_passing_count_actions'],
            position_avg['avg_shotstopping_goals_added_raw'],
            position_avg['avg_shotstopping_goals_added_above_avg'],
            position_avg['avg_shotstopping_count_actions'],
            position_avg['avg_sweeping_goals_added_raw'],
            position_avg['avg_sweeping_goals_added_above_avg'],
            position_avg['avg_sweeping_count_actions'],

            position_min['min_claiming_goals_added_raw'],
            position_min['min_claiming_goals_added_above_avg'],
            position_min['min_claiming_count_actions'],
            position_min['min_fielding_goals_added_raw'],
            position_min['min_fielding_goals_added_above_avg'],
            position_min['min_fielding_count_actions'],
            position_min['min_handling_goals_added_raw'],
            position_min['min_handling_goals_added_above_avg'],
            position_min['min_handling_count_actions'],
            position_min['min_passing_goals_added_raw'],
            position_min['min_passing_goals_added_above_avg'],
            position_min['min_passing_count_actions'],
            position_min['min_shotstopping_goals_added_raw'],
            position_min['min_shotstopping_goals_added_above_avg'],
            position_min['min_shotstopping_count_actions'],
            position_min['min_sweeping_goals_added_raw'],
            position_min['min_sweeping_goals_added_above_avg'],
            position_min['min_sweeping_count_actions'],

            position_max['max_claiming_goals_added_raw'],
            position_max['max_claiming_goals_added_above_avg'],
            position_max['max_claiming_count_actions'],
            position_max['max_fielding_goals_added_raw'],
            position_max['max_fielding_goals_added_above_avg'],
            position_max['max_fielding_count_actions'],
            position_max['max_handling_goals_added_raw'],
            position_max['max_handling_goals_added_above_avg'],
            position_max['max_handling_count_actions'],
            position_max['max_passing_goals_added_raw'],
            position_max['max_passing_goals_added_above_avg'],
            position_max['max_passing_count_actions'],
            position_max['max_shotstopping_goals_added_raw'],
            position_max['max_shotstopping_goals_added_above_avg'],
            position_max['max_shotstopping_count_actions'],
            position_max['max_sweeping_goals_added_raw'],
            position_max['max_sweeping_goals_added_above_avg'],
            position_max['max_sweeping_count_actions']
        ))
        
    conn.commit()