from api import make_asa_api_call
from .normalize import normalize_player_stats
from .player_xgoal_strength import calculate_player_xgoal_strength
import sqlite3
from collections import defaultdict

MINUTE_LIMIT = 180

def insert_player_xgoals_by_season(season, conn=None):
    """
    Main function to fetch, process, and insert player xGoals data.

    Args:
        season (int): The season year.
        conn (sqlite3.Connection, optional): Database connection. Defaults to None.

    Returns:
        None
    """
    print(f'Inserting data for players (xgoal) for season: {season}')
    close_connection = False
    if conn is None:
        conn = sqlite3.connect('data/nwsl.db')
        close_connection = True

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

    if close_connection:
        conn.close()
    print(f'Player xgoals data for season {season} inserted successfully.')

def get_player_xgoal_data(player_id: str, season: int):
    """
    Fetches and returns player xGoals data for a specific player and season.

    Args:
        player_id (str): The unique identifier of the player.
        season (int): The season year.

    Returns:
        sqlite3.Row: A Row object containing xGoals data for the player, including 
                     related player information and team details.
    """
    print('Fetching player xgoals for:{}, Season: {}'.format(player_id, season))
    obj_id = player_id + str(season)
    conn = sqlite3.connect('data/nwsl.db')
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
    conn.commit()
    conn.close()
    print('Player xgoal returned.')
    return row

def get_all_player_xgoals(season: int, sorting_stat: str='goals', limit: int=None):
    """
    Retrieve all players' xGoals data for a specific season, ordered by a specified column, with an optional limit.

    This function queries the `player_xgoals` table to fetch player data for a given season, 
    along with related player and team information, sorted by the specified column, 
    and optionally limited to a specific number of rows.

    Args:
        season (int): The season year to filter the data (e.g., 2023).
        sorting_stat (str): The column by which to sort the results (default is 'goals').
        limit (int, optional): The maximum number of rows to return. Defaults to None (no limit).

    Returns:
        list[sqlite3.Row]: A list of rows containing player xGoals data for the specified season, ordered by the given column.
    """
    print('Fetching all players xgoals for season: {} sorted by {}'.format(season, sorting_stat))
    conn = sqlite3.connect('data/nwsl.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Use a parameterized query to prevent SQL injection
    query = f'''
        SELECT 
            px.*,
            pi.*,
            ti.team_name
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
            px.season = ?
        ORDER BY
            px.{sorting_stat};
    '''

    # Add LIMIT clause if limit is specified
    if limit is not None:
        query += f' LIMIT {limit}'
    
    cursor.execute(query, (season,))
    rows = cursor.fetchall()
    conn.commit()
    conn.close()
    print(f'All players xgoals sorted by {sorting_stat} returned.')
    return rows

def get_top_player_xgoals_stat(season, sorting_stat, limit):
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
    conn = sqlite3.connect('data/nwsl.db')
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
        LIMIT {limit};
    '''
    cursor.execute(query, (season,))
    rows = cursor.fetchall()
    conn.commit()
    conn.close()
    print('Top {} sorted by {} for: {} returned'.format(limit, sorting_stat, season))
    return rows

def player_xgoals_minimum_shots(season, sorting_stat, limit, minimum_shots):
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
    print('Players - Fetching {} shots on target% sorted by {} for: {}.'.format(limit, sorting_stat, season))
    conn = sqlite3.connect('data/nwsl.db')
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
    print('Top {} shots on target% sorted by {} for: {} returned'.format(limit, sorting_stat, season))
    return rows

def player_xgoals_get_minutes_played_defender(season, sorting_stat, limit):
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
    conn = sqlite3.connect('data/nwsl.db')
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

def player_xgoals_get_minutes_played_non_df(season, sorting_stat, limit):
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
    conn = sqlite3.connect('data/nwsl.db')
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

def get_stat_ranges():
    """
    Retrieve the minimum and maximum values for key player statistics from the database.

    This function queries the `player_xgoals` table to calculate the min and max values
    for various player stats. The results are returned as a dictionary with each stat's
    name as the key and a tuple of (min, max) values as the value.

    Args:
        None

    Returns:
        dict: A dictionary containing the min and max values for each stat. 
              Format: { "stat_name": (min_value, max_value), ... }
    """
    conn = sqlite3.connect('data/nwsl.db')
    cursor = conn.cursor()
    
    query = """
    SELECT 
        MIN(minutes_played), MAX(minutes_played),
        MIN(shots), MAX(shots),
        MIN(shots_on_target), MAX(shots_on_target),
        MIN(shots_on_target_perc), MAX(shots_on_target_perc),
        MIN(goals), MAX(goals),
        MIN(xgoals), MAX(xgoals),
        MIN(xplace), MAX(xplace),
        MIN(goals_minus_xgoals), MAX(goals_minus_xgoals),
        MIN(key_passes), MAX(key_passes),
        MIN(primary_assists), MAX(primary_assists),
        MIN(xassists), MAX(xassists),
        MIN(primary_assists_minus_xassists), MAX(primary_assists_minus_xassists),
        MIN(xgoals_plus_xassists), MAX(xgoals_plus_xassists),
        MIN(points_added), MAX(points_added),
        MIN(xpoints_added), MAX(xpoints_added)
    FROM player_xgoals;
    """
    
    cursor.execute(query)
    result = cursor.fetchone()
    
    stat_names = [
        "minutes_played", "shots", "shots_on_target", "shots_on_target_perc", 
        "goals", "xgoals", "xplace", "goals_minus_xgoals", 
        "key_passes", "primary_assists", "xassists", 
        "primary_assists_minus_xassists", "xgoals_plus_xassists", 
        "points_added", "xpoints_added"
    ]
    
    stat_ranges = {stat_names[i]: (result[i*2], result[i*2+1]) for i in range(len(stat_names))}
    
    conn.close()
    return stat_ranges

def update_xgoals_xassists_per_90(season):
    """
    Update the xGoals + xAssists per 90 metric for all players in the specified season, 
    calculating position-specific averages, maximums, and minimums.

    Args:
        season (int): The season year for which the xGoals + xAssists per 90 metric should be updated.
    
    Returns:
        None
    """
    print(f'Updating xGoals + xAssists per 90 for season: {season}')
    
    # Fetch all player xgoals data for the given season
    rows = get_all_player_xgoals(season)

    conn = sqlite3.connect('data/nwsl.db')
    cursor = conn.cursor()

    position_stats = {}

    for row in rows:
        # Convert row to a dictionary
        player_stats = dict(row)

        # Extract relevant stats
        position = player_stats.get('general_position', 'Unknown')
        xgoals = player_stats.get('xgoals', 0)
        xassists = player_stats.get('xassists', 0)
        minutes_played = player_stats.get('minutes_played', 0)

        # Calculate xGoals + xAssists per 90
        if minutes_played >= MINUTE_LIMIT:  # Minimum minutes threshold
            xgoals_xassists_per_90 = round(((xgoals + xassists) / minutes_played) * 90, 2)
        else:
            xgoals_xassists_per_90 = 0

        # Update the row in the database
        cursor.execute('''
            UPDATE player_xgoals
            SET xgoals_xassists_per_90 = ?
            WHERE id = ?
        ''', (xgoals_xassists_per_90, player_stats['id']))

        # Aggregate stats by position for averages, min, and max
        if position not in position_stats:
            position_stats[position] = {'sum': 0, 'count': 0, 'max': float('-inf'), 'min': float('inf')}
        position_stats[position]['sum'] += xgoals_xassists_per_90
        if xgoals_xassists_per_90 > 0:
            position_stats[position]['count'] += 1
            position_stats[position]['max'] = max(position_stats[position]['max'], xgoals_xassists_per_90)
            position_stats[position]['min'] = min(position_stats[position]['min'], xgoals_xassists_per_90)

    # Update averages, min, and max for each player
    for row in rows:
        player_stats = dict(row)
        position = player_stats.get('general_position', 'Unknown')

        if position in position_stats and position_stats[position]['count'] > 0:
            avg_xgoals_xassists_per_90 = round(
                position_stats[position]['sum'] / position_stats[position]['count'], 2
            )
            max_xgoals_xassists_per_90 = position_stats[position]['max']
            min_xgoals_xassists_per_90 = position_stats[position]['min']
        else:
            avg_xgoals_xassists_per_90 = 0
            max_xgoals_xassists_per_90 = 0
            min_xgoals_xassists_per_90 = 0

        # Update the average, max, and min stats for the player
        cursor.execute('''
            UPDATE player_xgoals
            SET avg_xgoals_xassists_per_90 = ?, max_xgoals_xassists_per_90 = ?, min_xgoals_xassists_per_90 = ?
            WHERE id = ?
        ''', (avg_xgoals_xassists_per_90, max_xgoals_xassists_per_90, min_xgoals_xassists_per_90, player_stats['id']))

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

    print(f'xGoals + xAssists per 90 updated for all players in season {season}, including position-specific averages, mins, and maxes.')

def get_player_xgoals_ids_by_season(season):
    """
    Fetch all player xgoals IDs for a specific season.

    Args:
        season (int): The season year to filter by.

    Returns:
        list: A list of IDs from the player_xgoals table for the specified season.
    """
    print(f"Fetching all player xgoals IDs for season: {season}")
    conn = sqlite3.connect('data/nwsl.db')
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

# unit test done
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

# unit test done
def calculate_player_statistics(players_data: list, minimum_minutes: int = 180):
    """
    Calculate `shots_on_target_perc` and filter players by minutes played.

    Args:
        players_data (list): List of player data dictionaries.
        minimum_minutes (int): minimum required minutes for statistics to be returned.

    Returns:
        list: Filtered list of player data dictionaries with calculated statistics.
    """
    for player in players_data:
        shots = player.get('shots', 0)
        shots_on_target = player.get('shots_on_target', 0)
        player['shots_on_target_perc'] = (shots_on_target / shots) * 100 if shots > 0 else 0

    # Filter players with minutes >= the minimum
    return [player for player in players_data if player.get('minutes_played', 0) >= minimum_minutes]

# unit test done
def aggregate_position_data(filtered_players, stats_to_track):
    """
    Calculate averages, minimums, and maximums for players grouped by position.

    Args:
        filtered_players (list): Filtered list of player data dictionaries.
        stats_to_track (list): List of stats to calculate.

    Returns:
        dict: Aggregated position data with averages, mins, and maxs.
    """
    position_sums = defaultdict(lambda: defaultdict(float))
    position_counts = defaultdict(int)
    position_mins = defaultdict(lambda: {stat: float('inf') for stat in stats_to_track})
    position_maxs = defaultdict(lambda: {stat: float('-inf') for stat in stats_to_track})

    for player in filtered_players:
        position = player.get('general_position', 'Unknown General Position')
        position_counts[position] += 1

        for stat in stats_to_track:
            value = player.get(stat, 0)
            position_sums[position][stat] += value
            position_mins[position][stat] = min(position_mins[position][stat], value)
            position_maxs[position][stat] = max(position_maxs[position][stat], value)

    return {
        position: {
            **{f"avg_{stat}": round(position_sums[position][stat] / position_counts[position], 2)
               if position_counts[position] > 0 else 0 for stat in stats_to_track},
            **{f"min_{stat}": position_mins[position][stat] for stat in stats_to_track},
            **{f"max_{stat}": position_maxs[position][stat] for stat in stats_to_track}
        }
        for position in position_sums.keys()
    }

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
        obj_id = player_id + str(season)
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
        
        # Calculate Shot on Target% (not included in api)
        player_stats['shots_on_target_perc'] = round((player['shots_on_target'] / player['shots']) * 100 if player['shots'] > 10 else 0, 2)

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