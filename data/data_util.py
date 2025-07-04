from collections import defaultdict
import os
from datetime import datetime
import pytz

# Constants
MINIMUM_MINUTES = 270 # ~3 full games
ALL_SEASONS = [2025, 2024, 2023, 2022, 2021, 2020, 2019, 2018, 2017, 2016]

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
            value = player.get(stat, 0) or 0
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

def generate_player_season_id(player_id, season):
    """
    Creates a player id for a specific season.

    Args:
        player_id (int): The player's id.
        season (int): The season.
    
    Returns:
        str: The player id for a specific
        season.
    """
    return (str(player_id) + str(season))

def get_db_path():
    """
    Get the absolute path to the project's SQLite database file.

    Returns:
        str: The full absolute path to the 'nwsl.db' file located in the same
             directory as this script.
    """
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(BASE_DIR, 'nwsl.db')
    return db_path

def validate_id(id):
    """
    Validates that a game ID is a non-empty string.

    Args:
        game_id (str): The game ID to validate.

    Raises:
        ValueError: If the game ID is not a string or is empty.
    """
    if not id or not isinstance(id, str):
        raise ValueError("ID must be a non-empty string")

def validate_season(season):
    """
    Validates that a season value is a valid integer.

    Args:
        season (int): The season value to validate.

    Raises:
        ValueError: If the season is not an integer or is null/zero.
    """
    if not season or not isinstance(season, int):
        raise ValueError("season must be a valid integer")

def convert_utc_to_est(utc_str):
    """
    Converts a UTC datetime string to a formatted US Eastern Time string.

    Args:
        utc_str (str): A UTC datetime string in the format "%Y-%m-%d %H:%M:%S %Z".

    Returns:
        str or None: The datetime converted to US Eastern Time and formatted as 
        "Weekday, Month Day at Hour:Minute AM/PM". Returns None if the input is a placeholder string.
    """
    if utc_str == 'Unknown Last Updated Time':
        return None

    # Parse string to datetime
    dt_utc = datetime.strptime(utc_str, "%Y-%m-%d %H:%M:%S %Z")
    dt_utc = pytz.utc.localize(dt_utc)

    # Convert to US Eastern time
    dt_est = dt_utc.astimezone(pytz.timezone('US/Eastern'))

    # Format manually for cross-platform support
    weekday = dt_est.strftime("%A")
    month = dt_est.strftime("%B")
    day = str(dt_est.day)  # no leading zero
    hour = dt_est.strftime("%I").lstrip('0')  # remove leading zero
    minute = dt_est.strftime("%M")
    am_pm = dt_est.strftime("%p")

    return f"{weekday}, {month} {day} at {hour}:{minute} {am_pm}"

def get_range(rows, key):
    """
    Retrieves the minimum and maximum values for a specified key across a list of dictionaries.

    Args:
        rows (list[dict]): A list of dictionaries (e.g., player or team records).
        key (str): The key to extract values from for min/max computation.

    Returns:
        tuple[float, float]: A tuple containing the minimum and maximum values for the specified key.
    """
    values = [row[key] for row in rows]
    return min(values), max(values)

def normalize(val, min_val, max_val):
    """
    Normalizes a value to a 0–1 scale based on the provided minimum and maximum values.

    Args:
        val (float): The value to normalize.
        min_val (float): The minimum value of the feature range.
        max_val (float): The maximum value of the feature range.

    Returns:
        float: The normalized value between 0 and 1. If min and max are equal, returns 0.5 as a neutral midpoint.
    """
    return (val - min_val) / (max_val - min_val) if max_val != min_val else 0.5

def verify_minimum_minutes(players, minimum_minutes):
    """
    Splits players into qualified and unqualified based on minimum minutes played.

    Args:
        players (list of dict): List of player data dictionaries.
        minimum_minutes (int): Threshold for qualification.

    Returns:
        tuple: (qualified_players, unqualified_players)
    """
    qualified = []
    unqualified = []
    for p in players:
        if p['minutes_played'] >= minimum_minutes:
            qualified.append(p)
        else:
            unqualified.append(p)
    return qualified, unqualified