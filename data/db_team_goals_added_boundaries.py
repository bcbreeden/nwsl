import sqlite3
from .db_team_goals_added import get_all_teams_goals_added_by_season
from .data_util import get_db_path

def insert_team_goals_add_boundaries(season):
    """
    Entry point for inserting goals added boundaries for a season.
    Only inserts one row per season with global min/avg/max values.
    """
    team_data = [dict(row) for row in get_all_teams_goals_added_by_season(season)]
    stats_to_track = [
        "dribbling_num_actions_for", "dribbling_goals_added_for", "dribbling_num_actions_against", "dribbling_goals_added_against",
        "shooting_num_actions_for", "shooting_goals_added_for", "shooting_num_actions_against", "shooting_goals_added_against",
        "passing_num_actions_for", "passing_goals_added_for", "passing_num_actions_against", "passing_goals_added_against",
        "interrupting_num_actions_for", "interrupting_goals_added_for", "interrupting_num_actions_against", "interrupting_goals_added_against",
        "receiving_num_actions_for", "receiving_goals_added_for", "receiving_num_actions_against", "receiving_goals_added_against",
        "claiming_num_actions_for", "claiming_goals_added_for", "claiming_num_actions_against", "claiming_goals_added_against",
        "fouling_num_actions_for", "fouling_goals_added_for", "fouling_num_actions_against", "fouling_goals_added_against"
    ]

    season_stats = aggregate_season_stats(team_data, stats_to_track)
    insert_goals_add_boundaries_to_db(season_stats)

def aggregate_season_stats(team_data, stats_to_track):
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

def insert_goals_add_boundaries_to_db(season_data):
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()

    cursor.execute('''
        INSERT OR REPLACE INTO team_goals_add_boundaries (
            season,

            avg_dribbling_num_actions_for, min_dribbling_num_actions_for, max_dribbling_num_actions_for,
            avg_dribbling_goals_added_for, min_dribbling_goals_added_for, max_dribbling_goals_added_for,
            avg_dribbling_num_actions_against, min_dribbling_num_actions_against, max_dribbling_num_actions_against,
            avg_dribbling_goals_added_against, min_dribbling_goals_added_against, max_dribbling_goals_added_against,

            avg_shooting_num_actions_for, min_shooting_num_actions_for, max_shooting_num_actions_for,
            avg_shooting_goals_added_for, min_shooting_goals_added_for, max_shooting_goals_added_for,
            avg_shooting_num_actions_against, min_shooting_num_actions_against, max_shooting_num_actions_against,
            avg_shooting_goals_added_against, min_shooting_goals_added_against, max_shooting_goals_added_against,

            avg_passing_num_actions_for, min_passing_num_actions_for, max_passing_num_actions_for,
            avg_passing_goals_added_for, min_passing_goals_added_for, max_passing_goals_added_for,
            avg_passing_num_actions_against, min_passing_num_actions_against, max_passing_num_actions_against,
            avg_passing_goals_added_against, min_passing_goals_added_against, max_passing_goals_added_against,

            avg_interrupting_num_actions_for, min_interrupting_num_actions_for, max_interrupting_num_actions_for,
            avg_interrupting_goals_added_for, min_interrupting_goals_added_for, max_interrupting_goals_added_for,
            avg_interrupting_num_actions_against, min_interrupting_num_actions_against, max_interrupting_num_actions_against,
            avg_interrupting_goals_added_against, min_interrupting_goals_added_against, max_interrupting_goals_added_against,

            avg_receiving_num_actions_for, min_receiving_num_actions_for, max_receiving_num_actions_for,
            avg_receiving_goals_added_for, min_receiving_goals_added_for, max_receiving_goals_added_for,
            avg_receiving_num_actions_against, min_receiving_num_actions_against, max_receiving_num_actions_against,
            avg_receiving_goals_added_against, min_receiving_goals_added_against, max_receiving_goals_added_against,

            avg_claiming_num_actions_for, min_claiming_num_actions_for, max_claiming_num_actions_for,
            avg_claiming_goals_added_for, min_claiming_goals_added_for, max_claiming_goals_added_for,
            avg_claiming_num_actions_against, min_claiming_num_actions_against, max_claiming_num_actions_against,
            avg_claiming_goals_added_against, min_claiming_goals_added_against, max_claiming_goals_added_against,

            avg_fouling_num_actions_for, min_fouling_num_actions_for, max_fouling_num_actions_for,
            avg_fouling_goals_added_for, min_fouling_goals_added_for, max_fouling_goals_added_for,
            avg_fouling_num_actions_against, min_fouling_num_actions_against, max_fouling_num_actions_against,
            avg_fouling_goals_added_against, min_fouling_goals_added_against, max_fouling_goals_added_against

        ) VALUES (?, 
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?, ?, ?
        )
    ''', (
        season_data["season"],

        # DRIBBLING
        round(season_data.get("avg_dribbling_num_actions_for"), 2),
        season_data.get("min_dribbling_num_actions_for"),
        season_data.get("max_dribbling_num_actions_for"),

        round(season_data.get("avg_dribbling_goals_added_for"), 2),
        season_data.get("min_dribbling_goals_added_for"),
        season_data.get("max_dribbling_goals_added_for"),

        round(season_data.get("avg_dribbling_num_actions_against"), 2),
        season_data.get("min_dribbling_num_actions_against"),
        season_data.get("max_dribbling_num_actions_against"),

        round(season_data.get("avg_dribbling_goals_added_against"), 2),
        season_data.get("min_dribbling_goals_added_against"),
        season_data.get("max_dribbling_goals_added_against"),

        # SHOOTING
        round(season_data.get("avg_shooting_num_actions_for"), 2),
        season_data.get("min_shooting_num_actions_for"),
        season_data.get("max_shooting_num_actions_for"),

        round(season_data.get("avg_shooting_goals_added_for"), 2),
        season_data.get("min_shooting_goals_added_for"),
        season_data.get("max_shooting_goals_added_for"),

        round(season_data.get("avg_shooting_num_actions_against"), 2),
        season_data.get("min_shooting_num_actions_against"),
        season_data.get("max_shooting_num_actions_against"),

        round(season_data.get("avg_shooting_goals_added_against"), 2),
        season_data.get("min_shooting_goals_added_against"),
        season_data.get("max_shooting_goals_added_against"),

        # PASSING
        round(season_data.get("avg_passing_num_actions_for"), 2),
        season_data.get("min_passing_num_actions_for"),
        season_data.get("max_passing_num_actions_for"),

        round(season_data.get("avg_passing_goals_added_for"), 2),
        season_data.get("min_passing_goals_added_for"),
        season_data.get("max_passing_goals_added_for"),

        round(season_data.get("avg_passing_num_actions_against"), 2),
        season_data.get("min_passing_num_actions_against"),
        season_data.get("max_passing_num_actions_against"),

        round(season_data.get("avg_passing_goals_added_against"), 2),
        season_data.get("min_passing_goals_added_against"),
        season_data.get("max_passing_goals_added_against"),

        # INTERRUPTING
        round(season_data.get("avg_interrupting_num_actions_for"), 2),
        season_data.get("min_interrupting_num_actions_for"),
        season_data.get("max_interrupting_num_actions_for"),

        round(season_data.get("avg_interrupting_goals_added_for"), 2),
        season_data.get("min_interrupting_goals_added_for"),
        season_data.get("max_interrupting_goals_added_for"),

        round(season_data.get("avg_interrupting_num_actions_against"), 2),
        season_data.get("min_interrupting_num_actions_against"),
        season_data.get("max_interrupting_num_actions_against"),

        round(season_data.get("avg_interrupting_goals_added_against"), 2),
        season_data.get("min_interrupting_goals_added_against"),
        season_data.get("max_interrupting_goals_added_against"),

        # RECEIVING
        round(season_data.get("avg_receiving_num_actions_for"), 2),
        season_data.get("min_receiving_num_actions_for"),
        season_data.get("max_receiving_num_actions_for"),

        round(season_data.get("avg_receiving_goals_added_for"), 2),
        season_data.get("min_receiving_goals_added_for"),
        season_data.get("max_receiving_goals_added_for"),

        round(season_data.get("avg_receiving_num_actions_against"), 2),
        season_data.get("min_receiving_num_actions_against"),
        season_data.get("max_receiving_num_actions_against"),

        round(season_data.get("avg_receiving_goals_added_against"), 2),
        season_data.get("min_receiving_goals_added_against"),
        season_data.get("max_receiving_goals_added_against"),

        # CLAIMING
        round(season_data.get("avg_claiming_num_actions_for"), 2),
        season_data.get("min_claiming_num_actions_for"),
        season_data.get("max_claiming_num_actions_for"),

        round(season_data.get("avg_claiming_goals_added_for"), 2),
        season_data.get("min_claiming_goals_added_for"),
        season_data.get("max_claiming_goals_added_for"),

        round(season_data.get("avg_claiming_num_actions_against"), 2),
        season_data.get("min_claiming_num_actions_against"),
        season_data.get("max_claiming_num_actions_against"),

        round(season_data.get("avg_claiming_goals_added_against"), 2),
        season_data.get("min_claiming_goals_added_against"),
        season_data.get("max_claiming_goals_added_against"),

        # FOULING
        round(season_data.get("avg_fouling_num_actions_for"), 2),
        season_data.get("min_fouling_num_actions_for"),
        season_data.get("max_fouling_num_actions_for"),

        round(season_data.get("avg_fouling_goals_added_for"), 2),
        season_data.get("min_fouling_goals_added_for"),
        season_data.get("max_fouling_goals_added_for"),

        round(season_data.get("avg_fouling_num_actions_against"), 2),
        season_data.get("min_fouling_num_actions_against"),
        season_data.get("max_fouling_num_actions_against"),

        round(season_data.get("avg_fouling_goals_added_against"), 2),
        season_data.get("min_fouling_goals_added_against"),
        season_data.get("max_fouling_goals_added_against")
    ))

    conn.commit()
    conn.close()


def get_team_goals_add_boundaries_by_season(season):
    print('Attempting to get team goals added boundaries for season:', season)
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute('''
        SELECT * FROM team_goals_add_boundaries WHERE season = ?
    ''', (season,))
    
    row = cursor.fetchone()
    conn.commit()
    conn.close()

    if row:
        print('Team goals added boundaries successfully retrieved for season:', season)
    else:
        print('No data found for season:', season)

    return row
