import sqlite3
from .db_team_xpass import get_all_teams_xpass_by_season
from .data_util import get_db_path

def insert_team_xpass_boundaries(season):
    """
    Entry point for inserting xPass stat boundaries for a season.
    Only inserts one row per season with global min/avg/max values.
    """
    team_xpass_data = [dict(row) for row in get_all_teams_xpass_by_season(season)]
    stats_to_track = [
        "attempted_passes_for", "pass_completion_percentage_for",
        "xpass_completion_percentage_for", "passes_completed_over_expected_for",
        "passes_completed_over_expected_p100_for", "avg_vertical_distance_for",
        "attempted_passes_against", "pass_completion_percentage_against",
        "xpass_completion_percentage_against", "passes_completed_over_expected_against",
        "passes_completed_over_expected_p100_against", "avg_vertical_distance_against",
        "passes_completed_over_expected_difference", "avg_vertical_distance_difference"
    ]

    season_stats = aggregate_season_stats(team_xpass_data, stats_to_track)
    insert_xpass_boundaries_to_db(season_stats, stats_to_track)

def insert_xpass_boundaries_to_db(season_data, stats_to_track):
    """
    Inserts one season-wide row into team_xpass_boundaries with clear formatting.
    """
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()

    cursor.execute('''
        INSERT OR REPLACE INTO team_xpass_boundaries (
            season,

            avg_attempted_passes_for, min_attempted_passes_for, max_attempted_passes_for,
            avg_pass_completion_percentage_for, min_pass_completion_percentage_for, max_pass_completion_percentage_for,
            avg_xpass_completion_percentage_for, min_xpass_completion_percentage_for, max_xpass_completion_percentage_for,
            avg_passes_completed_over_expected_for, min_passes_completed_over_expected_for, max_passes_completed_over_expected_for,
            avg_passes_completed_over_expected_p100_for, min_passes_completed_over_expected_p100_for, max_passes_completed_over_expected_p100_for,
            avg_vertical_distance_for, min_vertical_distance_for, max_vertical_distance_for,
            avg_attempted_passes_against, min_attempted_passes_against, max_attempted_passes_against,
            avg_pass_completion_percentage_against, min_pass_completion_percentage_against, max_pass_completion_percentage_against,
            avg_xpass_completion_percentage_against, min_xpass_completion_percentage_against, max_xpass_completion_percentage_against,
            avg_passes_completed_over_expected_against, min_passes_completed_over_expected_against, max_passes_completed_over_expected_against,
            avg_passes_completed_over_expected_p100_against, min_passes_completed_over_expected_p100_against, max_passes_completed_over_expected_p100_against,
            avg_vertical_distance_against, min_vertical_distance_against, max_vertical_distance_against,
            avg_passes_completed_over_expected_difference, min_passes_completed_over_expected_difference, max_passes_completed_over_expected_difference,
            avg_vertical_distance_difference, min_vertical_distance_difference, max_vertical_distance_difference

        ) VALUES (?, 
            ?, ?, ?, 
            ?, ?, ?, 
            ?, ?, ?, 
            ?, ?, ?, 
            ?, ?, ?, 
            ?, ?, ?, 
            ?, ?, ?, 
            ?, ?, ?, 
            ?, ?, ?, 
            ?, ?, ?, 
            ?, ?, ?, 
            ?, ?, ?, 
            ?, ?, ?,
            ?, ?, ?
        )
    ''', (
        season_data["season"],

        round(season_data.get("avg_attempted_passes_for"), 2),
        season_data.get("min_attempted_passes_for"),
        season_data.get("max_attempted_passes_for"),

        round(season_data.get("avg_pass_completion_percentage_for"), 2),
        season_data.get("min_pass_completion_percentage_for"),
        season_data.get("max_pass_completion_percentage_for"),

        round(season_data.get("avg_xpass_completion_percentage_for"), 2),
        season_data.get("min_xpass_completion_percentage_for"),
        season_data.get("max_xpass_completion_percentage_for"),

        round(season_data.get("avg_passes_completed_over_expected_for"), 2),
        season_data.get("min_passes_completed_over_expected_for"),
        season_data.get("max_passes_completed_over_expected_for"),

        round(season_data.get("avg_passes_completed_over_expected_p100_for"), 2),
        season_data.get("min_passes_completed_over_expected_p100_for"),
        season_data.get("max_passes_completed_over_expected_p100_for"),

        round(season_data.get("avg_avg_vertical_distance_for"), 2),
        season_data.get("min_vertical_distance_for"),
        season_data.get("max_vertical_distance_for"),

        round(season_data.get("avg_attempted_passes_against"), 2),
        season_data.get("min_attempted_passes_against"),
        season_data.get("max_attempted_passes_against"),

        round(season_data.get("avg_pass_completion_percentage_against"), 2),
        season_data.get("min_pass_completion_percentage_against"),
        season_data.get("max_pass_completion_percentage_against"),

        round(season_data.get("avg_xpass_completion_percentage_against"), 2),
        season_data.get("min_xpass_completion_percentage_against"),
        season_data.get("max_xpass_completion_percentage_against"),

        round(season_data.get("avg_passes_completed_over_expected_against"), 2),
        season_data.get("min_passes_completed_over_expected_against"),
        season_data.get("max_passes_completed_over_expected_against"),

        round(season_data.get("avg_passes_completed_over_expected_p100_against"), 2),
        season_data.get("min_passes_completed_over_expected_p100_against"),
        season_data.get("max_passes_completed_over_expected_p100_against"),

        round(season_data.get("avg_avg_vertical_distance_against"), 2),
        season_data.get("min_vertical_distance_against"),
        season_data.get("max_vertical_distance_against"),

        round(season_data.get("avg_passes_completed_over_expected_difference"), 2),
        season_data.get("min_passes_completed_over_expected_difference"),
        season_data.get("max_passes_completed_over_expected_difference"),

        round(season_data.get("avg_avg_vertical_distance_difference"), 2),
        season_data.get("min_vertical_distance_difference"),
        season_data.get("max_vertical_distance_difference")
    ))

    conn.commit()
    conn.close()

def aggregate_season_stats(team_data, stats_to_track):
    """
    Computes avg, min, and max for each stat across all teams in a given season.
    Returns a dictionary ready for insertion.
    """
    result = {"team_id": "ALL", "season": team_data[0]["season"] if team_data else None}

    for stat in stats_to_track:
        values = [row[stat] for row in team_data if row.get(stat) is not None]
        if values:
            result[f"avg_{stat}"] = sum(values) / len(values)
            result[f"min_{stat}"] = min(values)
            result[f"max_{stat}"] = max(values)
        else:
            result[f"avg_{stat}"] = None
            result[f"min_{stat}"] = None
            result[f"max_{stat}"] = None

    return result

def get_team_xpass_boundaries_by_season(season):
    print('Attempting to get team xPass boundaries for season:', season)
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute('''
        SELECT * FROM team_xpass_boundaries WHERE season = ?
    ''', (season,))
    
    row = cursor.fetchone()
    conn.commit()
    conn.close()

    if row:
        print('Team xPass boundaries successfully retrieved for season:', season)
    else:
        print('No data found for season:', season)

    return row
