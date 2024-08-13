import sqlite3

def create_tables():
    # Connect to SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect('db/nwsl.db')
    cursor = conn.cursor()

    print('Starting to build tables...')
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

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS player_xgoals (
        player_id TEXT PRIMARY KEY,
        team_id TEXT,
        general_position TEXT,
        minutes_played INTEGER,
        shots INTEGER,
        shots_on_target INTEGER,
        goals INTEGER,
        xgoals REAL,
        xplace REAL,
        goals_minus_xgoals REAL,
        key_passes INTEGER,
        primary_assists INTEGER,
        xassists REAL,
        primary_assists_minus_xassists REAL,
        xgoals_plus_xassists REAL,
        points_added REAL,
        xpoints_added REAL,
        season INTEGER,
        FOREIGN KEY (team_id) REFERENCES team_info(team_id)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS player_xpass (
        player_id TEXT PRIMARY KEY,
        team_id TEXT,
        general_position TEXT,
        minutes_played INTEGER,
        attempted_passes INTEGER,
        pass_completion_percentage REAL,
        xpass_completion_percentage REAL,
        passes_completed_over_expected REAL,
        passes_completed_over_expected_p100 REAL,
        avg_distance_yds REAL,
        avg_vertical_distance_yds REAL,
        share_team_touches REAL,
        count_games INTEGER,
        season INTEGER,
        FOREIGN KEY (team_id) REFERENCES team_info(team_id)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS player_goals_added (
        player_id TEXT PRIMARY KEY,
        team_id TEXT,
        general_position TEXT,
        minutes_played INTEGER,
        dribbling_goals_added_raw REAL,
        dribbling_goals_added_above_avg REAL,
        dribbling_count_actions INTEGER,
        fouling_goals_added_raw REAL,
        fouling_goals_added_above_avg REAL,
        fouling_count_actions INTEGER,
        interrupting_goals_added_raw REAL,
        interrupting_goals_added_above_avg REAL,
        interrupting_count_actions INTEGER,
        passing_goals_added_raw REAL,
        passing_goals_added_above_avg REAL,
        passing_count_actions INTEGER,
        receiving_goals_added_raw REAL,
        receiving_goals_added_above_avg REAL,
        receiving_count_actions INTEGER,
        shooting_goals_added_raw REAL,
        shooting_goals_added_above_avg REAL,
        shooting_count_actions INTEGER,
        season INTEGER,
        FOREIGN KEY (team_id) REFERENCES team_info(team_id)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS goalkeeper_xgoals (
        player_id TEXT PRIMARY KEY,
        team_id TEXT,
        minutes_played INTEGER,
        shots_faced INTEGER,
        goals_conceded INTEGER,
        saves INTEGER,
        share_headed_shots REAL,
        xgoals_gk_faced REAL,
        goals_minus_xgoals_gk REAL,
        goals_divided_by_xgoals_gk  REAL,
        season INTEGER,
        FOREIGN KEY (team_id) REFERENCES team_info(team_id)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS goalkeeper_goals_added (
        player_id TEXT PRIMARY KEY,
        team_id TEXT,
        minutes_played INTEGER,
        claiming_goals_added_raw REAL,
        claiming_goals_added_above_avg REAL,
        claiming_count_actions INTEGER,
        fielding_goals_added_raw REAL,
        fielding_goals_added_above_avg REAL,
        fielding_count_actions INTEGER,
        handling_goals_added_raw REAL,
        handling_goals_added_above_avg REAL,
        handling_count_actions INTEGER,
        passing_goals_added_raw REAL,
        passing_goals_added_above_avg REAL,
        passing_count_actions INTEGER,
        shotstopping_goals_added_raw REAL,
        shotstopping_goals_added_above_avg REAL,
        shotstopping_count_actions INTEGER,
        sweeping_goals_added_raw REAL,
        sweeping_goals_added_above_avg REAL,
        sweeping_count_actions INTEGER,
        season INTEGER,
        FOREIGN KEY (team_id) REFERENCES team_info(team_id)
    )
    ''')

    # Commit the changes and close the connection
    conn.commit()
    conn.close()
    print('Tables built.')