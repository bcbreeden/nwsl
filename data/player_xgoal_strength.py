XGOAL_WEIGHTS = {
    "minutes_played": 0.05,
    "shots": 0.1,
    "shots_on_target": 0.125,
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

def calculate_player_xgoal_strength(normalized_player_stats):
    minutes_played = normalized_player_stats.get("minutes_played", 0)

    # Return 0 if the player hasn't met the minimum minutes threshold
    if minutes_played < MIN_PLAYING_TIME_THRESHOLD:
        return 0

    # Debugging: Print the player's minutes and normalized stats for verification
    print(f"Calculating xGoal strength for player with {minutes_played} minutes played...")

    # Convert stats to per-90 values
    per_90_stats = {
        stat: (value / minutes_played) * 90
        for stat, value in normalized_player_stats.items()
        if stat not in EXCLUDED_METRICS and minutes_played > 0
    }

    # Debugging: Print per-90 stats to verify
    print("Per-90 stats:", per_90_stats)

    # Calculate player strength using weighted stats
    player_strength = sum(
        per_90_stats.get(stat, 0) * XGOAL_WEIGHTS.get(stat, 0)
        for stat in XGOAL_WEIGHTS
    )

    # Return the rounded player strength
    return round((player_strength * 100), 5)