from .data_util import get_db_path, MINIMUM_MINUTES
from .db_player_xgoals import get_top_player_xgoals_stat
from .db_player_xpass import get_all_player_xpass
from .db_player_goals_added import get_all_players_goals_added_by_season
import sqlite3

def normalize(val, min_val, max_val):
    return (val - min_val) / (max_val - min_val) if max_val != min_val else 0.5

def get_range(rows, key):
    values = [row[key] for row in rows]
    return min(values), max(values)

def update_defender_strength(season):
    players_xgoals = get_top_player_xgoals_stat(season)
    players_xpass = get_all_player_xpass(season)

def update_midfielder_strength(season):
    players_xgoals = get_top_player_xgoals_stat(season)
    players_xpass = get_all_player_xpass(season)
    player_goals_added = get_all_players_goals_added_by_season(season)

    # Build dictionaries for joins
    xgoals_dict = {p['player_id']: dict(p) for p in players_xgoals}
    xpass_dict = {p['player_id']: dict(p) for p in players_xpass}
    goals_added_dict = {p['player_id']: dict(p) for p in player_goals_added}

    # Join and filter midfielders
    midfielders = []
    for player_id, p_xpass in xpass_dict.items():
        if p_xpass['general_position'] not in ('DM', 'CM', 'AM'):
            continue
        if player_id not in xgoals_dict or player_id not in goals_added_dict:
            continue

        combined = {
            'player_id': player_id,
            'season': p_xpass['season'],
            'xassists': xgoals_dict[player_id]['xassists'],
            'points_added': xgoals_dict[player_id]['points_added'],
            'passes_completed_over_expected': p_xpass['passes_completed_over_expected'],
            'pass_completion_percentage': p_xpass['pass_completion_percentage'],
            'share_team_touches': p_xpass['share_team_touches'],
            'minutes_played': p_xpass['minutes_played'],
            'passing_ga': goals_added_dict[player_id]['passing_goals_added_raw'],
            'receiving_ga': goals_added_dict[player_id]['receiving_goals_added_raw'],
            'interrupting_ga': goals_added_dict[player_id]['interrupting_goals_added_raw'],
            'player_name': xgoals_dict[player_id].get('player_name', 'Unknown')
        }
        midfielders.append(combined)

    # Filter by minutes
    qualified = [p for p in midfielders if p['minutes_played'] >= MINIMUM_MINUTES]
    unqualified = [p for p in midfielders if p['minutes_played'] < MINIMUM_MINUTES]

    if not qualified:
        print("No qualified midfielders found.")
        return

    # Normalize features
    min_exp, max_exp = get_range(qualified, 'passes_completed_over_expected')
    min_touch, max_touch = get_range(qualified, 'share_team_touches')
    min_xa, max_xa = get_range(qualified, 'xassists')
    min_pts, max_pts = get_range(qualified, 'points_added')
    min_pga, max_pga = get_range(qualified, 'passing_ga')
    min_rga, max_rga = get_range(qualified, 'receiving_ga')
    min_iga, max_iga = get_range(qualified, 'interrupting_ga')

    # DB update
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()

    for p in qualified:
        exp = normalize(p['passes_completed_over_expected'], min_exp, max_exp)
        touch = normalize(p['share_team_touches'], min_touch, max_touch)
        xa = normalize(p['xassists'], min_xa, max_xa)
        pts = normalize(p['points_added'], min_pts, max_pts)
        pga = normalize(p['passing_ga'], min_pga, max_pga)
        rga = normalize(p['receiving_ga'], min_rga, max_rga)
        iga = normalize(p['interrupting_ga'], min_iga, max_iga)

        strength = (
            0.20 * exp +
            0.15 * touch +
            0.15 * xa +
            0.15 * pts +
            0.15 * pga +
            0.10 * rga +
            0.10 * iga
        )

        score = round(strength * 100, 1)

        cursor.execute(
            '''
            UPDATE player_xgoals
            SET player_strength = ?
            WHERE player_id = ? AND season = ?
            ''',
            (score, p['player_id'], season)
        )

    # Unqualified players get a score of 0
    for p in unqualified:
        cursor.execute(
            '''
            UPDATE player_xgoals
            SET player_strength = 0
            WHERE player_id = ? AND season = ?
            ''',
            (p['player_id'], season)
        )

    conn.commit()
    conn.close()
    print(f"Updated strength for {len(qualified)} midfielders, reset {len(unqualified)} others.")


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
