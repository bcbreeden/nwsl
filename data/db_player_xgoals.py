from api import make_asa_api_call
from .data_util import aggregate_position_data, generate_player_season_id, MINIMUM_MINUTES, get_db_path
import sqlite3

def get_all_player_xgoal_by_team(team_id: str, season: int):
    """
    Fetches and returns xGoals data for all players on a given team for a specific season.

    Args:
        team_id (str): The unique identifier of the team.
        season (int): The season year.

    Returns:
        list[sqlite3.Row]: A list of Row objects, each containing xGoals data for a player,
                           including related player information and team details.

    Raises:
        ValueError: If no data is found for the given team and season.
    """
    print(f'Fetching all player xGoals for team_id={team_id}, season={season}')
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    query = '''
        SELECT 
            px.*,
            pi.*,
            ti.team_name,
            ti.team_abbreviation
        FROM 
            player_xgoals AS px
        JOIN 
            player_info AS pi
            ON px.player_id = pi.player_id
        JOIN
            team_info AS ti
            ON px.team_id = ti.team_id   
        WHERE
            px.team_id = ? AND px.season = ?
        ORDER BY 
            px.player_strength DESC;
    '''

    cursor.execute(query, (team_id, season))
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        raise ValueError(f"No player xGoal data found for team_id={team_id} and season={season}")

    print(f'Returned {len(rows)} player xGoal entries.')
    return rows

def get_player_xgoal_data_all_seasons(player_id: str):
    """
    Fetches and returns player xGoals data for all seasons.

    Args:
        player_id (str): The unique identifier of the player.

    Returns:
        sqlite3.Row: A Row object containing xGoals data for the player, including 
                     related player information and team details.

    Raises:
        PlayerDataNotFoundError: If no data is found for the given player and season.
    """
    print('Fetching player xgoals for:{}, All Seasons'.format(player_id))
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    query = '''
        SELECT 
            px.*,
            pi.*,
            ti.team_name,
            ti.team_abbreviation
            FROM 
                player_xgoals AS px
            JOIN 
                player_info AS pi
            ON 
                px.player_id = pi.player_id
            JOIN
                team_info AS ti
            ON
                px.team_id = ti.team_id
            WHERE
                px.player_id = ?
            ORDER BY
                px.season DESC;
        '''
    cursor.execute(query, (player_id,))
    row = cursor.fetchall()
    if row is None:
        print(f"No player xgoal data found for player_id={player_id} all seasons.")
    conn.commit()
    conn.close()
    print('Player xgoal returned for all seasons.')
    return row

def get_player_xgoal_data(player_id: str, season: int):
    """
    Fetches and returns player xGoals data for a specific player and season.

    Args:
        player_id (str): The unique identifier of the player.
        season (int): The season year.

    Returns:
        sqlite3.Row: A Row object containing xGoals data for the player, including 
                     related player information and team details.

    Raises:
        PlayerDataNotFoundError: If no data is found for the given player and season.
    """
    print('Fetching player xgoals for:{}, Season: {}'.format(player_id, season))
    obj_id = generate_player_season_id(player_id=player_id, season=str(season))
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    query = '''
        SELECT 
            px.*,
            pi.*,
            ti.team_name,
            ti.team_abbreviation
            FROM 
                player_xgoals AS px
            JOIN 
                player_info AS pi
            ON 
                px.player_id = pi.player_id
            JOIN
                team_info AS ti
            ON
                px.team_id = ti.team_id   
            WHERE
                px.id = ?;
        '''
    cursor.execute(query, (obj_id,))
    row = cursor.fetchone()
    if row is None:
        print(f"WARNING: No player xgoal data found for player_id={player_id} and season={season}")
    conn.commit()
    conn.close()
    print('Player xgoal returned.')
    return row

def get_top_player_xgoals_stat(season, sorting_stat: str='goals', limit: int=None):
    """
    Retrieve the top players' xGoals data for a given season, sorted by a specific statistic.

    This function queries the `player_xgoals` table to fetch player data for a specified season, 
    sorting the results by the given statistic and limiting the number of returned rows.

    Args:
        season (int): The season year to filter the data (e.g., 2023).
        sorting_stat (str): The column from `player_xgoals` to sort the results by (e.g., "goals", "xgoals").
        limit (int): The maximum number of players to return.

    Returns:
        list[sqlite3.Row]: A list of rows containing player data, sorted and limited as specified.
    """
    print('Players - Fetching top {} sorted by {} for: {}.'.format(limit, sorting_stat, season))
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    query = f'''
        SELECT 
            px.*,
            pi.*,
            ti.*
        FROM 
            player_xgoals AS px
        JOIN 
            player_info AS pi
        ON 
            px.player_id = pi.player_id
        JOIN
            team_info AS ti
        ON
            px.team_id  = ti.team_id
        WHERE
            px.season = ?
        ORDER BY
            px.{sorting_stat} DESC
    '''
    # Add LIMIT clause if limit is specified
    if limit is not None:
        query += f' LIMIT {limit};'
    else:
        query += f';'

    cursor.execute(query, (season,))
    rows = cursor.fetchall()
    conn.commit()
    conn.close()
    print('Top {} sorted by {} for: {} returned'.format(limit, sorting_stat, season))
    return rows

def get_player_xgoals_minimum_shots(season, sorting_stat, limit, minimum_shots):
    """
    Retrieve player data for a given season, filtered by a minimum number of shots 
    and sorted by a specified stat.

    Args:
        season (int): The season year to filter the data (e.g., 2023).
        sorting_stat (str): The player_xgoals column to sort results by (e.g., "shots_on_target_perc").
        limit (int): The maximum number of players to return.
        minimum_shots (int): The minimum number of shots required for a player to be included.

    Returns:
        list[sqlite3.Row]: A list of rows containing player data, limited, filtered, and sorted as specified.
    """
    print('Players - Fetching {} player xgoals sorted by {} for: {} season.'.format(limit, sorting_stat, season))
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    query = f'''
        SELECT 
            px.*,
            pi.*,
            ti.*
        FROM 
            player_xgoals AS px
        JOIN 
            player_info AS pi
        ON 
            px.player_id = pi.player_id
        JOIN
            team_info AS ti
        ON
            px.team_id  = ti.team_id
        WHERE
            px.season = ?
            AND px.shots > {minimum_shots}
        ORDER BY
            px.{sorting_stat} DESC
        LIMIT {limit};
    '''
    cursor.execute(query, (season,))
    rows = cursor.fetchall()
    conn.commit()
    conn.close()
    print('Top {} player xgoals sorted by {} for: {} season returned'.format(limit, sorting_stat, season))
    return rows

def get_defender_minutes_played(season, sorting_stat, limit):
    """
    Retrieve minutes played for defenders in a given season, sorted by a specified stat.

    Args:
        season (int): The season year to filter the data (e.g., 2023).
        sorting_stat (str): The player_xgoals column to sort results by (e.g., "minutes_played", "goals").
        limit (int): The maximum number of players to return.

    Returns:
        list[sqlite3.Row]: A list of rows containing player data, limited and sorted as specified.
    """
    print('Players - Fetching {} minutes played sorted by {} for: {}.'.format(limit, sorting_stat, season))
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    query = f'''
        SELECT 
            px.*,
            pi.*,
            ti.*
        FROM 
            player_xgoals AS px
        JOIN 
            player_info AS pi
        ON 
            px.player_id = pi.player_id
        JOIN
            team_info AS ti
        ON
            px.team_id  = ti.team_id
        WHERE
            px.season = ?
            AND pi.primary_broad_position == 'DF'
        ORDER BY
            px.{sorting_stat} DESC
        LIMIT {limit};
    '''
    cursor.execute(query, (season,))
    rows = cursor.fetchall()
    conn.commit()
    conn.close()
    print('Top {} minutes played sorted by {} for: {} returned'.format(limit, sorting_stat, season))
    return rows

def get_minutes_played_non_df(season, sorting_stat, limit):
    """
    Retrieve the minutes played for players who are not defenders (DF) or goalkeepers (GK),
    sorted by a specified stat.

    This function queries the database to fetch player data for a given season, excluding
    defenders and goalkeepers, and sorts the results based on the specified statistic. 
    The results are limited to a specified number of players.

    Args:
        season (int): The season year to filter the data (e.g., 2023).
        sorting_stat (str): The player_xgoals column by which to sort the results 
                            (e.g., "minutes_played", "goals").
        limit (int): The maximum number of players to return in the result.

    Returns:
        list: A list of rows (SQLite Row objects) containing player data that matches the query.
    """
    print('Players - Fetching {} minutes played sorted by {} for: {}.'.format(limit, sorting_stat, season))
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    query = f'''
        SELECT 
            px.*,
            pi.*,
            ti.*
        FROM 
            player_xgoals AS px
        JOIN 
            player_info AS pi
        ON 
            px.player_id = pi.player_id
        JOIN
            team_info AS ti
        ON
            px.team_id  = ti.team_id
        WHERE
            px.season = ?
            AND pi.primary_broad_position != 'DF'
            AND pi.primary_broad_position != 'GK'
        ORDER BY
            px.{sorting_stat} DESC
        LIMIT {limit};
    '''
    cursor.execute(query, (season,))
    rows = cursor.fetchall()
    conn.commit()
    conn.close()
    print('Top {} minutes played sorted by {} for: {} returned'.format(limit, sorting_stat, season))
    return rows

def get_player_xgoals_ids_by_season(season):
    """
    Fetch all player xgoals IDs for a specific season.

    Args:
        season (int): The season year to filter by.

    Returns:
        list: A list of IDs from the player_xgoals table for the specified season.
    """
    print(f"Fetching all player xgoals IDs for season: {season}")
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = lambda cursor, row: row[0]  # Return only the first column (id)
    cursor = conn.cursor()
    
    query = '''
        SELECT player_id
        FROM player_xgoals
        WHERE season = ?;
    '''
    cursor.execute(query, (season,))
    ids = cursor.fetchall()
    
    conn.close()
    print(f"Retrieved {len(ids)} IDs for season {season}.")
    return ids

'''
======================
   Insert xGoals Data
======================
'''
def insert_player_xgoals_by_season(season):
    """
    Main function to fetch, process, and insert player xGoals data.

    Args:
        season (int): The season year.

    Returns:
        None
    """
    print(f'Inserting data for players (xgoal) for season: {season}')
    conn = sqlite3.connect(get_db_path())

    stats_to_track = [
    'minutes_played', 'shots', 'shots_on_target', 'shots_on_target_perc', 'goals',
    'xgoals', 'xplace', 'goals_minus_xgoals', 'primary_assists_minus_xassists',
    'key_passes', 'primary_assists', 'xassists', 'xgoals_plus_xassists',
    'points_added', 'xpoints_added'
    ]

    players_data = fetch_players_xgoal_data(season, excluded_positions=['GK'])
    filtered_players = calculate_player_statistics(players_data)
    position_data = aggregate_position_data(filtered_players, stats_to_track)
    insert_player_data(conn, players_data, position_data, stats_to_track, season)

    conn.close()
    print(f'Player xgoals data for season {season} inserted successfully.')

def fetch_players_xgoal_data(season: int, excluded_positions: list = None):
    """
    Fetch player data from the API for a specific season.

    Args:
        season (int): The season year.
        excluded_positions (list): A list of general positions to be excluded.

    Returns:
        list: A list of player data dictionaries.
    """
    if excluded_positions is None:
        excluded_positions = ['']

    api_string = f'nwsl/players/xgoals?season_name={season}&stage_name=Regular Season'
    players_data = make_asa_api_call(api_string)[1]

    # Filter out passed in positions and return
    return [player for player in players_data if player.get('general_position') not in excluded_positions]

def calculate_player_statistics(players_data: list):
    """
    Calculate `shots_on_target_perc` and filter players by minutes played.

    Args:
        players_data (list): List of player data dictionaries.

    Returns:
        list: Filtered list of player data dictionaries with calculated statistics.
    """
    for player in players_data:
        shots = player.get('shots', 0)
        shots_on_target = player.get('shots_on_target', 0)
        player['shots_on_target_perc'] = (shots_on_target / shots) * 100 if shots > 0 else 0

    # Filter players with minutes >= the minimum
    return [player for player in players_data if player.get('minutes_played', 0) >= MINIMUM_MINUTES]

def insert_player_data(conn, players_data, position_data, stats_to_track, season):
    """
    Insert player data into the database, rounding all REAL values to two decimal places.

    Args:
        conn (sqlite3.Connection): Database connection.
        players_data (list): List of player data dictionaries.
        position_data (dict): Aggregated position data.
        stats_to_track (list): List of stats to track.
        season (int): The season year.
    """
    cursor = conn.cursor()

    for player in players_data:
        player_id = player.get('player_id', 'Unknown Player ID')
        obj_id = generate_player_season_id(player_id=player_id, season=str(season))
        team_id = player.get('team_id', [])
        if isinstance(team_id, list):
            team_id = team_id[-1]
        general_position = player.get('general_position', 'Unknown General Position')

        # Prepare player stats and round values
        player_stats = {stat: round(player.get(stat, 0), 2) if isinstance(player.get(stat), (float, int)) else player.get(stat, 0)
                        for stat in stats_to_track}
        position_avg = {f"avg_{stat}": round(position_data.get(general_position, {}).get(f"avg_{stat}", 0), 2) for stat in stats_to_track}
        position_min = {f"min_{stat}": round(position_data.get(general_position, {}).get(f"min_{stat}", 0), 2) for stat in stats_to_track}
        position_max = {f"max_{stat}": round(position_data.get(general_position, {}).get(f"max_{stat}", 0), 2) for stat in stats_to_track}

        cursor.execute('''
            INSERT OR REPLACE INTO player_xgoals (
                id, player_id, team_id, general_position, season,
                minutes_played, shots, shots_on_target, shots_on_target_perc, goals,
                xgoals, xplace, goals_minus_xgoals, primary_assists_minus_xassists,
                key_passes, primary_assists, xassists, xgoals_plus_xassists,
                points_added, xpoints_added,
                avg_minutes_played, avg_shots, avg_shots_on_target, avg_shots_on_target_perc, avg_goals, avg_xgoals,
                avg_xplace, avg_goals_minus_xgoals, avg_primary_assists_minus_xassists, avg_key_passes,
                avg_primary_assists, avg_xassists, avg_xgoals_plus_xassists, avg_points_added, avg_xpoints_added,
                min_minutes_played, min_shots, min_shots_on_target, min_shots_on_target_perc, min_goals, min_xgoals,
                min_xplace, min_goals_minus_xgoals, min_primary_assists_minus_xassists, min_key_passes,
                min_primary_assists, min_xassists, min_xgoals_plus_xassists, min_points_added, min_xpoints_added,
                max_minutes_played, max_shots, max_shots_on_target, max_shots_on_target_perc, max_goals, max_xgoals,
                max_xplace, max_goals_minus_xgoals, max_primary_assists_minus_xassists, max_key_passes,
                max_primary_assists, max_xassists, max_xgoals_plus_xassists, max_points_added, max_xpoints_added
            ) VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            )
        ''', (
            obj_id, player_id, team_id, general_position, int(season),
            player_stats['minutes_played'], player_stats['shots'], player_stats['shots_on_target'],
            player_stats['shots_on_target_perc'], player_stats['goals'], player_stats['xgoals'], player_stats['xplace'],
            player_stats['goals_minus_xgoals'], player_stats['primary_assists_minus_xassists'], player_stats['key_passes'],
            player_stats['primary_assists'], player_stats['xassists'], player_stats['xgoals_plus_xassists'],
            player_stats['points_added'], player_stats['xpoints_added'],
            position_avg['avg_minutes_played'], position_avg['avg_shots'], position_avg['avg_shots_on_target'],
            position_avg['avg_shots_on_target_perc'], position_avg['avg_goals'], position_avg['avg_xgoals'],
            position_avg['avg_xplace'], position_avg['avg_goals_minus_xgoals'],
            position_avg['avg_primary_assists_minus_xassists'], position_avg['avg_key_passes'],
            position_avg['avg_primary_assists'], position_avg['avg_xassists'],
            position_avg['avg_xgoals_plus_xassists'], position_avg['avg_points_added'], position_avg['avg_xpoints_added'],
            position_min['min_minutes_played'], position_min['min_shots'], position_min['min_shots_on_target'],
            position_min['min_shots_on_target_perc'], position_min['min_goals'], position_min['min_xgoals'],
            position_min['min_xplace'], position_min['min_goals_minus_xgoals'],
            position_min['min_primary_assists_minus_xassists'], position_min['min_key_passes'],
            position_min['min_primary_assists'], position_min['min_xassists'],
            position_min['min_xgoals_plus_xassists'], position_min['min_points_added'], position_min['min_xpoints_added'],
            position_max['max_minutes_played'], position_max['max_shots'], position_max['max_shots_on_target'],
            position_max['max_shots_on_target_perc'], position_max['max_goals'], position_max['max_xgoals'],
            position_max['max_xplace'], position_max['max_goals_minus_xgoals'],
            position_max['max_primary_assists_minus_xassists'], position_max['max_key_passes'],
            position_max['max_primary_assists'], position_max['max_xassists'],
            position_max['max_xgoals_plus_xassists'], position_max['max_points_added'], position_max['max_xpoints_added']
        ))

    conn.commit()

'''
XGOALS || XASSISTS PER 90   
'''
def calculate_and_update_xgxa90(season):
    """
    Calculate xGoals + xAssists per 90 and update the database for each player.
    """
    rows = get_top_player_xgoals_stat(season)
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    for row in rows:
        player_stats = dict(row)
        xgoals = player_stats.get('xgoals', 0)
        xassists = player_stats.get('xassists', 0)
        minutes_played = player_stats.get('minutes_played', 0)

        if minutes_played >= MINIMUM_MINUTES:
            xgoals_xassists_per_90 = round(((xgoals + xassists) / minutes_played) * 90, 2)
        else:
            xgoals_xassists_per_90 = 0

        cursor.execute('''
            UPDATE player_xgoals
            SET xgoals_xassists_per_90 = ?
            WHERE id = ?
        ''', (xgoals_xassists_per_90, player_stats['id']))
    conn.commit()
    conn.close()


def update_position_aggregates(rows, position_data):
    """
    Update position-specific averages, minimums, and maximums in the database.
    """
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    for row in rows:
        player_stats = dict(row)
        position = player_stats.get('general_position', 'Unknown General Position')

        avg = position_data[position].get(f"avg_xgoals_xassists_per_90", 0)
        max_ = position_data[position].get(f"max_xgoals_xassists_per_90", 0)
        min_ = position_data[position].get(f"min_xgoals_xassists_per_90", 0)

        cursor.execute('''
            UPDATE player_xgoals
            SET avg_xgoals_xassists_per_90 = ?, max_xgoals_xassists_per_90 = ?, min_xgoals_xassists_per_90 = ?
            WHERE id = ?
        ''', (avg, max_, min_, player_stats['id']))
    
    conn.commit()
    conn.close()

def update_xgoals_xassists_per_90(season):
    """
    Update the xGoals + xAssists per 90 metric and aggregated position stats for a given season.
    """
    print(f'Updating xGoals + xAssists per 90 for season: {season}')
    calculate_and_update_xgxa90(season)

    # Aggregate position stats based on updated data
    rows = get_top_player_xgoals_stat(season)
    stats_to_track = ['xgoals_xassists_per_90']
    filtered_players = [dict(row) for row in rows]
    position_data = aggregate_position_data(filtered_players, stats_to_track)

    # Update database with aggregated stats
    update_position_aggregates(rows, position_data)
    print(f'xGoals + xAssists per 90 updated for season {season}.')