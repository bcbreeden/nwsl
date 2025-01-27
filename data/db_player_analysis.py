from .db_player_xgoals import get_player_xgoal_data
from .db_player_xpass import get_player_xpass
from .db_player_goals_added import get_player_goals_added_by_season
from .db_player_xgoals import get_player_xgoals_ids_by_season
from .data_util import generate_player_season_id
import cohere
from dotenv import load_dotenv
import os
from html import escape
import sqlite3
import time

def insert_all_player_analysis(season, testing = True):
    load_dotenv()
    API_KEY = os.getenv('analysis_api_key')
    player_ids = get_player_xgoals_ids_by_season(season)

    # Define the rate limit and buffer
    RATE_LIMIT = 10  # 10 requests per minute
    REQUEST_INTERVAL = (60 - 5) / RATE_LIMIT  # Subtract 5 seconds for a buffer, then calculate interval

    # Initialize the Cohere client
    co = cohere.Client(API_KEY)

    for idx, id in enumerate(player_ids):
        print('Creating analysis for player:', id)
        # sample_id = player_ids[0]
        analysis_string = generate_analysis_string(player_id=id, season=season, minimum_minutes=180)

        if analysis_string is not None:
            full_message = '''
            Analyze the following player stats from the perspective of a soccer scout. The player is a woman. Use the provided statistics and league average to provide a concise, 2-3 paragraph summary of the players performance.
            ''' + analysis_string

            # Chat API call with properly structured messages
            response = co.chat(
                model="command-r7b-12-2024-vllm",  # Specify the model
                message=full_message
            )
            converted_html_text = convert_analysis_to_html(response.text)

            print('Inserting player analysis: {} {}'.format(id, season))
            insert_player_analysis(player_id=id, season=season, analysis_string=converted_html_text)
            print('Complete for: {} {}'.format(id, season))
            print(converted_html_text)

        if testing:
            break
        # If not the last iteration, wait to respect the rate limit
        print('Cycle complete, rate limit pause initiated.')
        if idx < len(player_ids) - 1:
            time.sleep(REQUEST_INTERVAL)
        

def insert_player_analysis(player_id, season, analysis_string):
    obj_id = generate_player_season_id(player_id=player_id, season=season)

    conn = sqlite3.connect('data/nwsl.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('''
            INSERT OR REPLACE INTO player_analysis  (id, player_id, season, analysis) 
            VALUES (?, ?, ?, ?)
        ''', (obj_id, player_id, season, analysis_string)
        )
    conn.commit()
    conn.close()

def generate_analysis_string(player_id, season, minimum_minutes):
    """
    Generate a descriptive string of non-average statistics for a player and season, including xgoals, xpass, and goals added.

    Args:
        player_id (str): The player's ID.
        season (int): The season year.

    Returns:
        str: A formatted string containing non-average statistics for xgoals, xpass, and goals added.
    """
    xgoals_stats = [
        "minutes_played", "shots", "shots_on_target", "shots_on_target_perc", "goals",
        "xgoals", "xplace", "goals_minus_xgoals", "key_passes", "primary_assists",
        "xassists", "primary_assists_minus_xassists", "xgoals_plus_xassists",
        "points_added", "xpoints_added", "xgoals_xassists_per_90", "avg_minutes_played",
        "avg_shots", "avg_shots_on_target", "avg_shots_on_target_perc", "avg_goals",
        "avg_xgoals", "avg_key_passes", "avg_primary_assists", "avg_xassists",
        "avg_xgoals_plus_xassists", "avg_points_added", "avg_xpoints_added",
        "avg_xgoals_xassists_per_90", "avg_xplace", "avg_goals_minus_xgoals",
        "avg_primary_assists_minus_xassists"
    ]

    xpass_stats = [
        "attempted_passes", "pass_completion_percentage", "xpass_completion_percentage",
        "passes_completed_over_expected", "passes_completed_over_expected_p100",
        "avg_distance_yds", "avg_vertical_distance_yds", "share_team_touches", "count_games", "avg_attempted_passes", "avg_pass_completion_percentage",
        "avg_xpass_completion_percentage", "avg_passes_completed_over_expected",
        "avg_passes_completed_over_expected_p100", "avg_avg_distance_yds",
        "avg_avg_vertical_distance_yds", "avg_share_team_touches",
        "avg_count_games"
    ]

    goals_added_stats = [
        "dribbling_goals_added_raw", "dribbling_goals_added_above_avg", "dribbling_count_actions",
        "fouling_goals_added_raw", "fouling_goals_added_above_avg", "fouling_count_actions",
        "interrupting_goals_added_raw", "interrupting_goals_added_above_avg", "interrupting_count_actions",
        "passing_goals_added_raw", "passing_goals_added_above_avg", "passing_count_actions",
        "receiving_goals_added_raw", "receiving_goals_added_above_avg", "receiving_count_actions",
        "shooting_goals_added_raw", "shooting_goals_added_above_avg", "shooting_count_actions"
        "avg_dribbling_goals_added_raw", "avg_dribbling_goals_added_above_avg",
        "avg_dribbling_count_actions", "avg_fouling_goals_added_raw",
        "avg_fouling_goals_added_above_avg", "avg_fouling_count_actions",
        "avg_interrupting_goals_added_raw", "avg_interrupting_goals_added_above_avg",
        "avg_interrupting_count_actions", "avg_passing_goals_added_raw",
        "avg_passing_goals_added_above_avg", "avg_passing_count_actions",
        "avg_receiving_goals_added_raw", "avg_receiving_goals_added_above_avg",
        "avg_receiving_count_actions", "avg_shooting_goals_added_raw",
        "avg_shooting_goals_added_above_avg", "avg_shooting_count_actions"
    ]

    # Fetch data for xgoals, xpass, and goals added
    xgoals_data = get_player_xgoal_data(player_id, season)
    xpass_data = get_player_xpass(player_id, season)
    goals_added_data = get_player_goals_added_by_season(player_id, season)

    if not any([xgoals_data, xpass_data, goals_added_data]):
        print(f"No data available for player ID: {player_id}, Season: {season}.")
        return None
    
    minutes = int(xgoals_data['minutes_played'])
    if minutes < minimum_minutes:
        print(f"Player did not meet minimum minutes requirement: {player_id}, Minutes: {minutes}.")
        return None

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

def convert_analysis_to_html(analysis: str) -> str:
    """
    Converts a formatted analysis string into an HTML representation.

    Args:
        analysis (str): The input analysis string.

    Returns:
        str: The HTML representation of the analysis.
    """
    lines = analysis.split("\n")
    html_lines = []

    for line in lines:
        if line.startswith("**") and line.endswith("**"):
            # Convert headings (e.g., **Strengths:**)
            html_lines.append(f"<h2>{escape(line.strip('**:'))}</h2>")
        elif line.startswith("- **") and line.endswith(":"):
            # Convert strengths/weaknesses list items with bold text
            key, value = line[3:].split("**", 1)
            value = value.strip(":")
            html_lines.append(f"<li><strong>{escape(key)}</strong>: {escape(value)}</li>")
        elif line.startswith("-"):
            # Convert list items
            html_lines.append(f"<li>{escape(line[2:].strip())}</li>")
        elif line.strip() == "":
            # Skip empty lines
            continue
        elif line.startswith("**"):
            # Convert bolded text (e.g., "**Player Analysis: Lena Silano**")
            html_lines.append(f"<h3>{escape(line.strip('**'))}</h3>")
        else:
            # Convert regular paragraphs
            html_lines.append(f"<p>{escape(line.strip())}</p>")

    # Wrap everything in a container div and join the HTML lines
    html_result = f"<div>\n{''.join(html_lines)}\n</div>"

    # Remove all asterisks and apostrophes from the final HTML string
    return html_result.replace("*", "").replace("&#x27;", "'")


def get_player_analysis(player_id: str, season: int):
    print('Fetching player analysis for:{}, Season: {}'.format(player_id, season))
    obj_id = generate_player_season_id(player_id=player_id, season=str(season))
    conn = sqlite3.connect('data/nwsl.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    query = '''
        SELECT * FROM player_analysis
        WHERE id = ?
        '''
    cursor.execute(query, (obj_id,))
    row = cursor.fetchone()
    conn.commit()
    conn.close()
    print('Player analysis returned: {}-{}'.format(season, player_id))
    return row