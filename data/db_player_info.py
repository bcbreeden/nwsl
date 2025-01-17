from api import make_asa_api_call
import sqlite3

def insert_all_players_info():
    """
    Fetches player data from the NWSL API and inserts it into an SQLite database.

    This function retrieves player information using the `make_asa_api_call` function,
    processes the data to extract relevant fields, and inserts or updates the data
    in the `player_info` table of the database.

    Args:
        None
    """
    print('Attempting  to insert all players info...')
    players_data = make_asa_api_call('nwsl/players')[1]
    conn = sqlite3.connect('data/nwsl.db')
    cursor = conn.cursor()
    for player in players_data:
        player_id = player.get('player_id', 'Unknown ID')
        player_name = player.get('player_name', 'Unknown Name')
        player_first_name = _split_player_name(player_name)[0]
        player_last_name = _split_player_name(player_name)[1]
        nationality = player.get('nationality', 'Unknown Nationality')
        birth_date = player.get('birth_date', 'Unknown Birth Date')
        height_ft = player.get('height_ft', 'Unknown Height (ft)')
        height_in = player.get('height_in', 'Unknown Height (in)')
        primary_broad_position = player.get('primary_broad_position', 'Unknown Primary Broad Position')
        primary_general_position = player.get('primary_general_position', 'Unknown Primary General Position')
        secondary_broad_position = player.get('secondary_broad_position', 'Unknown Secondary Broad Position')
        secondary_general_position = player.get('secondary_general_position', 'Unknown Secondary General Position')
        season_names = player.get('season_name', [])

        # If the season is empty, it is returned as a dict. Otherwise it is a list.
        if isinstance(season_names, list):
            for season in season_names:
                _insert_player_season_entry(player_id, season, cursor)
        elif isinstance(season_names, str):
            _insert_player_season_entry(player_id, season_names, cursor)
        else:
            print('No season associated with player:', player_id)
        
        cursor.execute('''
        INSERT OR REPLACE INTO player_info (
            player_id, player_name, player_first_name, player_last_name, birth_date, height_ft, height_in, nationality,
            primary_broad_position, primary_general_position, secondary_broad_position,
            secondary_general_position
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            player_id, player_name, player_first_name, player_last_name, birth_date, height_ft, height_in, nationality,
            primary_broad_position, primary_general_position, secondary_broad_position,
            secondary_general_position
        ))
        conn.commit()
    conn.close()
    print('All players info successfully entered into the database.')

def _insert_player_season_entry(player_id, season, cursor):
    """
    Inserts or updates a player's season data into the `player_seasons` table.

    Args:
        player_id (str): The unique identifier for the player.
        season (str): The season year as a string.
        cursor (sqlite3.Cursor): The database cursor to execute SQL commands.

    Notes:
        - Constructs a unique `season_player_id` by concatenating the `player_id`
          and the `season`.
        - The `player_seasons` table is expected to have columns `season_player_id`,
          `player_id`, and `year`.
    """
    season_int = int(season)
    season_player_id = '{}{}'.format(player_id, season)
    cursor.execute('''
        INSERT OR REPLACE INTO player_seasons (
            season_player_id, player_id, year
        ) VALUES (?, ?, ?)
        ''', (
            season_player_id, player_id, season_int
        ))

def _split_player_name(name):
    """
    Splits a player's full name into first and last names.

    Args:
        name (str): The full name of the player.

    Returns:
        tuple: A tuple containing the first name and last name as strings. If the 
               name does not contain a space, the first name will be an empty string 
               and the last name will contain the full name.

    Example:
        ("Alex Morgan")
        ('Alex', 'Morgan')
        ("Kerolin")
        ('', 'Kerolin')
    """
    words = name.split(' ', 1)  # Split at the first space
    if len(words) > 1:
        first_name = words[0]
        last_name = words[1]
    else:
        first_name = ''
        last_name = words[0]
    
    return [first_name, last_name]

def get_all_players_info():
    """
    Retrieves all player information from the `player_info` table in the SQLite database.

    This function connects to the database, fetches all rows from the `player_info` table,
    and returns them as a list of SQLite Row objects for easy access to column data.

    Args:
        None

    Returns:
        list: A list of SQLite Row objects containing player information.
    """
    print('Fetching all players info from the database...')
    conn = sqlite3.connect('data/nwsl.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM player_info')
    rows = cursor.fetchall()
    conn.commit()
    conn.close()
    print('All players info returned.')
    return rows

def get_all_player_seasons():
    """
    Retrieves all player season data from the `player_seasons` table in the SQLite database.

    This function connects to the database, fetches all rows from the `player_seasons` table,
    and returns them as a list of SQLite Row objects for easy access to column data.

    Args:
        None

    Returns:
        list: A list of SQLite Row objects containing player season data.
    """
    print('Fetching all player seasons from the database...')
    conn = sqlite3.connect('data/nwsl.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM player_seasons')
    rows = cursor.fetchall()
    conn.commit()
    conn.close()
    print('All players info returned.')
    return rows

def get_player_seasons(player_id):
    """
    Retrieves season data for a specific player from the `player_seasons` table 
    in the SQLite database.

    Args:
        player_id (str): The unique identifier of the player whose season data 
                         is to be retrieved.

    Returns:
        list: A list of SQLite Row objects containing season data for the specified player.
    """
    print('Fetching seasons for:', player_id)
    conn = sqlite3.connect('data/nwsl.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM player_seasons WHERE player_id = ?', (player_id,))
    rows = cursor.fetchall()
    conn.commit()
    conn.close()
    print('Player seasons info returned.')
    return rows

def get_player_info_by_id(player_id):
    """
    Retrieves information for a specific player from the `player_info` table 
    in the SQLite database.

    Args:
        player_id (str): The unique identifier of the player whose information 
                         is to be retrieved.

    Returns:
        sqlite3.Row: A Row object containing the player's information, or None 
                     if no matching record is found.
    """
    print('Fetching player info for:', player_id)
    conn = sqlite3.connect('data/nwsl.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM player_info WHERE player_id = ?', (player_id,))
    row = cursor.fetchone()
    conn.commit()
    conn.close()
    print('Players info returned.')
    return row
