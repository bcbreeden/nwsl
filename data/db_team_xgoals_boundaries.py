import sqlite3
from .db_team_xgoals import get_top_team_xgoals_stat
from .data_util import get_db_path

def insert_team_xgoal_boundaries(season):
    """
    Entry point for inserting stat boundaries for a season.
    Only inserts one row per season with global min/avg/max values.
    """
    team_xgoals_data = [dict(row) for row in get_top_team_xgoals_stat(season)]
    stats_to_track = [
        "shots_for", "shots_against", "goals_for",
        "goals_against", "goal_difference", "xgoals_for", "xgoals_against",
        "xgoal_difference", "goal_difference_minus_xgoal_difference",
        "points", "xpoints", "point_diff", "goalfor_xgoalfor_diff", "psxg_xg_diff"
    ]

    season_stats = aggregate_season_stats(team_xgoals_data, stats_to_track)
    insert_season_boundaries_to_db(season_stats, stats_to_track)

def insert_season_boundaries_to_db(season_data, stats_to_track):
    """
    Inserts one season-wide row into team_xgoals_boundaries.
    """
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()

    cursor.execute('''
        INSERT OR REPLACE INTO team_xgoals_boundaries (
            season,

            avg_shots_for, min_shots_for, max_shots_for,
            avg_shots_against, min_shots_against, max_shots_against,
            avg_goals_for, min_goals_for, max_goals_for,
            avg_goals_against, min_goals_against, max_goals_against,
            avg_goal_difference, min_goal_difference, max_goal_difference,
            avg_xgoals_for, min_xgoals_for, max_xgoals_for,
            avg_xgoals_against, min_xgoals_against, max_xgoals_against,
            avg_xgoal_difference, min_xgoal_difference, max_xgoal_difference,
            avg_goal_difference_minus_xgoal_difference, min_goal_difference_minus_xgoal_difference, max_goal_difference_minus_xgoal_difference,
            avg_points, min_points, max_points,
            avg_xpoints, min_xpoints, max_xpoints,
            avg_point_diff, min_point_diff, max_point_diff,
            avg_goalfor_xgoalfor_diff, min_goalfor_xgoalfor_diff, max_goalfor_xgoalfor_diff,
            avg_psxg_xg_diff, min_psxg_xg_diff, max_psxg_xg_diff
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

        round(season_data.get("avg_shots_for"), 2),
        season_data.get("min_shots_for"),
        season_data.get("max_shots_for"),

        round(season_data.get("avg_shots_against"), 2),
        season_data.get("min_shots_against"),
        season_data.get("max_shots_against"),

        round(season_data.get("avg_goals_for"), 2),
        season_data.get("min_goals_for"),
        season_data.get("max_goals_for"),

        round(season_data.get("avg_goals_against"), 2),
        season_data.get("min_goals_against"),
        season_data.get("max_goals_against"),

        round(season_data.get("avg_goal_difference"), 2),
        season_data.get("min_goal_difference"),
        season_data.get("max_goal_difference"),

        round(season_data.get("avg_xgoals_for"), 2),
        season_data.get("min_xgoals_for"),
        season_data.get("max_xgoals_for"),

        round(season_data.get("avg_xgoals_against"), 2),
        season_data.get("min_xgoals_against"),
        season_data.get("max_xgoals_against"),

        round(season_data.get("avg_xgoal_difference"), 2),
        season_data.get("min_xgoal_difference"),
        season_data.get("max_xgoal_difference"),

        round(season_data.get("avg_goal_difference_minus_xgoal_difference"), 2),
        season_data.get("min_goal_difference_minus_xgoal_difference"),
        season_data.get("max_goal_difference_minus_xgoal_difference"),

        round(season_data.get("avg_points"), 2),
        season_data.get("min_points"),
        season_data.get("max_points"),

        round(season_data.get("avg_xpoints"), 2),
        season_data.get("min_xpoints"),
        season_data.get("max_xpoints"),

        round(season_data.get("avg_point_diff"), 2),
        season_data.get("min_point_diff"),
        season_data.get("max_point_diff"),

        round(season_data.get("avg_goalfor_xgoalfor_diff"), 2),
        season_data.get("min_goalfor_xgoalfor_diff"),
        season_data.get("max_goalfor_xgoalfor_diff"),

        round(season_data.get("avg_psxg_xg_diff"), 2),
        season_data.get("min_psxg_xg_diff"),
        season_data.get("max_psxg_xg_diff")
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

def get_team_xgoal_boundaries_by_season(season):
    print('Attempting to get team xGoal boundaries for season:', season)
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute('''
        SELECT * FROM team_xgoals_boundaries WHERE season = ?
    ''', (season,))
    
    row = cursor.fetchone()
    conn.commit()
    conn.close()

    if row:
        print('Team xGoal boundaries successfully retrieved for season:', season)
    else:
        print('No data found for season:', season)

    return row
