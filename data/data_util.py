from collections import defaultdict
import os

# Constants
MINIMUM_MINUTES = 270 # ~3 full games

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