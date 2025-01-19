from .db_player_xgoals import get_player_xgoals
from .db_player_xpass import get_player_xpass
from .db_player_goals_added import get_player_goals_added_by_season
from data.db_player_xgoals import get_player_xgoals_ids_by_season
import cohere

def generate_analysis_string(player_id, season):
    """
    Generate a descriptive string of non-average statistics for a player and season, including xgoals, xpass, and goals added.

    Args:
        player_id (str): The player's ID.
        season (int): The season year.

    Returns:
        str: A formatted string containing non-average statistics for xgoals, xpass, and goals added.
    """
    # Non-average statistics from player_xgoals
    xgoals_stats = [
        "minutes_played", "shots", "shots_on_target", "shots_on_target_perc", "goals",
        "xgoals", "xplace", "goals_minus_xgoals", "key_passes", "primary_assists",
        "xassists", "primary_assists_minus_xassists", "xgoals_plus_xassists",
        "points_added", "xpoints_added", "xgoals_xassists_per_90"
    ]

    # Non-average statistics from player_xpass
    xpass_stats = [
        "attempted_passes", "pass_completion_percentage", "xpass_completion_percentage",
        "passes_completed_over_expected", "passes_completed_over_expected_p100",
        "avg_distance_yds", "avg_vertical_distance_yds", "share_team_touches", "count_games"
    ]

    # Non-average statistics from player_goals_added
    goals_added_stats = [
        "dribbling_goals_added_raw", "dribbling_goals_added_above_avg", "dribbling_count_actions",
        "fouling_goals_added_raw", "fouling_goals_added_above_avg", "fouling_count_actions",
        "interrupting_goals_added_raw", "interrupting_goals_added_above_avg", "interrupting_count_actions",
        "passing_goals_added_raw", "passing_goals_added_above_avg", "passing_count_actions",
        "receiving_goals_added_raw", "receiving_goals_added_above_avg", "receiving_count_actions",
        "shooting_goals_added_raw", "shooting_goals_added_above_avg", "shooting_count_actions"
    ]

    # Fetch data for xgoals, xpass, and goals added
    xgoals_data = get_player_xgoals(player_id, season)
    xpass_data = get_player_xpass(player_id, season)
    goals_added_data = get_player_goals_added_by_season(player_id, season)

    if not any([xgoals_data, xpass_data, goals_added_data]):
        return f"No data available for player ID: {player_id}, Season: {season}."

    # Construct analysis string
    analysis_parts = []

    # Add player name from xgoals_data
    analysis_parts.append(f"Player: {xgoals_data['player_name']}")
    analysis_parts.append(f"Position: {xgoals_data['primary_general_position']}")
    analysis_parts.append(f"Team: {xgoals_data['team_name']}")

    # Add xgoals stats to the analysis
    if xgoals_data:
        analysis_parts.append("\nXGoals Statistics:")
        for stat in xgoals_stats:
            if stat in xgoals_data.keys():
                analysis_parts.append(f"{stat.replace('_', ' ').capitalize()}: {xgoals_data[stat]}")

    # Add xpass stats to the analysis
    if xpass_data:
        analysis_parts.append("\nXPass Statistics:")
        for stat in xpass_stats:
            if stat in xpass_data.keys():
                analysis_parts.append(f"{stat.replace('_', ' ').capitalize()}: {xpass_data[stat]}")

    # Add goals added stats to the analysis
    if goals_added_data:
        analysis_parts.append("\nGoals Added Statistics:")
        for stat in goals_added_stats:
            if stat in goals_added_data.keys():
                analysis_parts.append(f"{stat.replace('_', ' ').capitalize()}: {goals_added_data[stat]}")

    # Join the parts into a single string
    analysis_string = "\n".join(analysis_parts)
    return analysis_string


def insert_all_player_analysis(season):
    player_ids = get_player_xgoals_ids_by_season(season)
    sample_id = player_ids[0]
    # print(generate_analysis_string(sample_id, season))
    
    # Initialize the Cohere client
    co = cohere.Client("")
    full_message = '''
    Analyze the following player stats and provide a cohesive analysis for a soccer player. Be consise and highlight key stats that contributes to their play style, strengths, and weaknesses:
    ''' + generate_analysis_string(sample_id, season)
    print(full_message)


    # Chat API call with properly structured messages
    response = co.chat(
        model="command-r7b-12-2024-vllm",  # Specify the model
        message=full_message
    )

    # Print the response
    print(response.text)


