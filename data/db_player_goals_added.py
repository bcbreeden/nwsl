from api import make_asa_api_call
import sqlite3
from .data_util import aggregate_position_data, generate_player_season_id, MINIMUM_MINUTES, get_db_path

def insert_player_goals_added_by_season(season, conn=None): # pragma: no cover
    """
    Inserts player goals added data for a given season into the database, excluding goalkeepers.

    Args:
        season (int or str): The season year to process (e.g., '2024').
        conn (sqlite3.Connection, optional): An existing SQLite connection. If None, a new
            connection will be created and closed within the function.

    Behavior:
        - Fetches raw player goals added data for the given season.
        - Filters and calculates per-player statistics.
        - Computes average, min, and max values for each tracked stat by position.
        - Inserts enriched player-level goals added data into the `player_goals_added` table,
          including normalization fields for contextual comparison.
        - Uses INSERT OR REPLACE to ensure up-to-date entries per player-season.

    Returns:
        None
    """
    print(f'Inserting data for players (goals added) for season: {season}')
    close_connection = False
    if conn is None:
        conn = sqlite3.connect(get_db_path())
        close_connection = True

    stats_to_track = [
        'dribbling_goals_added_raw',
        'dribbling_goals_added_above_avg',
        'dribbling_count_actions',

        'fouling_goals_added_raw',
        'fouling_goals_added_above_avg',
        'fouling_count_actions',

        'interrupting_goals_added_raw',
        'interrupting_goals_added_above_avg',
        'interrupting_count_actions',

        'passing_goals_added_raw',
        'passing_goals_added_above_avg',
        'passing_count_actions',

        'receiving_goals_added_raw',
        'receiving_goals_added_above_avg',
        'receiving_count_actions',

        'shooting_goals_added_raw',
        'shooting_goals_added_above_avg',
        'shooting_count_actions',
    ]

    players_data = fetch_players_goals_added_data(season, excluded_positions=['GK'])
    filtered_players = calculate_player_statistics(players_data)
    position_data = aggregate_position_data(filtered_players, stats_to_track)
    insert_player_data(conn, players_data, position_data, stats_to_track, season)

    if close_connection:
        conn.close()
    print(f'Player goals added data for season {season} inserted with position-specific averages.')


def fetch_players_goals_added_data(season: int, excluded_positions: list = None):
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

    api_string = f'nwsl/players/goals-added?season_name={season}&stage_name=Regular Season'
    players_data = make_asa_api_call(api_string)[1]
    
    for player in players_data:
        for action in player.get('data', []):
            action_type = action['action_type'].lower()  # Lowercase the action type for key consistency
            player[f"{action_type}_goals_added_raw"] = action['goals_added_raw']
            player[f"{action_type}_goals_added_above_avg"] = action['goals_added_above_avg']
            player[f"{action_type}_count_actions"] = action['count_actions']

    # Filter out passed in positions and return
    return [player for player in players_data if player.get('general_position') not in excluded_positions]

def calculate_player_statistics(players_data: list):
    """
    Return a list of player statistics. Any custom filtering should be done in this function.

    Args:
        players_data (list): List of player data dictionaries.

    Returns:
        list: Filtered list of player data dictionaries with calculated statistics.
    """
    # Filter players with minutes >= the minimum
    return [player for player in players_data if player.get('minutes_played', 0) >= MINIMUM_MINUTES]

def insert_player_data(conn, players_data, position_data, stats_to_track, season): # pragma: no cover
    """
    Inserts or updates goals added data for all players for a given season.

    Args:
        conn (sqlite3.Connection): Active SQLite connection object.
        players_data (list[dict]): List of dictionaries containing per-player data, including 
            action-level goals added stats (e.g., dribbling, passing, etc.).
        position_data (dict): Dictionary mapping general position (e.g., 'Midfielder') to 
            aggregate statistics (averages, mins, maxes) used for normalization.
        stats_to_track (list[str]): List of stat keys to compute position-based average, min, and max.
        season (int or str): The season year to associate with the data being inserted.

    Behavior:
        - Computes and stores goals added values (raw and above average) and action counts
          for multiple action types: dribbling, fouling, interrupting, passing, receiving, shooting.
        - Normalizes these metrics using position-based averages, minimums, and maximums.
        - Handles edge cases like missing or malformed team IDs.
        - Uses INSERT OR REPLACE to upsert rows into the `player_goals_added` table.

    Returns:
        None: All data is committed directly to the provided database connection.
    """
    cursor = conn.cursor()

    for player in players_data:
        player_id = player.get('player_id', 'Unknown Player ID')
        obj_id = generate_player_season_id(player_id=player_id, season=str(season))
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

        # Prepare player stats and round values
        position_avg = {f"avg_{stat}": round(position_data.get(general_position, {}).get(f"avg_{stat}", 0), 2) for stat in stats_to_track}
        position_min = {f"min_{stat}": round(position_data.get(general_position, {}).get(f"min_{stat}", 0), 2) for stat in stats_to_track}
        position_max = {f"max_{stat}": round(position_data.get(general_position, {}).get(f"max_{stat}", 0), 2) for stat in stats_to_track}


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
                min_dribbling_goals_added_raw, min_dribbling_goals_added_above_avg, min_dribbling_count_actions,
                min_fouling_goals_added_raw, min_fouling_goals_added_above_avg, min_fouling_count_actions,
                min_interrupting_goals_added_raw, min_interrupting_goals_added_above_avg, min_interrupting_count_actions,
                min_passing_goals_added_raw, min_passing_goals_added_above_avg, min_passing_count_actions,
                min_receiving_goals_added_raw, min_receiving_goals_added_above_avg, min_receiving_count_actions,
                min_shooting_goals_added_raw, min_shooting_goals_added_above_avg, min_shooting_count_actions,
                max_dribbling_goals_added_raw, max_dribbling_goals_added_above_avg, max_dribbling_count_actions,
                max_fouling_goals_added_raw, max_fouling_goals_added_above_avg, max_fouling_count_actions,
                max_interrupting_goals_added_raw, max_interrupting_goals_added_above_avg, max_interrupting_count_actions,
                max_passing_goals_added_raw, max_passing_goals_added_above_avg, max_passing_count_actions,
                max_receiving_goals_added_raw, max_receiving_goals_added_above_avg, max_receiving_count_actions,
                max_shooting_goals_added_raw, max_shooting_goals_added_above_avg, max_shooting_count_actions,
                season
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                       ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                       ?, ?, ?, ?, ?, ?, ?)
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
            position_min.get('min_dribbling_goals_added_raw', 0), position_min.get('min_dribbling_goals_added_above_avg', 0), position_min.get('min_dribbling_count_actions', 0),
            position_min.get('min_fouling_goals_added_raw', 0), position_min.get('min_fouling_goals_added_above_avg', 0), position_min.get('min_fouling_count_actions', 0),
            position_min.get('min_interrupting_goals_added_raw', 0), position_min.get('min_interrupting_goals_added_above_avg', 0), position_min.get('min_interrupting_count_actions', 0),
            position_min.get('min_passing_goals_added_raw', 0), position_min.get('min_passing_goals_added_above_avg', 0), position_min.get('min_passing_count_actions', 0),
            position_min.get('min_receiving_goals_added_raw', 0), position_min.get('min_receiving_goals_added_above_avg', 0), position_min.get('min_receiving_count_actions', 0),
            position_min.get('min_shooting_goals_added_raw', 0), position_min.get('min_shooting_goals_added_above_avg', 0), position_min.get('min_shooting_count_actions', 0),
            position_max.get('max_dribbling_goals_added_raw', 0), position_max.get('max_dribbling_goals_added_above_avg', 0), position_max.get('max_dribbling_count_actions', 0),
            position_max.get('max_fouling_goals_added_raw', 0), position_max.get('max_fouling_goals_added_above_avg', 0), position_max.get('max_fouling_count_actions', 0),
            position_max.get('max_interrupting_goals_added_raw', 0), position_max.get('max_interrupting_goals_added_above_avg', 0), position_max.get('max_interrupting_count_actions', 0),
            position_max.get('max_passing_goals_added_raw', 0), position_max.get('max_passing_goals_added_above_avg', 0), position_max.get('max_passing_count_actions', 0),
            position_max.get('max_receiving_goals_added_raw', 0), position_max.get('max_receiving_goals_added_above_avg', 0), position_max.get('max_receiving_count_actions', 0),
            position_max.get('max_shooting_goals_added_raw', 0), position_max.get('max_shooting_goals_added_above_avg', 0), position_max.get('max_shooting_count_actions', 0),
            int(season)
        ))

    conn.commit()

def get_player_goals_added_by_season(player_id, season):
    """
    Retrieves goals added data for a specific player during a given season.

    Args:
        player_id (str): The unique identifier for the player.
        season (str or int): The season to filter the data (e.g., '2024').

    Returns:
        sqlite3.Row or None: A single row containing goals added data,
        player name details, and team name for the specified player and season.
        Returns None if no data is found.
    """
    print('Fetching player goals added for:{}, Season: {}'.format(player_id, season))
    obj_id = generate_player_season_id(player_id=player_id, season=str(season))
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
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

def get_all_players_goals_added_by_season(season):
    """
    Retrieves all players' goals added data for a given season.

    Args:
        season (str): The season identifier to filter the data (e.g., '2024').

    Returns:
        list[sqlite3.Row]: A list of rows containing player goals added data,
        including player info and team info, for the specified season.
    """
    print('Fetching all players goals added. Season: {}'.format(season))
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    query = f'''
        SELECT 
            pga.*,
            pi.*,
            ti.*
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
                pga.season = ?;
        '''
    cursor.execute(query, (season,))
    rows = cursor.fetchall()
    conn.commit()
    conn.close()
    print('All players goals added returned.')
    return rows
