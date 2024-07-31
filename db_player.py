from api import make_api_call
import sqlite3

def insert_all_players_info():
    print('Attempting  to insert all players info...')
    players_data = make_api_call('nwsl/players')[1]
    conn = sqlite3.connect('nwsl.db')
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
        season_name = player.get("season_name", [])

        # If the season is empty, it is returned as a dict. Otherwise it is a list.
        if isinstance(season_name, list):
            seasons = ", ".join(season_name) if season_name else "No Seasons Available"
        else:
            seasons = "No Seasons Available"
        
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

def get_all_players_info():
    print('Fetching all players info from the database...')
    conn = sqlite3.connect('nwsl.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM player_info')
    rows = cursor.fetchall()
    conn.commit()
    conn.close()
    print('All players info returned.')
    return rows