from .data_util import get_db_path, MINIMUM_MINUTES
from .db_player_xgoals import get_top_player_xgoals_stat
from .db_player_xpass import get_all_player_xpass
from .db_player_goals_added import get_all_players_goals_added_by_season
from .db_game_shots import get_shots_by_type
from .data_util import get_range, normalize, get_range, verify_minimum_minutes
import sqlite3

def update_midfielder_strength(season):
    players_xgoals = get_top_player_xgoals_stat(season)
    players_xpass = get_all_player_xpass(season)
    player_goals_added = get_all_players_goals_added_by_season(season)
    penalty_shots = get_shots_by_type('penalty', season)

    # Build dictionaries for joins
    xgoals_dict = {p['player_id']: dict(p) for p in players_xgoals}
    xpass_dict = {p['player_id']: dict(p) for p in players_xpass}
    goals_added_dict = {p['player_id']: dict(p) for p in player_goals_added}

    # Sum penalty xG per player
    penalty_xg_by_player = {}
    for shot in penalty_shots:
        pid = shot['shooter_player_id']
        penalty_xg_by_player[pid] = penalty_xg_by_player.get(pid, 0) + shot['shot_xg']

    # Join and filter midfielders
    midfielders = build_midfielder_profiles(xgoals_dict=xgoals_dict,
                                            xpass_dict=xpass_dict,
                                            goals_added_dict=goals_added_dict,
                                            penalty_xg_by_player=penalty_xg_by_player)

    # Filter by minutes
    qualified, unqualified = verify_minimum_minutes(midfielders, MINIMUM_MINUTES)

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
        features = {
            "exp": normalize(p['passes_completed_over_expected'], min_exp, max_exp),
            "touch": normalize(p['share_team_touches'], min_touch, max_touch),
            "xa": normalize(p['xassists'], min_xa, max_xa),
            "pts": normalize(p['points_added'], min_pts, max_pts),
            "pga": normalize(p['passing_ga'], min_pga, max_pga),
            "rga": normalize(p['receiving_ga'], min_rga, max_rga),
            "iga": normalize(p['interrupting_ga'], min_iga, max_iga)
        }

        score = calculate_midfielder_strength(features)

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

def build_midfielder_profiles(xgoals_dict, xpass_dict, goals_added_dict, penalty_xg_by_player):
    """
    Builds a list of midfielder profiles with adjusted metrics.

    Args:
        xgoals_dict (dict): Dictionary of player xGoals data keyed by player_id.
        xpass_dict (dict): Dictionary of player xPass data keyed by player_id.
        goals_added_dict (dict): Dictionary of goals added data keyed by player_id.
        penalty_xg_by_player (dict): Dictionary of penalty xG totals keyed by player_id.

    Returns:
        list[dict]: A list of midfielder profiles with relevant stats and adjusted metrics.
    """
    midfielders = []
    for player_id, p_xpass in xpass_dict.items():
        if p_xpass['general_position'] not in ('DM', 'CM', 'AM'):
            continue
        if player_id not in xgoals_dict or player_id not in goals_added_dict:
            continue

        xg_data = xgoals_dict[player_id]
        ga_data = goals_added_dict[player_id]

        # Deduct penalty xG
        original_pts = xg_data['points_added']
        pk_xg = penalty_xg_by_player.get(player_id, 0)
        adjusted_pts = max(0, original_pts - pk_xg)

        combined = {
            'player_id': player_id,
            'season': p_xpass['season'],
            'xassists': xg_data['xassists'],
            'points_added': adjusted_pts,
            'passes_completed_over_expected': p_xpass['passes_completed_over_expected'],
            'pass_completion_percentage': p_xpass['pass_completion_percentage'],
            'share_team_touches': p_xpass['share_team_touches'],
            'minutes_played': p_xpass['minutes_played'],
            'passing_ga': ga_data['passing_goals_added_raw'],
            'receiving_ga': ga_data['receiving_goals_added_raw'],
            'interrupting_ga': ga_data['interrupting_goals_added_raw'],
            'player_name': xg_data.get('player_name', 'Unknown'),
        }
        midfielders.append(combined)
    return midfielders

def calculate_midfielder_strength(features):
    """
    Calculate a midfielder's strength score based on weighted normalized features.

    Args:
        features (dict): Dictionary of normalized metrics:
            - exp: Passes completed over expected
            - touch: Share of team touches
            - xa: Expected assists
            - pts: Points added
            - pga: Passing goals added
            - rga: Receiving goals added
            - iga: Interrupting goals added

    Returns:
        float: Midfielder strength score scaled from 0–100.
    """
    strength = (
        0.20 * features["exp"] +
        0.15 * features["touch"] +
        0.15 * features["xa"] +
        0.15 * features["pts"] +
        0.15 * features["pga"] +
        0.10 * features["rga"] +
        0.10 * features["iga"]
    )
    return round(strength * 100, 1)
