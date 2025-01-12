XGOAL_WEIGHTS = {
    "minutes_played": 0.05,
    "shots": 0.1,
    "shots_on_target": 0.1,
    "shots_on_target_perc": 0.05,
    "goals": 0.2,
    "xgoals": 0.15,
    "xplace": 0.05,
    "goals_minus_xgoals": 0.05,
    "key_passes": 0.1,
    "primary_assists": 0.1,
    "xassists": 0.1,
    "primary_assists_minus_xassists": 0.05,
    "xgoals_plus_xassists": 0.1,
    "points_added": 0.1,
    "xpoints_added": 0.05
}

def calculate_player_xgoal_strength(normalized_player_stats):
    player_strength = sum(
    normalized_player_stats[stat] * XGOAL_WEIGHTS[stat]
    for stat in normalized_player_stats
    if stat not in {'season', 'height_ft', 'height_in'}  # Exclude unwanted keys
    )
    
    return round(player_strength, 2)