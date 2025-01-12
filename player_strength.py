from data import db_player_xgoals, normalize

player_stats = db_player_xgoals.get_player_xgoals('BLMv7oZO5x', 2024)
# Example usage
stat_ranges = db_player_xgoals.get_stat_ranges()
normalized_player_stats = normalize.normalize_player_stats(player_stats, stat_ranges)
for stat, value in normalized_player_stats.items():
    try:
        # Try to format as a float
        print(f"{stat}: {float(value):.4f}")
    except ValueError:
        # If it can't be converted to float, print as is
        print(f"{stat}: {value}")

print('STRENGTH')
print(db_player_xgoals.calculate_player_xgoal_strength(normalized_player_stats))