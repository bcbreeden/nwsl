from api import make_asa_api_call
from .data_util import get_db_path, validate_id, validate_season
import sqlite3

def insert_all_game_shots(game_id, season): # pragma: no cover
    """
    Inserts shot-level data into the game_shots table for a specific game and season.

    Args:
        game_id (str): The unique identifier for the game to insert shot data for.
        season (int): The season the game belongs to.
    
    Returns:
        None
    """
    validate_id(game_id)
    validate_season(season)
    print(f'Attempting to insert all shots for game {game_id}, season: {season}...')
    shots_data = make_asa_api_call(f'nwsl/games/shots?game_id={game_id}')[1]
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()

    for shot in shots_data:
        game_id_val = shot.get('game_id', 'Unknown')
        period_id = shot.get('period_id', -1)
        expanded_minute = shot.get('expanded_minute', -1)
        game_minute = shot.get('game_minute', -1)
        team_id = shot.get('team_id', 'Unknown')
        shooter_player_id = shot.get('shooter_player_id', 'Unknown')
        assist_player_id = shot.get('assist_player_id', 'Unknown')
        shot_location_x = shot.get('shot_location_x', 0.0)
        shot_location_y = shot.get('shot_location_y', 0.0)
        shot_end_location_x = shot.get('shot_end_location_x', 0.0)
        shot_end_location_y = shot.get('shot_end_location_y', 0.0)
        distance_from_goal = shot.get('distance_from_goal', 0.0)
        distance_from_goal_yds = shot.get('distance_from_goal_yds', 0.0)
        blocked = shot.get('blocked', 0)
        blocked_x = shot.get('blocked_x', 0.0)
        blocked_y = shot.get('blocked_y', 0.0)
        goal = shot.get('goal', 0)
        own_goal = shot.get('own_goal', 0)
        home_score = shot.get('home_score', -1)
        away_score = shot.get('away_score', -1)
        shot_xg = shot.get('shot_xg', 0.0)
        shot_psxg = shot.get('shot_psxg', 0.0)
        head = shot.get('head', 0)
        assist_through_ball = shot.get('assist_through_ball', 0)
        assist_cross = shot.get('assist_cross', 0)
        pattern_of_play = shot.get('pattern_of_play', 'Unknown')
        shot_order = shot.get('shot_order', -1)

        cursor.execute('''
            INSERT OR REPLACE INTO game_shots (
                game_id,
                period_id,
                expanded_minute,
                game_minute,
                team_id,
                shooter_player_id,
                assist_player_id,
                shot_location_x,
                shot_location_y,
                shot_end_location_x,
                shot_end_location_y,
                distance_from_goal,
                distance_from_goal_yds,
                blocked,
                blocked_x,
                blocked_y,
                goal,
                own_goal,
                home_score,
                away_score,
                shot_xg,
                shot_psxg,
                head,
                assist_through_ball,
                assist_cross,
                pattern_of_play,
                shot_order,
                season
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            game_id_val, period_id, expanded_minute, game_minute, team_id,
            shooter_player_id, assist_player_id, shot_location_x, shot_location_y,
            shot_end_location_x, shot_end_location_y, round(distance_from_goal, 1),
            round(distance_from_goal_yds, 1), blocked, blocked_x, blocked_y,
            goal, own_goal, home_score, away_score, round(shot_xg, 2), round(shot_psxg, 2),
            head, assist_through_ball, assist_cross, pattern_of_play, shot_order, season
        ))
        conn.commit()

    conn.close()
    print(f'All shots for game {game_id} successfully entered into the database.')

def get_shots_by_game_id(game_id):
    """
    Retrieves all shot records for a specific game from the local database.

    Args:
        game_id (str): The unique identifier for the game to fetch shot data for.

    Returns:
        list[sqlite3.Row]: A list of shot records ordered by shot sequence.
    """
    validate_id(game_id)
    print(f'Fetching all shots for game {game_id}...')
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute('''
        SELECT * FROM game_shots
        WHERE game_id = ?
        ORDER BY shot_order ASC
    ''', (game_id,))
    
    rows = cursor.fetchall()
    conn.close()

    print(f'{len(rows)} shots retrieved for game {game_id}.')
    return rows

def get_shots_by_type(shot_type, season):
    """
    Retrieves all shots of a specific pattern of play for a given season.

    Args:
        shot_type (str): The shot type to filter by (e.g., 'regular', 'set piece', 'fastbreak').
        season (int): The season to filter shot data by.

    Returns:
        list[sqlite3.Row]: A list of shot records matching the specified type and season.
    """
    validate_season(season)
    print(f'Fetching all {shot_type} shots...')
    available_shot_types = ['regular', 'set piece', 'fastbreak', 'free kick', 'penalty']
    shot_type = shot_type.lower()

    if shot_type not in available_shot_types:
        raise ValueError(f"Invalid shot type. Available types are: {', '.join(available_shot_types)}")

    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute('''
        SELECT * FROM game_shots
        WHERE pattern_of_play = ? AND season = ?
        ORDER BY shot_order ASC
    ''', (shot_type.lower(),season))
    
    rows = cursor.fetchall()
    conn.close()

    print(f'{len(rows)} {shot_type} shots retrieved.')
    return rows

def get_total_psxg_by_team_and_season(team_id, season):
    """
    Retrieves the total post-shot expected goals (PSxG) for a given team and season.

    Args:
        team_id (str): The unique identifier for the team.
        season (int): The season to filter shot data by.

    Returns:
        float: The total PSxG value for the specified team and season.
    """
    validate_id(team_id)
    validate_season(season)
    print(f'Fetching total PSxG for team {team_id} in season {season}...')
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute('''
        SELECT shot_psxg FROM game_shots
        WHERE team_id = ? AND season = ?
    ''', (team_id, season))
    
    rows = cursor.fetchall()
    conn.close()

    total_psxg = sum(row['shot_psxg'] for row in rows if row['shot_psxg'] is not None)
    print(f'Total PSxG for team {team_id} in season {season}: {total_psxg:.2f}')
    return total_psxg

def get_total_psxg_by_game_id(game_id):
    """
    Retrieves the total post-shot expected goals (PSxG) for both teams in a specific game.

    Args:
        game_id (str): The unique identifier for the game.

    Returns:
        dict[str, float]: A dictionary mapping team IDs to their total PSxG values for the game.
    """
    validate_id(game_id)
    print(f'Fetching total PSxG for both teams in game {game_id}...')
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute('''
        SELECT team_id, shot_psxg
        FROM game_shots
        WHERE game_id = ?
    ''', (game_id,))

    psxg_by_team = {}
    for row in cursor.fetchall():
        team_id = row['team_id']
        psxg = row['shot_psxg'] or 0.0
        psxg_by_team[team_id] = psxg_by_team.get(team_id, 0.0) + psxg

    conn.close()

    for team_id, total in psxg_by_team.items():
        print(f'Team {team_id} total PSxG: {round(total, 2)}')

    return {team_id: round(total, 2) for team_id, total in psxg_by_team.items()}

def get_total_shots_by_game_id(game_id):
    """
    Retrieves the total number of shots taken by each team in a specific game.

    Args:
        game_id (str): The unique identifier for the game to fetch shot counts for.

    Returns:
        dict[str, int]: A dictionary mapping team IDs to the total number of shots 
        they took in the specified game.
    """
    validate_id(game_id)
    print(f'Fetching total shots for both teams in game {game_id}...')
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute('''
        SELECT team_id
        FROM game_shots
        WHERE game_id = ?
    ''', (game_id,))

    shots_by_team = {}
    for row in cursor.fetchall():
        team_id = row['team_id']
        shots_by_team[team_id] = shots_by_team.get(team_id, 0) + 1

    conn.close()

    for team_id, total in shots_by_team.items():
        print(f'Team {team_id} total shots: {total}')

    return shots_by_team


def get_total_shots_on_target_by_game_id(game_id):
    """
    Retrieves the total number of shots on target for both teams in a specific game.

    Args:
        game_id (str): The unique identifier for the game to analyze.

    Returns:
        dict[str, int]: A dictionary where each key is a team_id and the corresponding value 
        is the count of shots on target for that team. A shot is considered on target if:
            - It is a goal OR has a non-zero PSxG value,
            - It was not blocked,
            - It has a valid (non-null and > 0) PSxG value.
    """
    validate_id(game_id)
    print(f'Fetching total shots on target for both teams in game {game_id}...')
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute('''
        SELECT *
        FROM game_shots
        WHERE game_id = ?
    ''', (game_id,))

    shots_on_target_by_team = {}
    for row in cursor.fetchall():
        team_id = row['team_id']
        goal = row['goal']
        psxg = row['shot_psxg']
        blocked = row['blocked']

        is_on_target = (
            (goal == 1 or (psxg is not None and psxg > 0)) and
            (blocked is None or blocked == 0) and
            (psxg is not None and psxg > 0)
        )

        if is_on_target:
            shots_on_target_by_team[team_id] = shots_on_target_by_team.get(team_id, 0) + 1

    conn.close()

    for team_id, total in shots_on_target_by_team.items():
        print(f'Team {team_id} shots on target: {total}')

    return shots_on_target_by_team

def get_shots_for_team(team_id, season):
    """
    Retrieves all shot records for a specific team in a given season.

    Args:
        team_id (str): The unique identifier for the team.
        season (int): The season to fetch shot data for.

    Returns:
        list[sqlite3.Row]: A list of shot records ordered by game and shot sequence.
    """
    validate_id(team_id)
    print(f'Fetching all shots for team {team_id} in season {season}...')
    
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute('''
        SELECT * FROM game_shots
        WHERE team_id = ?
          AND season = ?
        ORDER BY game_id ASC, shot_order ASC
    ''', (team_id, season))
    
    rows = cursor.fetchall()
    conn.close()

    print(f'{len(rows)} shots retrieved for team {team_id} in season {season}.')
    return rows


def get_avg_shots_for_team(team_id, season):
    """
    Calculates the average number of shots per game for a team in a given season.

    Args:
        team_id (str): The unique identifier for the team.
        season (int): The season to consider.

    Returns:
        float: The average number of shots per game, or 0.0 if no data found.
    """
    validate_id(team_id)
    print(f'Calculating average shots per game for team {team_id} in season {season}...')

    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()

    # Total shots taken by the team
    cursor.execute('''
        SELECT COUNT(*) FROM game_shots
        WHERE team_id = ?
          AND season = ?
    ''', (team_id, season))
    total_shots = cursor.fetchone()[0]

    # Total games the team played in
    cursor.execute('''
        SELECT COUNT(DISTINCT game_id) FROM game_shots
        WHERE team_id = ?
          AND season = ?
    ''', (team_id, season))
    total_games = cursor.fetchone()[0]

    conn.close()

    avg_shots = total_shots / total_games if total_games > 0 else 0.0
    print(f'Team {team_id} averaged {avg_shots:.2f} shots per game over {total_games} games.')
    return avg_shots