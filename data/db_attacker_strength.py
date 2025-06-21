from .data_util import get_db_path, MINIMUM_MINUTES
from .db_player_xgoals import get_top_player_xgoals_stat
from .db_player_goals_added import get_all_players_goals_added_by_season
from .db_game_shots import get_shots_by_type
from .data_util import get_range, normalize, get_range, verify_minimum_minutes
import sqlite3

def update_attacker_strength(season):
    """
    Calculates and updates strength scores for attackers in a given season.

    This function processes goal-scoring and creative metrics for forwards (ST, W),
    excluding penalty goals and xG, then normalizes the metrics and assigns a composite 
    strength score based on weighted contributions. Scores are saved to the database.

    Args:
        season (int): The season year to calculate attacker strength for.

    Process Overview:
        - Fetches xG, goals, and goals added metrics.
        - Filters for attacking positions and deducts penalties.
        - Normalizes key metrics like xG, goals, xA, shots, and goals added.
        - Applies weighted formula to calculate player strength scores.
        - Saves updated scores to the `player_xgoals` table.
        - Sets unqualified players (low minutes) to strength = 0.
    """
    # Retrieve core attacker stats and penalty data for the given season
    players_data = get_top_player_xgoals_stat(season)
    goals_added_data = get_all_players_goals_added_by_season(season)
    penalty_shots = get_shots_by_type('penalty', season)

    # Convert lists to lookup dictionaries
    xgoals_dict = {p['player_id']: dict(p) for p in players_data}
    goals_added_dict = {p['player_id']: dict(p) for p in goals_added_data}

    # Compute total penalty xG and goals per player
    penalty_xg_by_player, penalty_goals_by_player = get_penalty_adjustments(penalty_shots)

    # Assemble attacker profiles (excluding penalty impact)
    attackers = build_attacker_profiles(
        xgoals_dict=xgoals_dict,
        goals_added_dict=goals_added_dict,
        penalty_xg_by_player=penalty_xg_by_player,
        penalty_goals_by_player=penalty_goals_by_player
    )

    # Separate players based on minimum minutes requirement
    qualified, unqualified = verify_minimum_minutes(attackers, MINIMUM_MINUTES)

    if not qualified:
        print("No qualified attackers to score.")
        return

    # Compute normalization ranges for each key metric
    min_xg, max_xg = get_range(qualified, 'xgoals')
    min_goals, max_goals = get_range(qualified, 'goals')
    min_xa, max_xa = get_range(qualified, 'xassists')
    min_sot, max_sot = get_range(qualified, 'shots_on_target')
    min_pts, max_pts = get_range(qualified, 'points_added')
    min_shoot, max_shoot = get_range(qualified, 'shooting_ga')
    min_recv, max_recv = get_range(qualified, 'receiving_ga')
    min_drib, max_drib = get_range(qualified, 'dribbling_ga')

    # Open database connection
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()

    # Calculate strength score for each qualified attacker
    for p in qualified:
        # Normalize each metric for the player relative to the group
        features = {
            "xg": normalize(p['xgoals'], min_xg, max_xg),
            "goals": normalize(p['goals'], min_goals, max_goals),
            "xa": normalize(p['xassists'], min_xa, max_xa),
            "sot": normalize(p['shots_on_target'], min_sot, max_sot),
            "pts": normalize(p['points_added'], min_pts, max_pts),
            "shoot": normalize(p['shooting_ga'], min_shoot, max_shoot),
            "recv": normalize(p['receiving_ga'], min_recv, max_recv),
            "drib": normalize(p['dribbling_ga'], min_drib, max_drib)
        }

        # Generate weighted composite score
        strength_score = calculate_attacker_strength(features)

        # Update the player_xgoals table with the new strength score
        cursor.execute(
            '''
            UPDATE player_xgoals
            SET player_strength = ?
            WHERE player_id = ? AND season = ?
            ''',
            (strength_score, p['player_id'], p['season'])
        )

    # Set player_strength = 0 for unqualified attackers
    for p in unqualified:
        cursor.execute(
            '''
            UPDATE player_xgoals
            SET player_strength = 0
            WHERE player_id = ? AND season = ?
            ''',
            (p['player_id'], p['season'])
        )

    # Finalize updates and close DB connection
    conn.commit()
    conn.close()
    print(f"Updated strength for {len(qualified)} attackers, reset {len(unqualified)} others.")


def get_penalty_adjustments(penalty_shots):
    """
    Sums penalty xG and goals for each player based on shot data.

    Args:
        penalty_shots (list): List of shot dictionaries with 'shooter_player_id', 'shot_xg', and 'goal'.

    Returns:
        tuple[dict, dict]: Two dictionaries mapping player_id to total penalty xG and goals.
    """
    penalty_xg = {}
    penalty_goals = {}
    for shot in penalty_shots:
        pid = shot['shooter_player_id']
        penalty_xg[pid] = penalty_xg.get(pid, 0) + shot['shot_xg']
        if shot['goal']:
            penalty_goals[pid] = penalty_goals.get(pid, 0) + 1
    return penalty_xg, penalty_goals

def build_attacker_profiles(xgoals_dict, goals_added_dict, penalty_xg_by_player, penalty_goals_by_player):
    """
    Builds attacker profiles from xGoals and goals added data with penalty adjustments.

    Args:
        xgoals_dict (dict): Player xGoals data keyed by player_id.
        goals_added_dict (dict): Goals added data keyed by player_id.
        penalty_xg_by_player (dict): Player ID to penalty xG total.
        penalty_goals_by_player (dict): Player ID to penalty goal total.

    Returns:
        list[dict]: List of attacker dictionaries with all necessary fields for scoring.
    """
    attackers = []
    for player_id, player in xgoals_dict.items():
        if player['general_position'] not in ('W', 'ST'):
            continue
        if player_id not in goals_added_dict:
            continue

        ga = goals_added_dict[player_id]
        adjusted_xg = max(0, player['xgoals'] - penalty_xg_by_player.get(player_id, 0))
        adjusted_goals = max(0, player['goals'] - penalty_goals_by_player.get(player_id, 0))

        attackers.append({
            'player_id': player_id,
            'season': player['season'],
            'xgoals': adjusted_xg,
            'goals': adjusted_goals,
            'xassists': player['xassists'],
            'shots_on_target': player['shots_on_target'],
            'points_added': player['points_added'],
            'shooting_ga': ga['shooting_goals_added_raw'],
            'receiving_ga': ga['receiving_goals_added_raw'],
            'dribbling_ga': ga['dribbling_goals_added_raw'],
            'minutes_played': player['minutes_played']
        })
    return attackers

def calculate_attacker_strength(features):
    """
    Calculates the attacker strength score based on weighted normalized metrics.

    Args:
        features (dict): Dictionary containing normalized metrics:
            - xg (float): Expected goals
            - goals (float): Actual goals
            - xa (float): Expected assists
            - sot (float): Shots on target
            - pts (float): Points added
            - shoot (float): Shooting goals added
            - recv (float): Receiving goals added
            - drib (float): Dribbling goals added

    Returns:
        float: Strength score scaled to 0–100.
    """
    strength = (
        0.25 * features["xg"] +
        0.20 * features["goals"] +
        0.15 * features["xa"] +
        0.10 * features["sot"] +
        0.10 * features["pts"] +
        0.10 * features["shoot"] +
        0.05 * features["recv"] +
        0.05 * features["drib"]
    )
    return round(strength * 100, 1)

