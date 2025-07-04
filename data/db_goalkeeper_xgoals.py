from api import make_asa_api_call
from .data_util import aggregate_position_data, generate_player_season_id, MINIMUM_MINUTES, get_db_path, validate_id
import sqlite3

def get_all_goalkeepers_xgoals_by_season(season):
    print('Fetching all goalkeepers xgoals for season: {}'.format(season))
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    query = '''
        SELECT 
            gx.*,
            pi.*,
            ti.*
            FROM 
                goalkeeper_xgoals AS gx
            JOIN 
                player_info AS pi
            ON 
                gx.player_id = pi.player_id
            JOIN
                team_info AS ti
            ON
                gx.team_id = ti.team_id   
            WHERE
                gx.season = ?
            ORDER BY
                gx.saves;
        '''
    cursor.execute(query, (season,))
    rows = cursor.fetchall()
    if len(rows) == 0:
        print(f"WARNING: No goalkeeper data found for all players. Season={season}.") # pragma: no cover
    conn.commit()
    conn.close()
    print('All goalkeepers returned with xgoal data.')
    return rows

def get_goalkeeper_xgoals_by_season(player_id, season):
    print('Fetching goalkeeper xgoals for {} season: {}'.format(player_id, season))
    obj_id = generate_player_season_id(player_id=player_id, season=str(season))
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    obj_id = generate_player_season_id(player_id=player_id, season=str(season))
    query = f'''
        SELECT 
            gx.*,
            pi.*,
            ti.*
            FROM 
                goalkeeper_xgoals AS gx
            JOIN 
                player_info AS pi
            ON 
                gx.player_id = pi.player_id
            JOIN
                team_info AS ti
            ON
                gx.team_id = ti.team_id   
            WHERE
                gx.id = ?;
        '''
    cursor.execute(query, (obj_id,))
    row = cursor.fetchone()
    if row is None:
        print(f"WARNING: No goalkeeper data found for player_id={player_id} Season= ={season}.") # pragma: no cover
    conn.commit()
    conn.close()
    print('Goalkeeper returned with xgoal data.')
    return row

'''
INSERT XGOALS DATA
'''
def insert_goalkeeper_xgoals_by_season(season): # pragma: no cover
    print(f'Inserting data for goalkeepers (xgoal) for season: {season}')
    conn = sqlite3.connect(get_db_path())

    stats_to_track = [
    'minutes_played', 'shots_faced', 'goals_conceded', 'saves', 'share_headed_shots',
    'xgoals_gk_faced', 'goals_minus_xgoals_gk', 'goals_divided_by_xgoals_gk', 'save_perc'
    ]

    keepers_data = fetch_keeper_xgoal_data(season)
    filtered_players = calculate_player_statistics(keepers_data)
    position_data = aggregate_position_data(filtered_players, stats_to_track)
    insert_keeper_data(conn, keepers_data, position_data, stats_to_track, season)

    conn.close()
    print(f'Keeper xgoals data for season {season} inserted successfully.')

def fetch_keeper_xgoal_data(season: int):
    """
    Fetch keeper data from the API for a specific season.

    Args:
        season (int): The season year.

    Returns:
        list: A list of keeper data dictionaries.
    """

    api_string = 'nwsl/goalkeepers/xgoals?season_name={}&stage_name=Regular Season'.format(str(season))
    keepers_data = make_asa_api_call(api_string)[1]

    return [keeper for keeper in keepers_data]

def calculate_player_statistics(keepers_data: list):
    """
    Return a list of player statistics. Any custom filtering should be done in this function.

    Args:
        keepers_data (list): List of keeper data dictionaries.

    Returns:
        list: Filtered list of player data dictionaries with calculated statistics.
    """
    for keeper in keepers_data:
        saves = keeper.get('saves', 0)
        shots_faced = keeper.get('shots_faced', 0)
        keeper['save_perc'] = (saves / shots_faced) * 100 if shots_faced > 0 else 0

    data = [player for player in keepers_data if player.get('minutes_played', 0) >= MINIMUM_MINUTES]
    if len(data) == 0:
        print('WARNING: No data returned in calculate player statistics goalkeeper xgoals.') # pragma: no cover
    return data

def insert_keeper_data(conn, keepers_data, position_data, stats_to_track, season): # pragma: no cover
    """
    Insert keeper data into the database, rounding all REAL values to two decimal places.

    Args:
        conn (sqlite3.Connection): Database connection.
        keepers_data (list): List of keeper data dictionaries.
        position_data (dict): Aggregated position data.
        stats_to_track (list): List of stats to track for avg, min, and max.
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
            INSERT OR REPLACE INTO goalkeeper_xgoals (
                id, player_id, team_id, season, minutes_played, shots_faced, goals_conceded, 
                saves, share_headed_shots, xgoals_gk_faced, goals_minus_xgoals_gk,
                goals_divided_by_xgoals_gk,
                avg_minutes_played, avg_shots_faced, avg_goals_conceded, avg_saves, avg_share_headed_shots, 
                avg_xgoals_gk_faced, avg_goals_minus_xgoals_gk, avg_goals_divided_by_xgoals_gk,
                min_minutes_played, min_shots_faced, min_goals_conceded, min_saves, min_share_headed_shots, 
                min_xgoals_gk_faced, min_goals_minus_xgoals_gk, min_goals_divided_by_xgoals_gk,
                max_minutes_played, max_shots_faced, max_goals_conceded, max_saves, max_share_headed_shots, 
                max_xgoals_gk_faced, max_goals_minus_xgoals_gk, max_goals_divided_by_xgoals_gk,
                save_perc, avg_save_perc, min_save_perc, max_save_perc
            ) VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?, ?, ?, ?,
                ?, ?, ?, ?
            )
        ''', (
            obj_id,
            player_id,
            team_id,
            int(season),
            player_stats['minutes_played'],
            player_stats['shots_faced'],
            player_stats['goals_conceded'],
            player_stats['saves'],
            player_stats['share_headed_shots'],
            player_stats['xgoals_gk_faced'],
            player_stats['goals_minus_xgoals_gk'],
            player_stats['goals_divided_by_xgoals_gk'],

            position_avg['avg_minutes_played'],
            position_avg['avg_shots_faced'],
            position_avg['avg_goals_conceded'],
            position_avg['avg_saves'],
            position_avg['avg_share_headed_shots'],
            position_avg['avg_xgoals_gk_faced'],
            position_avg['avg_goals_minus_xgoals_gk'],
            position_avg['avg_goals_divided_by_xgoals_gk'],

            position_min['min_minutes_played'],
            position_min['min_shots_faced'],
            position_min['min_goals_conceded'],
            position_min['min_saves'],
            position_min['min_share_headed_shots'],
            position_min['min_xgoals_gk_faced'],
            position_min['min_goals_minus_xgoals_gk'],
            position_min['min_goals_divided_by_xgoals_gk'],

            position_max['max_minutes_played'],
            position_max['max_shots_faced'],
            position_max['max_goals_conceded'],
            position_max['max_saves'],
            position_max['max_share_headed_shots'],
            position_max['max_xgoals_gk_faced'],
            position_max['max_goals_minus_xgoals_gk'],
            position_max['max_goals_divided_by_xgoals_gk'],

            player_stats['save_perc'],
            position_avg['avg_save_perc'],
            position_min['min_save_perc'],
            position_max['max_save_perc']
            ))
        
    conn.commit()

def get_goalkeepers_for_team(team_id, season, limit = 1):
    """
    Retrieves the goalkeeper(s) with the most minutes played for a given team and season.

    Args:
        team_id (str): The unique identifier for the team.
        season (int): The season to filter on.
        limit (int, optional): The number of top goalkeepers to retrieve, ordered by minutes played. Defaults to 1.

    Returns:
        sqlite3.Row or list[sqlite3.Row] or None: 
            - A single goalkeeper record if limit == 1.
            - A list of goalkeeper records if limit > 1.
            - None if no data exists for the given team and season.
    """
    validate_id(team_id)
    print(f'Fetching primary goalkeeper for team {team_id} in season {season}...')

    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute('''
        SELECT
            gk.*,
            pi.*
        FROM 
            goalkeeper_xgoals AS gk
        JOIN 
            player_info AS pi
            ON gk.player_id = pi.player_id
        WHERE 
            gk.team_id = ?
            AND gk.season = ?
        ORDER BY 
            gk.minutes_played DESC
        LIMIT ?
    ''', (team_id, season, limit))

    if limit <= 1:
        row = cursor.fetchone()
        conn.close()
        return row
    else:
        rows = cursor.fetchall()
        conn.close()
        return rows
