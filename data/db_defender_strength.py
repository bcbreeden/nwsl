from .data_util import get_db_path, MINIMUM_MINUTES
from .db_player_xgoals import get_top_player_xgoals_stat
from .db_player_xpass import get_all_player_xpass
from .db_player_goals_added import get_all_players_goals_added_by_season
from .db_game_shots import get_shots_by_type
from .data_util import get_range, normalize, verify_minimum_minutes
import sqlite3

def update_defender_strength(season):
    """
    Calculates and updates player_strength values for defenders in a given season.

    This function evaluates the performance of defenders (center backs and full backs) 
    using a combination of expected goals, passing metrics, and goals added data. 
    It adjusts expected goals to exclude penalty xG, normalizes each key metric 
    across qualified players, and calculates a weighted strength score that reflects 
    both defensive and passing contributions. Results are written to the `player_xgoals` table.

    Args:
        season (int): The season year for which defender strength scores will be calculated.

    Process Overview:
        - Retrieves defender data from xGoals, xPass, and goals added sources.
        - Builds a profile for each defender, excluding those missing key data.
        - Deducts penalty xG to prevent inflation of attacking metrics.
        - Filters out players with insufficient minutes.
        - Normalizes statistics such as passing over expected, xG, and goals added.
        - Computes strength scores using defined weightings for each attribute.
        - Updates the database with strength scores for qualified players.
        - Sets player_strength to 0 for unqualified players.

    Notes:
        The final strength score is scaled between 0 and 100. It emphasizes defensive disruption 
        (interrupting GA), passing quality, and involvement, while still acknowledging limited 
        offensive contributions like xG.
    """

    # Step 1: Fetch raw player data from database/API
    players_xgoals = get_top_player_xgoals_stat(season)
    players_xpass = get_all_player_xpass(season)
    player_goals_added = get_all_players_goals_added_by_season(season)
    penalty_shots = get_shots_by_type('penalty', season)

    # Step 2: Create quick-lookup dictionaries for merging player stats
    xgoals_dict = {p['player_id']: dict(p) for p in players_xgoals}
    xpass_dict = {p['player_id']: dict(p) for p in players_xpass}
    goals_added_dict = {p['player_id']: dict(p) for p in player_goals_added}

    # Step 3: Build a lookup of total penalty xG per player
    penalty_xg_by_player = get_penalty_xg_by_player(penalty_shots)

    # Step 4: Construct defender records with all relevant stats
    defenders = build_defender_profiles(
        xpass_dict,
        xgoals_dict,
        goals_added_dict,
        penalty_xg_by_player
    )

    # Step 5: Separate players by minutes played threshold
    qualified, unqualified = verify_minimum_minutes(defenders, MINIMUM_MINUTES)

    if not qualified:
        print("No qualified defenders found.")
        return

    # Step 6: Compute min/max ranges for normalization
    min_exp, max_exp = get_range(qualified, 'passes_completed_over_expected')
    min_pct, max_pct = get_range(qualified, 'pass_completion_percentage')
    min_touch, max_touch = get_range(qualified, 'share_team_touches')
    min_xg, max_xg = get_range(qualified, 'xgoals')
    min_pts, max_pts = get_range(qualified, 'points_added')
    min_iga, max_iga = get_range(qualified, 'interrupting_ga')
    min_rga, max_rga = get_range(qualified, 'receiving_ga')
    min_pga, max_pga = get_range(qualified, 'passing_ga')

    # Step 7: Connect to the database
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()

    # Step 8: Calculate normalized strength and update each qualified defender
    for p in qualified:
        # Composite strength score with custom weights
        features = {
            "exp": normalize(p['passes_completed_over_expected'], min_exp, max_exp),
            "pct": normalize(p['pass_completion_percentage'], min_pct, max_pct),
            "touch": normalize(p['share_team_touches'], min_touch, max_touch),
            "xg": normalize(p['xgoals'], min_xg, max_xg),
            "pts": normalize(p['points_added'], min_pts, max_pts),
            "iga": normalize(p['interrupting_ga'], min_iga, max_iga),
            "rga": normalize(p['receiving_ga'], min_rga, max_rga),
            "pga": normalize(p['passing_ga'], min_pga, max_pga)
        }
        score = calculate_defender_strength(features)

        cursor.execute(
            '''
            UPDATE player_xgoals
            SET player_strength = ?
            WHERE player_id = ? AND season = ?
            ''',
            (score, p['player_id'], p['season'])
        )

    # Step 9: Reset strength for unqualified players to 0
    for p in unqualified:
        cursor.execute(
            '''
            UPDATE player_xgoals
            SET player_strength = 0
            WHERE player_id = ? AND season = ?
            ''',
            (p['player_id'], p['season'])
        )

    # Step 10: Commit and close
    conn.commit()
    conn.close()

    print(f"Updated strength for {len(qualified)} defenders, reset {len(unqualified)} others.")


def deduct_penalty_from_xgoal(xgoal_value, penalty_xgoal_value):
    """
    Deducts penalty kick xG from total xG, ensuring the result is not negative.

    Args:
        xgoal_value (float): The original expected goals value.
        penalty_xgoal_value (float): The total xG value from penalty kicks.

    Returns:
        float: The adjusted xG value, with penalty xG removed and a minimum of 0.
    """
    return max(0, xgoal_value - penalty_xgoal_value)

def get_penalty_xg_by_player(penalty_shots):
    """
    Aggregates penalty xG totals for each player.

    Args:
        penalty_shots (list of dict): List of penalty shot data, 
                                      each with 'shooter_player_id' and 'shot_xg'.

    Returns:
        dict: Mapping of player_id to total penalty xG.
    """
    result = {}
    for shot in penalty_shots:
        pid = shot['shooter_player_id']
        result[pid] = result.get(pid, 0) + shot['shot_xg']
    return result

def build_defender_profiles(xpass_dict, xgoals_dict, goals_added_dict, penalty_xg_by_player):
    """
    Constructs defender profiles for players with full data, adjusting xG for penalties.

    Args:
        xpass_dict (dict): Mapping of player_id to xPass stats.
        xgoals_dict (dict): Mapping of player_id to xGoals stats.
        goals_added_dict (dict): Mapping of player_id to Goals Added metrics.
        penalty_xg_by_player (dict): Mapping of player_id to total penalty xG.

    Returns:
        list[dict]: List of fully constructed defender stat dictionaries.
    """
    defenders = []
    for player_id, p_xpass in xpass_dict.items():
        if p_xpass['general_position'] not in ('CB', 'FB'):
            continue
        if player_id not in xgoals_dict or player_id not in goals_added_dict:
            continue

        xg_data = xgoals_dict[player_id]
        ga_data = goals_added_dict[player_id]

        adjusted_xg = deduct_penalty_from_xgoal(
            xg_data['xgoals'],
            penalty_xg_by_player.get(player_id, 0)
        )

        combined = {
            'player_id': player_id,
            'season': p_xpass['season'],
            'xgoals': adjusted_xg,
            'points_added': xg_data['points_added'],
            'passes_completed_over_expected': p_xpass['passes_completed_over_expected'],
            'pass_completion_percentage': p_xpass['pass_completion_percentage'],
            'share_team_touches': p_xpass['share_team_touches'],
            'minutes_played': p_xpass['minutes_played'],
            'interrupting_ga': ga_data['interrupting_goals_added_raw'],
            'receiving_ga': ga_data['receiving_goals_added_raw'],
            'passing_ga': ga_data['passing_goals_added_raw']
        }
        defenders.append(combined)

    return defenders

def calculate_defender_strength(features):
    """
    Calculate a defender's strength score based on weighted normalized features.

    Args:
        features (dict): Dictionary containing normalized features such as:
            - exp (passes_completed_over_expected)
            - pct (pass_completion_percentage)
            - touch (share_team_touches)
            - xg (xgoals)
            - pts (points_added)
            - iga (interrupting_goals_added)
            - rga (receiving_goals_added)
            - pga (passing_goals_added)

    Returns:
        float: Defender strength score scaled to 0–100.
    """
    strength = (
        0.15 * features["exp"] +
        0.10 * features["pct"] +
        0.10 * features["touch"] +
        0.10 * features["xg"] +
        0.15 * features["pts"] +
        0.20 * features["iga"] +
        0.10 * features["rga"] +
        0.10 * features["pga"]
    )
    return round(strength * 100, 1)