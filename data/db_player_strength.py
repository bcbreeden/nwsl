from .data_util import get_db_path, MINIMUM_MINUTES
from .db_player_xgoals import get_top_player_xgoals_stat
import sqlite3

def normalize(val, min_val, max_val):
    return (val - min_val) / (max_val - min_val) if max_val != min_val else 0.5

def get_range(rows, key):
    values = [row[key] for row in rows]
    return min(values), max(values)

def update_attacker_strength(season):
    players_data = get_top_player_xgoals_stat(season)

    # Step 1: Filter for attackers (Wingers and Strikers)
    # Convert rows to dicts for editing
    all_attackers = [dict(p) for p in players_data if p['general_position'] in ('W', 'ST')]

    if not all_attackers:
        print("No attackers found.")
        return

    # Split into two groups
    qualified = [p for p in all_attackers if p['minutes_played'] >= MINIMUM_MINUTES]
    unqualified = [p for p in all_attackers if p['minutes_played'] < MINIMUM_MINUTES]

    # If none are qualified, skip scoring
    if not qualified:
        print("No qualified attackers to score.")
        return

    # Compute min/max for normalization
    min_xg, max_xg = get_range(qualified, 'xgoals')
    min_goals, max_goals = get_range(qualified, 'goals')
    min_xa, max_xa = get_range(qualified, 'xassists')
    min_sot, max_sot = get_range(qualified, 'shots_on_target')
    min_pts, max_pts = get_range(qualified, 'points_added')

    # Connect to DB
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()

    # Update qualified attackers
    for player in qualified:
        xg = normalize(player['xgoals'], min_xg, max_xg)
        goals = normalize(player['goals'], min_goals, max_goals)
        xa = normalize(player['xassists'], min_xa, max_xa)
        sot = normalize(player['shots_on_target'], min_sot, max_sot)
        pts = normalize(player['points_added'], min_pts, max_pts)

        strength_score = round((
            0.30 * xg +
            0.25 * goals +
            0.20 * xa +
            0.15 * sot +
            0.10 * pts
        ) * 100, 1)

        cursor.execute(
            '''
            UPDATE player_xgoals
            SET player_strength = ?
            WHERE player_id = ? AND season = ?
            ''',
            (strength_score, player['player_id'], player['season'])
        )

    # Set unqualified players to 0
    for player in unqualified:
        cursor.execute(
            '''
            UPDATE player_xgoals
            SET player_strength = 0
            WHERE player_id = ? AND season = ?
            ''',
            (player['player_id'], player['season'])
        )

    conn.commit()
    conn.close()
    print(f"Updated {len(qualified)} qualified attackers and set {len(unqualified)} unqualified to 0.")
