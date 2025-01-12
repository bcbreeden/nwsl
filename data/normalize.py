def normalize(stat, min_val, max_val):
    """
    Normalize a stat using min-max normalization.

    This function applies min-max normalization to scale a given stat to a 
    value between 0 and 1 based on its minimum and maximum range. If the 
    minimum and maximum values are equal, the function returns 0 to avoid 
    division by zero.

    Args:
        stat (float or int): 
            The value of the stat to be normalized.
        
        min_val (float or int): 
            The minimum possible value for the stat.
        
        max_val (float or int): 
            The maximum possible value for the stat.

    Returns:
        float: 
            The normalized value of the stat, scaled to the range [0, 1].
            If `min_val` equals `max_val`, the function returns 0.
    """
    if max_val == min_val:
        return 0  # Avoid division by zero if all values are the same
    return (stat - min_val) / (max_val - min_val)

def normalize_player_stats(player_stats, stat_ranges):
    """
    Normalize numeric stats for a player using dynamic stat ranges.

    This function takes a dictionary of player stats and a dictionary of stat ranges 
    (min and max values for each stat). It filters out non-numeric stats, normalizes 
    the remaining numeric stats using min-max normalization, and returns a dictionary 
    of normalized stats. Non-numeric stats are excluded, and `minutes_played` is kept 
    unnormalized to preserve its raw value.

    Args:
        player_stats (dict): 
            A dictionary containing player stats, where keys are stat names 
            and values are the respective stat values (e.g., "shots": 25).
        
        stat_ranges (dict): 
            A dictionary containing the min and max values for each stat, 
            where keys are stat names and values are tuples of the form (min, max). 
            Example: {"shots": (0, 100), "goals": (0, 30)}.

    Returns:
        dict: A dictionary of normalized stats, where each stat's value is 
              normalized to the range [0, 1] using min-max normalization. 
              Non-numeric stats are excluded, and `minutes_played` is kept unchanged.
    """
    player_stats = dict(player_stats)

    # Filter out non-numeric stats
    player_stats = {stat: value for stat, value in player_stats.items() if isinstance(value, (int, float))}

    # Normalize the remaining stats
    normalized_stats = {}
    for stat, value in player_stats.items():
        if stat in stat_ranges and stat != 'minutes_played':
            min_val, max_val = stat_ranges[stat]
            normalized_stats[stat] = normalize(value, min_val, max_val)
        else:
            normalized_stats[stat] = value  # Keep the original value if no range is available
    
    return normalized_stats