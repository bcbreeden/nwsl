import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import sqlite3

EXCLUDED_METRICS = {
    "season",
    "height_ft",
    "height_in",
    "minutes_played",
    "primary_assists_minus_xassists",
    "goals_minus_xgoals",
    "shots_on_target_perc"
}

MIN_PLAYING_TIME_THRESHOLD = 400  # Minimum minutes played to calculate meaningful xGoal strength

def calculate_player_xgoal_strength(normalized_player_stats, xgoals_weight=None):
    """
    Calculate a player's xGoal strength, optionally using a custom weight dictionary.

    This function computes the xGoal strength for a player by normalizing their stats to 
    per-90-minute values, applying weights to the normalized stats, and summing the weighted 
    contributions. If a custom weight dictionary (`xgoals_weight`) is not provided, dynamic 
    weights are generated. The function also excludes stats from the calculation based on 
    a predefined exclusion list (`EXCLUDED_METRICS`) and ensures players meet a minimum 
    playing time threshold.

    Args:
        normalized_player_stats (dict): 
            A dictionary containing normalized stats for a player, where keys are 
            stat names and values are normalized values.
        
        xgoals_weight (dict, optional): 
            A dictionary of weights for each stat, where keys are stat names and 
            values are their corresponding weights. If not provided, dynamic 
            weights are generated using `generate_player_stat_weights()`.

    Returns:
        float: 
            The calculated xGoal strength for the player, scaled by 100 and rounded 
            to three decimal places. Returns 0 if the player does not meet the 
            minimum playing time threshold.
    """
    if xgoals_weight is None:
        xgoals_weight = generate_player_stat_weights()

    minutes_played = normalized_player_stats.get("minutes_played", 0)

    # Return 0 if the player hasn't met the minimum minutes threshold
    if minutes_played < MIN_PLAYING_TIME_THRESHOLD:
        return 0

    # Convert stats to per-90 values (ignore EXCLUDED_METRICS)
    per_90_stats = {
        stat: (value / minutes_played) * 90
        for stat, value in normalized_player_stats.items()
        if stat not in EXCLUDED_METRICS and minutes_played > 0
    }

    # Calculate player strength using weighted stats
    player_strength = sum(
        per_90_stats.get(stat, 0) * xgoals_weight.get(stat, 0)
        for stat in xgoals_weight
    )

    return round((player_strength * 100), 3)

def calculate_xgoals_xassists(player_stats):
    """
    Calculate xGoals + xAssists for a player, normalized per 90 minutes.
    
    Args:
        player_stats (dict): Dictionary containing player stats, including
                             'xgoals', 'xassists', and 'minutes_played'.
    
    Returns:
        float: xGoals + xAssists per 90 minutes, rounded to two decimals.
    """
    xgoals = player_stats.get('xgoals', 0)
    xassists = player_stats.get('xassists', 0)
    minutes_played = player_stats.get('minutes_played', 0)
    
    # Avoid division by zero and handle players with very low minutes
    if minutes_played < 400:  # Threshold for meaningful minutes played
        return 0

    # Calculate per-90 metric
    xgoals_xassists_per_90 = ((xgoals + xassists) / minutes_played) * 90
    return round(xgoals_xassists_per_90, 2)

def generate_player_stat_weights():
    """
    Generate dynamic weights for player stats based on their correlation
    with the primary metric (e.g., xGoals + xAssists per 90).
    
    Returns:
        dict: Dictionary of dynamic weights for each player stat.
    """
    # List of all stats to include in the analysis
    relevant_stats = [
        "minutes_played", "shots", "shots_on_target", "shots_on_target_perc",
        "goals", "xgoals", "xplace", "goals_minus_xgoals",
        "key_passes", "primary_assists", "xassists", "primary_assists_minus_xassists",
        "xgoals_plus_xassists", "points_added", "xpoints_added"
    ]

    primary_metric = "xgoals_xassists_per_90"
    data = _get_player_xgoal_data()

    # Filter data to include only the relevant stats and the primary metric
    filtered_data = data[relevant_stats + [primary_metric]]

    # Calculate correlation of each stat with the primary metric
    correlations = filtered_data.corr()[primary_metric].drop(primary_metric)

    # Normalize correlations to sum to 1
    scaler = MinMaxScaler()
    normalized_corr = scaler.fit_transform(correlations.values.reshape(-1, 1)).flatten()
    normalized_weights = normalized_corr / normalized_corr.sum()

    # Create a dictionary of weights
    weights = {stat: weight for stat, weight in zip(correlations.index, normalized_weights)}

    # Debugging: Print weights to verify
    # print('Calculated stat weights:', weights)

    return weights

def _get_player_xgoal_data():
    conn = sqlite3.connect('data/nwsl.db')
    query = '''
        SELECT 
            minutes_played, shots, shots_on_target, shots_on_target_perc, goals,
            xgoals, xplace, goals_minus_xgoals, key_passes, primary_assists,
            xassists, primary_assists_minus_xassists, xgoals_plus_xassists,
            points_added, xpoints_added, xgoals_xassists_per_90
        FROM player_xgoals
        WHERE minutes_played >= 400;
    '''
    data = pd.read_sql_query(query, conn)
    conn.close
    return data