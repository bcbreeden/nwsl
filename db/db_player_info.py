from api import make_api_call
import sqlite3

def insert_all_players_info():
    print('Attempting  to insert all players info...')
    players_data = make_api_call('nwsl/players')[1]
    conn = sqlite3.connect('db/nwsl.db')
    cursor = conn.cursor()
    for player in players_data:
        player_id = player.get("player_id", "Unknown ID")
        player_name = player.get("player_name", "Unknown Name")
        nationality = player.get("nationality", "Unknown Nationality")
        birth_date = player.get("birth_date", "Unknown Birth Date")
        height_ft = player.get("height_ft", "Unknown Height (ft)")
        height_in = player.get("height_in", "Unknown Height (in)")
        primary_broad_position = player.get("primary_broad_position", "Unknown Primary Broad Position")
        primary_general_position = player.get("primary_general_position", "Unknown Primary General Position")
        secondary_broad_position = player.get("secondary_broad_position", "Unknown Secondary Broad Position")
        secondary_general_position = player.get("secondary_general_position", "Unknown Secondary General Position")
        season_names = player.get("season_name", [])

        # If the season is empty, it is returned as a dict. Otherwise it is a list.
        if isinstance(season_names, list):
            for season in season_names:
                insert_player_season_entry(player_id, season, cursor)
        elif isinstance(season_names, str):
            insert_player_season_entry(player_id, season_names, cursor)
        else:
            print('No season associated with player:', player_id)
        
        cursor.execute('''
        INSERT OR REPLACE INTO player_info (
            player_id, player_name, birth_date, height_ft, height_in, nationality,
            primary_broad_position, primary_general_position, secondary_broad_position,
            secondary_general_position
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            player_id, player_name, birth_date, height_ft, height_in, nationality,
            primary_broad_position, primary_general_position, secondary_broad_position,
            secondary_general_position
        ))
        conn.commit()
    conn.close()
    print('All players info successfully entered into the database.')

def insert_player_season_entry(player_id, season, cursor):
    season_int = int(season)
    season_player_id = '{}{}'.format(player_id, season)
    cursor.execute('''
        INSERT OR REPLACE INTO player_seasons (
            season_player_id, player_id, year
        ) VALUES (?, ?, ?)
        ''', (
            season_player_id, player_id, season_int
        ))

def get_all_players_info():
    print('Fetching all players info from the database...')
    conn = sqlite3.connect('db/nwsl.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM player_info')
    rows = cursor.fetchall()
    conn.commit()
    conn.close()
    print('All players info returned.')
    return rows

def get_all_player_seasons():
    print('Fetching all player seasons from the database...')
    conn = sqlite3.connect('db/nwsl.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM player_seasons')
    rows = cursor.fetchall()
    conn.commit()
    conn.close()
    print('All players info returned.')
    return rows

def get_player_seasons(player_id):
    print('Fetching seasons for:', player_id)
    conn = sqlite3.connect('db/nwsl.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM player_seasons WHERE player_id = ?', (player_id,))
    rows = cursor.fetchall()
    conn.commit()
    conn.close()
    print('Player seasons info returned.')
    return rows

def get_player_info_by_id(player_id):
    print('Fetching player info for:', player_id)
    conn = sqlite3.connect('db/nwsl.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM player_info WHERE player_id = ?', (player_id,))
    row = cursor.fetchone()
    conn.commit()
    conn.close()
    print('Players info returned.')
    return row
