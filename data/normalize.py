def normalize(stat, min_val, max_val):
    """Normalize a stat using min-max normalization."""
    if max_val == min_val:
        return 0  # Avoid division by zero if all values are the same
    return (stat - min_val) / (max_val - min_val)

def normalize_player_stats(player_stats, stat_ranges):
    """Normalize numeric stats for a player using dynamic stat ranges."""
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