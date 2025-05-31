from api import make_asa_api_call
from .data_util import get_db_path, validate_id, validate_season
import sqlite3

def insert_all_games_xgoals_by_season(season): # pragma: no cover
    """
    Insert xGoals data for all games in a given season.

    This function calls the ASA API to retrieve expected goals data for all 
    regular season games in the specified NWSL season. It parses the response 
    and inserts each game record into the local `games_xgoals` table using 
    INSERT OR REPLACE.

    Args:
        season (int): 
            The season year (e.g., 2024) for which game xGoals data should be inserted.

    Returns:
        None
    """
    validate_season(season)
    print('Inserting games by season for:', season)
    api_string = 'nwsl/games/xgoals?season_name={}&stage_name=Regular Season'.format(str(season))
    games_data = make_asa_api_call(api_string)[1]
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    for game in games_data:
        game_id = game.get('game_id', 'Unknown Game ID')
        date_time_utc = game.get('date_time_utc', 'Unknown Date/Time')
        home_team_id = game.get('home_team_id', 'Unknown Home Team ID')
        home_goals = game.get('home_goals', 0)
        home_team_xgoals = round(game.get('home_team_xgoals', 0.0), 2)
        home_player_xgoals = round(game.get('home_player_xgoals', 0.0), 2)
        away_team_id = game.get('away_team_id', 'Unknown Away Team ID')
        away_goals = game.get('away_goals', 0)
        away_team_xgoals = round(game.get('away_team_xgoals', 0.0), 2)
        away_player_xgoals = round(game.get('away_player_xgoals', 0.0), 2)
        goal_difference = game.get('goal_difference', 0)
        team_xgoal_difference = game.get('team_xgoal_difference', 0.0)
        player_xgoal_difference = game.get('player_xgoal_difference', 0.0)
        final_score_difference = game.get('final_score_difference', 0)
        home_xpoints = round(game.get('home_xpoints', 0.0), 2)
        away_xpoints = round(game.get('away_xpoints', 0.0), 2)
    
        cursor.execute('''
        INSERT OR REPLACE INTO games_xgoals (
            game_id, date_time_utc, home_team_id, home_goals, home_team_xgoals,
            home_player_xgoals, away_team_id, away_goals, away_team_xgoals,
            away_player_xgoals, goal_difference, team_xgoal_difference,
            player_xgoal_difference, final_score_difference, home_xpoints, away_xpoints, season
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            game_id, date_time_utc, home_team_id, home_goals, home_team_xgoals,
            home_player_xgoals, away_team_id, away_goals, away_team_xgoals,
            away_player_xgoals, goal_difference, team_xgoal_difference,
            player_xgoal_difference, final_score_difference, home_xpoints, away_xpoints, int(season)
        ))
        conn.commit()
    cursor.close()
    conn.close()

def get_all_games_xgoals_by_season(season):
    """
    Retrieve xGoals data for all games in a given season.

    This function queries the local SQLite database for all rows in the 
    `games_xgoals` table where the season matches the input year.

    Args:
        season (int): 
            The season year (e.g., 2024) to retrieve game xGoals data for.

    Returns:
        list[sqlite3.Row]: 
            A list of row objects, each containing xGoals data for one game.
    """
    validate_season(season)
    print('Fetching games xgoals for: {}'.format(season))
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM games_xgoals WHERE season = ?', (season,))
    rows = cursor.fetchall()
    conn.commit()
    conn.close()
    print('Games xgoals returned.')
    return rows

def get_game_xgoals_by_id(game_id):
    """
    Retrieve xGoals data for a single game by its ID.

    This function queries the local SQLite database for a single row in the 
    `games_xgoals` table that matches the specified game ID.

    Args:
        game_id (str): 
            The unique identifier of the game to retrieve xGoals data for.

    Returns:
        sqlite3.Row or None: 
            A row object containing the game xGoals data, or None if no match is found.
    """
    validate_id(game_id)
    print('Fetching game xgoals for: {}'.format(game_id))
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM games_xgoals WHERE game_id = ?', (game_id,))
    row = cursor.fetchone()
    conn.commit()
    conn.close()
    print('Game xgoals returned.')
    return row