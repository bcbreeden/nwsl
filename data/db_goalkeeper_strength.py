from .data_util import get_db_path, MINIMUM_MINUTES
from .db_goalkeeper_goals_added import get_all_goalkeeper_goals_added_by_season
from .db_goalkeeper_xgoals import get_all_goalkeepers_xgoals_by_season
from .data_util import get_range, normalize, get_range, verify_minimum_minutes
import sqlite3

def update_goalkeeper_strength(season):
    """
    Calculates and updates the strength score for goalkeepers for a given season.

    This function retrieves goalkeeper performance data, merges expected goals and 
    goals added metrics, normalizes relevant features, and computes a strength score 
    based on weighted contributions of various goalkeeping skills. The resulting 
    strength score is stored in the `goalkeeper_xgoals` database table.

    Args:
        season (int): The season year for which to update goalkeeper strength.

    Process Overview:
        - Fetches xGoals and goals added data for all goalkeepers.
        - Merges the data into player profiles.
        - Filters out players with insufficient minutes played.
        - Normalizes each feature relative to the pool of qualified players.
        - Computes strength scores using weighted feature contributions.
        - Updates the database with calculated strength scores.
        - Sets the strength of unqualified players to 0.

    Notes:
        The strength score is scaled from 0–100 and reflects overall goalkeeper effectiveness 
        including shot stopping, distribution, and command of the box.
    """

    # Fetch raw data: goals added and expected goals per goalkeeper
    players_goals_added = get_all_goalkeeper_goals_added_by_season(season)
    players_xgoals = get_all_goalkeepers_xgoals_by_season(season)

    # Convert both datasets into dictionaries keyed by player_id for fast lookup
    ga_dict = {p['player_id']: dict(p) for p in players_goals_added}
    xg_dict = {p['player_id']: dict(p) for p in players_xgoals}

    # Merge xGoals and goals added data into unified goalkeeper profiles
    goalkeepers = build_goalkeeper_profiles(xg_dict=xg_dict, ga_dict=ga_dict)

    # Split goalkeepers based on whether they meet the minimum minutes threshold
    qualified, unqualified = verify_minimum_minutes(goalkeepers, MINIMUM_MINUTES)

    # Exit early if no qualified keepers are found
    if not qualified:
        print("No qualified goalkeepers found.")
        return

    # Calculate normalization ranges for each relevant stat across qualified goalkeepers
    min_sv, max_sv = get_range(qualified, 'save_perc')
    min_eff, max_eff = get_range(qualified, 'goals_divided_by_xgoals_gk')
    min_ss, max_ss = get_range(qualified, 'shotstopping_ga')
    min_cl, max_cl = get_range(qualified, 'claiming_ga')
    min_pa, max_pa = get_range(qualified, 'passing_ga')
    min_ha, max_ha = get_range(qualified, 'handling_ga')
    min_sw, max_sw = get_range(qualified, 'sweeping_ga')

    # DB connection
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()

    # Loop through all qualified goalkeepers and compute their strength score
    for gk in qualified:
         # Normalize each stat using precomputed min/max ranges
        features = {
            "sv": normalize(gk['save_perc'], min_sv, max_sv),           # Save percentage
            "eff": normalize(gk['goals_divided_by_xgoals_gk'], min_eff, max_eff),  # G/xG (lower is better, flipped in scoring)
            "ss": normalize(gk['shotstopping_ga'], min_ss, max_ss),     # Shot-stopping value
            "cl": normalize(gk['claiming_ga'], min_cl, max_cl),         # Claims value
            "pa": normalize(gk['passing_ga'], min_pa, max_pa),          # Passing value
            "ha": normalize(gk['handling_ga'], min_ha, max_ha),         # Handling value
            "sw": normalize(gk['sweeping_ga'], min_sw, max_sw)          # Sweeping value
        }

        # Compute weighted strength score (0–100 scale)
        strength = calculate_goalkeeper_strength(features)

        # Store the strength score in the database
        cursor.execute(
            '''
            UPDATE goalkeeper_xgoals
            SET player_strength = ?
            WHERE player_id = ? AND season = ?
            ''',
            (strength, gk['player_id'], gk['season'])
        )

    # Set strength to 0 for goalkeepers who did not meet the minimum minutes threshold
    for gk in unqualified:
        cursor.execute(
            '''
            UPDATE goalkeeper_xgoals
            SET player_strength = 0
            WHERE player_id = ? AND season = ?
            ''',
            (gk['player_id'], gk['season'])
        )

    conn.commit()
    conn.close()
    print(f"Updated strength for {len(qualified)} goalkeepers, reset {len(unqualified)} others.")

def build_goalkeeper_profiles(xg_dict, ga_dict):
    """
    Constructs a list of goalkeeper profiles by merging xG data and goals added data.

    Args:
        xg_dict (dict): Dictionary of goalkeeper xG statistics keyed by player_id.
        ga_dict (dict): Dictionary of goalkeeper goals added metrics keyed by player_id.

    Returns:
        list: A list of dictionaries, each representing a goalkeeper's profile with:
            - player_id (str)
            - season (int)
            - minutes_played (int)
            - save_perc (float)
            - goals_divided_by_xgoals_gk (float)
            - shotstopping_ga (float)
            - claiming_ga (float)
            - passing_ga (float)
            - handling_ga (float)
            - sweeping_ga (float)

    Notes:
        Only goalkeepers present in both dictionaries are included.
    """
    profiles = []
    for player_id, p_xg in xg_dict.items():
        if player_id not in ga_dict:
            continue
        p_ga = ga_dict[player_id]
        profiles.append({
            'player_id': player_id,
            'season': p_xg['season'],
            'minutes_played': p_xg['minutes_played'],
            'save_perc': p_xg['save_perc'],
            'goals_divided_by_xgoals_gk': p_xg['goals_divided_by_xgoals_gk'],
            'shotstopping_ga': p_ga['shotstopping_goals_added_raw'],
            'claiming_ga': p_ga['claiming_goals_added_raw'],
            'passing_ga': p_ga['passing_goals_added_raw'],
            'handling_ga': p_ga['handling_goals_added_raw'],
            'sweeping_ga': p_ga['sweeping_goals_added_raw']
        })
    return profiles

# def verify_minimum_minutes(players, minimum_minutes):
#     """
#     Splits players into qualified and unqualified based on minimum minutes played.

#     Args:
#         players (list of dict): List of player data dictionaries.
#         minimum_minutes (int): Threshold for qualification.

#     Returns:
#         tuple: (qualified_players, unqualified_players)
#     """
#     qualified = []
#     unqualified = []
#     for p in players:
#         if p['minutes_played'] >= minimum_minutes:
#             qualified.append(p)
#         else:
#             unqualified.append(p)
#     return qualified, unqualified

def calculate_goalkeeper_strength(features):
    """
    Calculate a goalkeeper's strength score based on weighted normalized features.

    Args:
        features (dict): Dictionary containing normalized features such as:
            - sv (save_perc)
            - eff (goals_divided_by_xgoals_gk)
            - ss (shotstopping_goals_added)
            - cl (claiming_goals_added)
            - pa (passing_goals_added)
            - ha (handling_goals_added)
            - sw (sweeping_goals_added)

    Returns:
        float: Goalkeeper strength score scaled to 0–100.
    """
    strength = (
        0.20 * features["sv"] +          # Shot stopping effectiveness
        0.20 * (1 - features["eff"]) +   # Goal prevention efficiency (lower is better)
        0.20 * features["ss"] +          # Shot stopping GA
        0.10 * features["cl"] +          # Claiming GA
        0.10 * features["pa"] +          # Passing GA
        0.10 * features["ha"] +          # Handling GA
        0.10 * features["sw"]            # Sweeping GA
    )
    return round(strength * 100, 1)
