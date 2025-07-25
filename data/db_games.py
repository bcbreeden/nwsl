from api import make_asa_api_call
from .data_util import get_db_path, validate_id, validate_season, convert_utc_to_est
import sqlite3

def insert_all_games_by_season(season): # pragma: no cover
    """
    Inserts all regular season games for a given NWSL season into the local database.

    Args:
        season (int): The season year to fetch and store games for.

    Returns:
        None
    """
    validate_season(season)
    print('Inserting games by season for:', season)
    api_string = 'nwsl/games?season_name={}&stage_name=Regular Season'.format(str(season))
    games_data = make_asa_api_call(api_string)[1]
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    for game in games_data:
        game_id = game.get('game_id', 'Unknown Game ID')
        date_time_utc = game.get('date_time_utc', 'Unknown Date/Time')
        date_time_est = convert_utc_to_est(date_time_utc)
        home_score = game.get('home_score', 0)
        away_score = game.get('away_score', 0)
        home_team_id = game.get('home_team_id', 'Unknown Home Team ID')
        away_team_id = game.get('away_team_id', 'Unknown Away Team ID')
        referee_id = game.get('referee_id', 'Unknown Referee ID')
        stadium_id = game.get('stadium_id', 'Unknown Stadium ID')
        home_manager_id = game.get('home_manager_id', 'Unknown Home Manager ID')
        away_manager_id = game.get('away_manager_id', 'Unknown Away Manager ID')
        expanded_minutes = game.get('expanded_minutes', 0)
        season_name = game.get('season_name', 'Unknown Season')
        matchday = game.get('matchday', 0)
        attendance = game.get('attendance', 0)
        knockout_game = game.get('knockout_game', False)
        status = game.get('status', 'Unknown Status')
        last_updated_utc = game.get('last_updated_utc', 'Unknown Last Updated Time')
        last_updated_est = convert_utc_to_est(last_updated_utc)

        cursor.execute('''
        INSERT OR REPLACE INTO games (
            game_id, date_time_utc, date_time_est, home_score, away_score, 
            home_team_id, away_team_id, referee_id, stadium_id, 
            home_manager_id, away_manager_id, expanded_minutes, 
            season_name, matchday, attendance, knockout_game, status,
            last_updated_utc, last_updated_est, season
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            game_id, date_time_utc, date_time_est, home_score, away_score, 
            home_team_id, away_team_id, referee_id, stadium_id, 
            home_manager_id, away_manager_id, expanded_minutes, 
            season_name, matchday, attendance, knockout_game, status,
            last_updated_utc, last_updated_est, int(season)
        ))
        conn.commit()
    cursor.close()
    conn.close()

def get_all_games_by_season(season):
    """
    Retrieves all regular season games for a given NWSL season from the local database,
    including joined metadata such as team names, abbreviations, and stadium name.

    Args:
        season (int): The season year to query games for.

    Returns:
        list[sqlite3.Row]: A list of games with enriched metadata, ordered by matchday descending.
    """
    validate_season(season)
    print('Fetching games for: {}'.format(season))
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    query = '''
        SELECT
            gm.*,
            home_team.team_name AS home_team_name,
            home_team.team_short_name AS home_team_short_name,
            home_team.team_abbreviation AS home_team_abbreviation,
            away_team.team_name AS away_team_name,
            away_team.team_short_name AS away_team_short_name,
            away_team.team_abbreviation AS away_team_abbreviation,
            stadium.stadium_name AS stadium_name
        FROM
            games AS gm
        JOIN
            team_info AS home_team
            ON gm.home_team_id = home_team.team_id
        JOIN
            team_info AS away_team
            ON gm.away_team_id = away_team.team_id
        LEFT JOIN
            stadium_info AS stadium
            ON gm.stadium_id = stadium.stadium_id
        WHERE
            gm.season = ?
        ORDER BY
            gm.matchday DESC
    '''


    cursor.execute(query, (season,))
    rows = cursor.fetchall()
    conn.commit()
    conn.close()
    print('Games returned.')
    return rows

def get_game_by_id(game_id):
    """
    Retrieves detailed game information for a given game ID, including team metadata.

    Args:
        game_id (str): The unique identifier of the game to retrieve.

    Returns:
        sqlite3.Row | None: A single row containing game and team details if found, otherwise None.
    """
    validate_id(game_id)
    print('Fetching game: {}'.format(game_id))
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    query = '''
        SELECT
            gm.*,
            home_team.team_name AS home_team_name,
            home_team.team_short_name AS home_team_short_name,
            home_team.team_abbreviation AS home_team_abbreviation,
            away_team.team_name AS away_team_name,
            away_team.team_short_name AS away_team_short_name,
            away_team.team_abbreviation AS away_team_abbreviation
        FROM
            games AS gm
        JOIN
            team_info AS home_team
            ON gm.home_team_id = home_team.team_id
        JOIN
            team_info AS away_team
            ON gm.away_team_id = away_team.team_id
        WHERE
            gm.game_id = ?
    '''
    cursor.execute(query, (game_id,))
    row = cursor.fetchone()
    conn.commit()
    conn.close()
    print('Game returned.')
    return row

def get_game_ids_by_season(season):
    """
    Retrieves all game IDs for a given season.

    Args:
        season (int): The season year to filter games by.

    Returns:
        list[str]: A list of game ID strings for the specified season.
    """
    validate_season(season)
    print('Fetching game IDs for: {}'.format(season))
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    query = '''
        SELECT
            gm.game_id
        FROM
            games AS gm
        WHERE
            gm.season = ?
    '''
    cursor.execute(query, (season,))
    rows = cursor.fetchall()
    game_ids = [row['game_id'] for row in rows]
    conn.commit()
    conn.close()
    return game_ids

def get_latest_manager_id_by_team_and_season(team_id, season):
    """
    Retrieves the most recent manager ID for a given team in a specific season.

    Args:
        team_id (str): The unique identifier of the team.
        season (int): The season to search within.

    Returns:
        str or None: The manager ID of the most recent match for the team in the specified season.
                    Returns None if no matches are found.
    """
    validate_season(season)
    validate_id(team_id)
    print(f'Fetching most recent manager for team: {team_id} in season: {season}')
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    query = '''
        SELECT
            CASE
                WHEN home_team_id = ? THEN home_manager_id
                ELSE away_manager_id
            END AS manager_id
        FROM games
        WHERE season = ?
          AND (home_team_id = ? OR away_team_id = ?)
        ORDER BY date_time_utc DESC
        LIMIT 1;
    '''
    
    cursor.execute(query, (team_id, season, team_id, team_id))
    result = cursor.fetchone()
    
    conn.close()
    
    return result[0] if result else None

def get_team_record_by_season(team_id, season):
    """
    Retrieves the win-loss-draw record for a team in a specific season.

    Args:
        team_id (str): The unique identifier for the team.
        season (int): The season to evaluate the team record in.

    Returns:
        dict: A dictionary containing:
            - 'wins' (int): Total number of games won by the team.
            - 'losses' (int): Total number of games lost by the team.
            - 'draws' (int): Total number of games that ended in a draw.

    Raises:
        ValueError: If `team_id` is not a non-empty string or `season` is not a valid integer.
    """
    validate_season(season)
    validate_id(team_id)
    print(f'Fetching record for team: {team_id} in season: {season}')
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    query = '''
        SELECT
            SUM(CASE
                    WHEN (home_team_id = ? AND home_score > away_score)
                      OR (away_team_id = ? AND away_score > home_score)
                    THEN 1 ELSE 0 END) AS wins,
            SUM(CASE
                    WHEN (home_team_id = ? AND home_score < away_score)
                      OR (away_team_id = ? AND away_score < home_score)
                    THEN 1 ELSE 0 END) AS losses,
            SUM(CASE
                    WHEN home_score = away_score
                         AND (home_team_id = ? OR away_team_id = ?)
                    THEN 1 ELSE 0 END) AS draws
        FROM games
        WHERE season = ?
          AND (home_team_id = ? OR away_team_id = ?)
    '''

    cursor.execute(query, (
        team_id, team_id,  # wins
        team_id, team_id,  # losses
        team_id, team_id,  # draws
        season,
        team_id, team_id   # WHERE clause
    ))

    result = cursor.fetchone()
    conn.close()

    return {
        'wins': result[0],
        'losses': result[1],
        'draws': result[2]
    }


def get_team_game_results(team_id, season):
    """
    Retrieves a team's match results for a given season.

    Args:
        team_id (str): The unique identifier of the team.
        season (int): The season to filter match results by.

    Returns:
        list[dict]: A list of dictionaries, each representing a game result with fields for:
            - game_id (str): The unique match ID.
            - home_game (bool): True if the team was the home side, otherwise False.
            - result (str): One of "win", "loss", or "draw".
            - opponent (str): The opposing team's ID.
            - opponent_name (str): The full name of the opposing team.
            - opponent_short_name (str): The short name of the opposing team.
            - opponent_abbreviation (str): The team abbreviation of the opponent.
            - goals_scored (int): Goals scored by the team.
            - goals_against (int): Goals conceded by the team.
            - date_time_est (str): The local Eastern time of the match.
    """
    validate_season(season)
    validate_id(team_id)
    print(f'Fetching game results for team: {team_id} in season: {season}')
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    query = '''
        SELECT
            g.game_id, 
            g.home_team_id,
            g.away_team_id,
            g.home_score,
            g.away_score,
            g.date_time_est,
            t.team_id AS opponent_id,
            t.team_name AS opponent_name,
            t.team_short_name AS opponent_short_name,
            t.team_abbreviation AS opponent_abbreviation
        FROM games g
        JOIN team_info t
          ON (g.home_team_id = ? AND t.team_id = g.away_team_id)
          OR (g.away_team_id = ? AND t.team_id = g.home_team_id)
        WHERE g.season = ?
          AND (g.home_team_id = ? OR g.away_team_id = ?)
          AND g.home_score IS NOT NULL
          AND g.away_score IS NOT NULL
        ORDER BY g.date_time_utc DESC
    '''

    cursor.execute(query, (
        team_id, team_id,
        season,
        team_id, team_id
    ))

    rows = cursor.fetchall()
    conn.close()

    results = []

    for row in rows:
        is_home = row['home_team_id'] == team_id
        goals_scored = row['home_score'] if is_home else row['away_score']
        goals_against = row['away_score'] if is_home else row['home_score']

        if goals_scored > goals_against:
            result = "win"
        elif goals_scored < goals_against:
            result = "loss"
        else:
            result = "draw"

        results.append({
            "game_id": row['game_id'],
            "home_game": is_home,
            "result": result,
            "opponent": row['opponent_id'],
            "opponent_name": row['opponent_name'],
            "opponent_short_name": row['opponent_short_name'],
            "opponent_abbreviation": row['opponent_abbreviation'],
            "goals_scored": goals_scored,
            "goals_against": goals_against,
            "date_time_est": row['date_time_est']
        })

    return results

def get_most_recent_home_stadium_id(team_id, season):
    """
    Retrieves the stadium ID of the most recent completed home game for a given team and season.

    Args:
        team_id (str): The unique identifier for the home team.
        season (int): The season to search within.

    Returns:
        str | None: The stadium ID of the most recent home game, or None if no matching game is found.
    """
    validate_season(season)
    validate_id(team_id)
    print(f'Getting most recent home game stadium for team {team_id} in season {season}')
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    query = '''
        SELECT stadium_id
        FROM games
        WHERE season = ?
          AND home_team_id = ?
          AND home_score IS NOT NULL
          AND away_score IS NOT NULL
        ORDER BY date_time_utc DESC
        LIMIT 1
    '''

    cursor.execute(query, (season, team_id))
    result = cursor.fetchone()
    conn.close()

    return result[0] if result else None