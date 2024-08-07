import sqlite3

def create_tables():
    # Connect to SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect('db/nwsl.db')
    cursor = conn.cursor()

    # Create the players table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS player_info (
        player_id TEXT PRIMARY KEY,
        player_name TEXT,
        birth_date TEXT,
        height_ft INTEGER,
        height_in INTEGER,
        nationality TEXT,
        primary_broad_position TEXT,
        primary_general_position TEXT,
        secondary_broad_position TEXT,
        secondary_general_position TEXT
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS team_info (
        team_id TEXT PRIMARY KEY,
        team_name TEXT,
        team_short_name TEXT,
        team_abbreviation TEXT
    )              
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS player_seasons (
        season_player_id TEXT PRIMARY KEY,
        player_id TEXT,
        year INTEGER,
        FOREIGN KEY (player_id) REFERENCES player_info(player_id)
    )              
    ''')

    # Commit the changes and close the connection
    conn.commit()
    conn.close()