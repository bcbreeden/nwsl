from api import make_asa_api_call
from .data_util import generate_player_season_id, aggregate_position_data
import sqlite3

# def insert_goalkeeper_goals_added_by_season(season):
#     print('Inserting goals added by season for:', season)
#     api_string = 'nwsl/goalkeepers/goals-added?season_name={}&stage_name=Regular Season'.format(str(season))
#     players_data = make_asa_api_call(api_string)[1]
#     conn = sqlite3.connect('data/nwsl.db')
#     cursor = conn.cursor()
#     for player in players_data:
#         player_id = player.get('player_id', 'Unknown Player ID')
#         obj_id = generate_player_season_id(player_id=player_id, season=str(season))
#         team_id = player.get('team_id', 'Unknown Team ID')
#         minutes_played = player.get('minutes_played', 0)

#         for action in player.get('data', []):
#             match (action.get('action_type')):
#                 case 'Claiming':
#                     claiming_goals_added_raw = action.get('goals_added_raw')
#                     claiming_goals_added_above_avg = action.get('goals_added_above_avg')
#                     claiming_count_actions = action.get('count_actions')
#                 case 'Fielding':
#                     fielding_goals_added_raw = action.get('goals_added_raw')
#                     fielding_goals_added_above_avg = action.get('goals_added_above_avg')
#                     fielding_count_actions = action.get('count_actions')
#                 case 'Handling':
#                     handling_goals_added_raw = action.get('goals_added_raw')
#                     handling_goals_added_above_avg = action.get('goals_added_above_avg')
#                     handling_count_actions = action.get('count_actions')
#                 case 'Passing':
#                     passing_goals_added_raw = action.get('goals_added_raw')
#                     passing_goals_added_above_avg = action.get('goals_added_above_avg')
#                     passing_count_actions = action.get('count_actions')
#                 case 'Shotstopping':
#                     shotstopping_goals_added_raw = action.get('goals_added_raw')
#                     shotstopping_goals_added_above_avg = action.get('goals_added_above_avg')
#                     shotstopping_count_actions = action.get('count_actions')
#                 case 'Sweeping':
#                     sweeping_goals_added_raw = action.get('goals_added_raw')
#                     sweeping_goals_added_above_avg = action.get('goals_added_above_avg')
#                     sweeping_count_actions = action.get('count_actions')
#                 case _:
#                     print('No action found!')
        
#         if isinstance(team_id, list):
#             team_id = team_id[-1]
#         elif isinstance(team_id, str):
#             pass
#         else:
#             print('No team associated with player:', player_id)
        
#         cursor.execute('''
#             INSERT OR REPLACE INTO goalkeeper_goals_added (
#                 id,
#                 player_id,
#                 team_id,
#                 minutes_played,
#                 claiming_goals_added_raw,
#                 claiming_goals_added_above_avg,
#                 claiming_count_actions,
#                 fielding_goals_added_raw,
#                 fielding_goals_added_above_avg,
#                 fielding_count_actions,
#                 handling_goals_added_raw,
#                 handling_goals_added_above_avg,
#                 handling_count_actions,
#                 passing_goals_added_raw,
#                 passing_goals_added_above_avg,
#                 passing_count_actions,
#                 shotstopping_goals_added_raw,
#                 shotstopping_goals_added_above_avg,
#                 shotstopping_count_actions,
#                 sweeping_goals_added_raw,
#                 sweeping_goals_added_above_avg,
#                 sweeping_count_actions,
#                 season
#             ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
#         ''', (
#             obj_id,
#             player_id,
#             team_id,
#             minutes_played,
#             claiming_goals_added_raw,
#             claiming_goals_added_above_avg,
#             claiming_count_actions,
#             fielding_goals_added_raw,
#             fielding_goals_added_above_avg,
#             fielding_count_actions,
#             handling_goals_added_raw,
#             handling_goals_added_above_avg,
#             handling_count_actions,
#             passing_goals_added_raw,
#             passing_goals_added_above_avg,
#             passing_count_actions,
#             shotstopping_goals_added_raw,
#             shotstopping_goals_added_above_avg,
#             shotstopping_count_actions,
#             sweeping_goals_added_raw,
#             sweeping_goals_added_above_avg,
#             sweeping_count_actions,
#             int(season)
#         ))
#         conn.commit()
#     cursor.close()
#     conn.close()

def get_goalkeeper_goals_added_by_season(player_id, season):
    print('Fetching goalkeeper xgoals for:{}, Season: {}'.format(player_id, season))
    obj_id = generate_player_season_id(player_id=player_id, season=str(season))
    conn = sqlite3.connect('data/nwsl.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    query = '''
        SELECT 
            gkga.*,
            pi.player_name,
            pi.player_first_name,
            pi.player_last_name,
            ti.team_name
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
    conn.commit()
    conn.close()
    print('Goalkeeper goals added returned.')
    return row

'''
INSERT GOALS ADDED DATA
'''
def insert_goalkeeper_goals_added_by_season(season):
    print(f'Inserting data for goalkeepers (goals added) for season: {season}')
    conn = sqlite3.connect('data/nwsl.db')

    stats_to_track = [
        'minutes_played',
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

    keepers_data = fetch_keeper_xgoal_data(season)
    filtered_players = calculate_player_statistics(keepers_data)
    position_data = aggregate_position_data(filtered_players, stats_to_track)
    insert_keeper_data(conn, keepers_data, position_data, stats_to_track, season)

    conn.close()
    print(f'Keeper goals added data for season {season} inserted successfully.')

def fetch_keeper_xgoal_data(season: int):
    """
    Fetch keeper data from the API for a specific season.

    Args:
        season (int): The season year.

    Returns:
        list: A list of keeper data dictionaries.
    """

    api_string = 'nwsl/goalkeepers/goals-added?season_name={}&stage_name=Regular Season'.format(str(season))
    keepers_data = make_asa_api_call(api_string)[1]

    # Filter out passed in positions and return
    return [keeper for keeper in keepers_data]

def calculate_player_statistics(keepers_data: list, minimum_minutes: int = 500):
    """
    Return a list of player statistics. This function is where any custome

    Args:
        keepers_data (list): List of keeper data dictionaries.
        minimum_minutes (int): minimum required minutes for statistics to be returned.

    Returns:
        list: Filtered list of player data dictionaries with calculated statistics.
    """
    return [player for player in keepers_data if player.get('minutes_played', 0) >= minimum_minutes]

def insert_keeper_data(conn, keepers_data, position_data, stats_to_track, season):
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

        if isinstance(team_id, list):
            team_id = team_id[-1]
        general_position = keeper.get('general_position', 'Unknown General Position')

        player_stats = {stat: round(keeper.get(stat, 0), 2) if isinstance(keeper.get(stat), (float, int)) else keeper.get(stat, 0)
                        for stat in stats_to_track}
        position_avg = {f"avg_{stat}": round(position_data.get(general_position, {}).get(f"avg_{stat}", 0), 2) for stat in stats_to_track}
        position_min = {f"min_{stat}": round(position_data.get(general_position, {}).get(f"min_{stat}", 0), 2) for stat in stats_to_track}
        position_max = {f"max_{stat}": round(position_data.get(general_position, {}).get(f"max_{stat}", 0), 2) for stat in stats_to_track}

        cursor.execute('''
            INSERT OR REPLACE INTO goalkeeper_goals_added (
                id,
                player_id,
                team_id,
                season,
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
                avg_minutes_played,
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
                min_minutes_played,
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
                max_minutes_played,
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
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            obj_id,
            player_id,
            team_id,
            int(season),
            player_stats['minutes_played'],
            player_stats['claiming_goals_added_raw'],
            player_stats['claiming_goals_added_above_avg'],
            player_stats['claiming_count_actions'],
            player_stats['fielding_goals_added_raw'],
            player_stats['fielding_goals_added_above_avg'],
            player_stats['fielding_count_actions'],
            player_stats['handling_goals_added_raw'],
            player_stats['handling_goals_added_above_avg'],
            player_stats['handling_count_actions'],
            player_stats['passing_goals_added_raw'],
            player_stats['passing_goals_added_above_avg'],
            player_stats['passing_count_actions'],
            player_stats['shotstopping_goals_added_raw'],
            player_stats['shotstopping_goals_added_above_avg'],
            player_stats['shotstopping_count_actions'],
            player_stats['sweeping_goals_added_raw'],
            player_stats['sweeping_goals_added_above_avg'],
            player_stats['sweeping_count_actions'],

            position_avg['avg_minutes_played'],
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

            position_min['min_minutes_played'],
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

            position_max['max_minutes_played'],
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