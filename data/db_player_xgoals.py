from api import make_asa_api_call
from .normalize import normalize_player_stats
from .player_xgoal_strength import calculate_player_xgoal_strength
import sqlite3
from collections import defaultdict

MINUTE_LIMIT = 180

def insert_player_xgoals_by_season(season):
    """
    Inserts player xGoal data into the database for a specific season, calculating 
    position-specific averages for players with sufficient minutes played.

    Args:
        season (int): The season year for which to insert player xGoal data.

    Functionality:
    - Fetches player data from the NWSL API.
    - Excludes goalkeepers and players with less than 200 minutes played for average calculations.
    - Calculates position-specific averages for stats such as minutes played, goals, xGoals, etc.
    - Inserts or updates player data into the 'player_xgoals' database table, including position-specific averages.
    """
def insert_player_xgoals_by_season(season):
    print(f'Inserting data for players (xgoal) for season: {season}')
    
    api_string = f'nwsl/players/xgoals?season_name={season}&stage_name=Regular Season'
    players_data = make_asa_api_call(api_string)[1]
    conn = sqlite3.connect('data/nwsl.db')
    cursor = conn.cursor()

    # Filter out goalkeepers
    players_data = [player for player in players_data if player.get('general_position') != 'GK']

    # Filter out players with less than 200 minutes played for averages
    filtered_for_averages = [player for player in players_data if player.get('minutes_played', 0) >= 200]

    # Group players by position and calculate sums and counts
    position_sums = defaultdict(lambda: defaultdict(float))
    position_counts = defaultdict(int)

    for player in filtered_for_averages:
        position = player.get('general_position', 'Unknown General Position')
        position_counts[position] += 1
        position_sums[position]['minutes_played'] += player.get('minutes_played', 0)
        position_sums[position]['shots'] += player.get('shots', 0)
        position_sums[position]['shots_on_target'] += player.get('shots_on_target', 0)
        position_sums[position]['shots_on_target_perc'] += int((player.get('shots_on_target', 0) / player.get('shots', 1)) * 100) if player.get('shots', 0) else 0
        position_sums[position]['goals'] += player.get('goals', 0)
        position_sums[position]['xgoals'] += player.get('xgoals', 0)
        position_sums[position]['xplace'] += player.get('xplace', 0)  # Aggregate xplace
        position_sums[position]['goals_minus_xgoals'] += player.get('goals_minus_xgoals', 0)  # Aggregate goals - xgoals
        position_sums[position]['primary_assists_minus_xassists'] += player.get('primary_assists_minus_xassists', 0)  # Aggregate primary_assists - xassists
        position_sums[position]['key_passes'] += player.get('key_passes', 0)
        position_sums[position]['primary_assists'] += player.get('primary_assists', 0)
        position_sums[position]['xassists'] += player.get('xassists', 0)
        position_sums[position]['xgoals_plus_xassists'] += player.get('xgoals_plus_xassists', 0)
        position_sums[position]['points_added'] += player.get('points_added', 0)
        position_sums[position]['xpoints_added'] += player.get('xpoints_added', 0)

    # Calculate averages for each position
    position_averages = {
        position: {f"avg_{key}": round(value / position_counts[position], 2) for key, value in sums.items()}
        for position, sums in position_sums.items()
    }

    # Insert data for each player
    for player in players_data:
        player_id = player.get('player_id', 'Unknown Player ID')
        obj_id = player_id + str(season)
        team_id = player.get('team_id', [])
        general_position = player.get('general_position', 'Unknown General Position')
        minutes_played = player.get('minutes_played', 0)
        shots = player.get('shots', 0)
        shots_on_target = player.get('shots_on_target', 0)
        shots_on_target_perc = int((shots_on_target / shots) * 100) if shots else 0
        goals = player.get('goals', 0)
        xgoals = round(player.get('xgoals', 0), 2)
        xplace = round(player.get('xplace', 0), 2)
        goals_minus_xgoals = round(player.get('goals_minus_xgoals', 0), 2)
        primary_assists_minus_xassists = round(player.get('primary_assists_minus_xassists', 0), 2)
        key_passes = player.get('key_passes', 0)
        primary_assists = player.get('primary_assists', 0)
        xassists = round(player.get('xassists', 0), 2)
        primary_assists_minus_xassists = round(player.get('primary_assists_minus_xassists', 0), 2)
        xgoals_plus_xassists = round(player.get('xgoals_plus_xassists', 0), 2)
        points_added = round(player.get('points_added', 0), 2)
        xpoints_added = round(player.get('xpoints_added', 0), 2)

        if isinstance(team_id, list):
            team_id = team_id[-1]

        # Get position-specific averages or set default values
        position_avg = position_averages.get(
            general_position, {f"avg_{key}": 0 for key in position_sums['Unknown General Position'].keys()}
        )

        cursor.execute('''
            INSERT OR REPLACE INTO player_xgoals (
                id, player_id, team_id, general_position, minutes_played, shots, 
                shots_on_target, shots_on_target_perc, goals, xgoals, xplace, goals_minus_xgoals, 
                key_passes, primary_assists, xassists, primary_assists_minus_xassists, 
                xgoals_plus_xassists, points_added, xpoints_added, season,
                avg_minutes_played, avg_shots, avg_shots_on_target, avg_shots_on_target_perc, avg_goals, avg_xgoals, 
                avg_xplace, avg_goals_minus_xgoals, avg_primary_assists_minus_xassists, avg_key_passes, 
                avg_primary_assists, avg_xassists, avg_xgoals_plus_xassists, avg_points_added, avg_xpoints_added
            ) VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            )
        ''', (
            obj_id, player_id, team_id, general_position, minutes_played, shots, shots_on_target, shots_on_target_perc,
            goals, xgoals, xplace, goals_minus_xgoals, key_passes, primary_assists, xassists,
            primary_assists_minus_xassists, xgoals_plus_xassists, points_added, xpoints_added, int(season),
            position_avg['avg_minutes_played'], position_avg['avg_shots'], position_avg['avg_shots_on_target'],
            position_avg['avg_shots_on_target_perc'], position_avg['avg_goals'], position_avg['avg_xgoals'],
            position_avg['avg_xplace'], position_avg['avg_goals_minus_xgoals'], position_avg['avg_primary_assists_minus_xassists'],
            position_avg['avg_key_passes'], position_avg['avg_primary_assists'], position_avg['avg_xassists'],
            position_avg['avg_xgoals_plus_xassists'], position_avg['avg_points_added'], position_avg['avg_xpoints_added']
        ))

    conn.commit()
    conn.close()
    print(f'Player xgoals data for season {season} inserted with position-specific averages, including avg_primary_assists_minus_xassists.')






def get_player_xgoals(player_id, season):
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

def get_all_player_xgoals(season):
    print('Fetching all players xgoals for season: {}'.format(season))
    conn = sqlite3.connect('data/nwsl.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    query = '''
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
                px.goals;
        '''
    cursor.execute(query, (season,))
    rows = cursor.fetchall()
    conn.commit()
    conn.close()
    print('All players xgoals returned.')
    return rows

def get_top_player_xgoals_stat(season, sorting_stat, limit):
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

# needs unit test
def player_xgoals_get_minutes_played_defender(season, sorting_stat, limit):
    """
    Retrieve the minutes played for defender (DF) players, sorted by a specified stat.

    This function queries the database to fetch player data for a given season, filtering
    only defenders (players with `primary_broad_position` of 'DF') and sorting the results
    based on the specified statistic. The results are limited to a specified number of players.

    Args:
        season (int): The season year to filter the data (e.g., 2023).
        sorting_stat (str): The player_xgoals column by which to sort the results 
                            (e.g., "minutes_played", "goals").
        limit (int): The maximum number of players to return in the result.

    Process:
        1. Establish a connection to the SQLite database and set the row factory.
        2. Execute an SQL query to:
            - Select data from `player_xgoals`, `player_info`, and `team_info`.
            - Filter by season and include only players with `primary_broad_position` of 'DF'.
            - Sort results by the specified stat in descending order.
            - Limit the results to the specified number of players.
        3. Fetch and return the results.

    Returns:
        list: A list of rows (SQLite Row objects) containing defender player data 
              that matches the query.

    Example Usage:
        rows = player_xgoals_get_minutes_played_defender(2023, "minutes_played", 10)

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

# needs unit test
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

    Process:
        1. Establish a connection to the SQLite database and set the row factory.
        2. Execute an SQL query to:
            - Select data from `player_xgoals`, `player_info`, and `team_info`.
            - Filter by season and exclude players with `primary_broad_position` of DF or GK.
            - Sort results by the specified stat in descending order.
            - Limit the results to the specified number of players.
        3. Fetch and return the results.

    Returns:
        list: A list of rows (SQLite Row objects) containing player data that matches the query.

    Example Usage:
        rows = player_xgoals_get_minutes_played_non_df(2023, "minutes_played", 10)
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

    Process:
        1. Establish a connection to the SQLite database.
        2. Execute an SQL query to calculate the minimum and maximum values for key stats.
        3. Map the query results to a dictionary using stat names as keys.
        4. Close the database connection and return the dictionary.

    Returns:
        dict: A dictionary containing the min and max values for each stat. 
              Format: { "stat_name": (min_value, max_value), ... }

    Example Output:
        {
            "minutes_played": (0, 3000),
            "shots": (0, 150),
            "goals": (0, 25),
            ...
        }
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
    Update the xGoals + xAssists per 90 metric for all players in the specified season.

    This function retrieves all player data for a given season from the database, calculates 
    the xGoals + xAssists per 90 metric for each player, and updates the player_xgoals table 
    with the calculated values. Players with fewer than MINUTE_LIMIT will have their 
    xGoals + xAssists per 90 metric set to 0.

    Args:
        season (int): The season year for which the xGoals + xAssists per 90 metric should be updated.
    
    Process:
        1. Fetch all player xgoals data for the specified season using the get_all_player_xgoals function.
        2. For each player:
            - Extract xGoals, xAssists, and minutes played.
            - Calculate xGoals + xAssists per 90 if the player has >= MINUTE_LIMIT.
        3. Update the player_xgoals table in the database with the calculated metric.
    
    Database Table:
        Updates the `player_xgoals` table, specifically the `xgoals_xassists_per_90` column.

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

        # Aggregate stats by position for averages
        if position not in position_stats:
            position_stats[position] = {'sum': 0, 'count': 0}
        position_stats[position]['sum'] += xgoals_xassists_per_90
        position_stats[position]['count'] += 1 if xgoals_xassists_per_90 > 0 else 0

     # Calculate averages by position and update the table
    for row in rows:
        player_stats = dict(row)
        position = player_stats.get('general_position', 'Unknown')

        if position in position_stats and position_stats[position]['count'] > 0:
            avg_xgoals_xassists_per_90 = round(
                position_stats[position]['sum'] / position_stats[position]['count'], 2
            )
        else:
            avg_xgoals_xassists_per_90 = 0

        # Update average stat for the player
        cursor.execute('''
            UPDATE player_xgoals
            SET avg_xgoals_xassists_per_90 = ?
            WHERE id = ?
        ''', (avg_xgoals_xassists_per_90, player_stats['id']))

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

    print(f'xGoals + xAssists per 90 updated for all players in season {season}.')

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
