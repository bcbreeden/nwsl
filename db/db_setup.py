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
        player_first_name TEXT,
        player_last_name TEXT,
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
        id TEXT PRIMARY KEY,
        player_id TEXT,
        team_id TEXT,
        general_position TEXT,
        minutes_played INTEGER,
        shots INTEGER,
        shots_on_target INTEGER,
        shots_on_target_perc INTEGER,
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
        FOREIGN KEY (team_id) REFERENCES team_info(team_id),
        FOREIGN KEY (player_id) REFERENCES player_info(player_id)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS player_xpass (
        id TEXT PRIMARY KEY,
        player_id TEXT,
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
        FOREIGN KEY (team_id) REFERENCES team_info(team_id),
        FOREIGN KEY (player_id) REFERENCES player_info(player_id)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS player_goals_added (
        id TEXT PRIMARY KEY,
        player_id TEXT,
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
        FOREIGN KEY (team_id) REFERENCES team_info(team_id),
        FOREIGN KEY (player_id) REFERENCES player_info(player_id)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS goalkeeper_xgoals (
        id TEXT PRIMARY KEY,
        player_id TEXT,
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
        FOREIGN KEY (team_id) REFERENCES team_info(team_id),
        FOREIGN KEY (player_id) REFERENCES player_info(player_id)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS goalkeeper_goals_added (
        id PRIMARY KEY, 
        player_id TEXT,
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

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS team_xgoals (
        id TEXT PRIMARY KEY,
        team_id TEXT,
        count_games INTEGER,
        shots_for INTEGER,
        shots_against INTEGER,
        goals_for INTEGER,
        goals_against INTEGER,
        goal_difference INTEGER,
        xgoals_for REAL,
        xgoals_against REAL,
        xgoal_difference REAL,
        goal_difference_minus_xgoal_difference REAL,
        points INTEGER,
        xpoints REAL,
        season INTEGER,
        predicted_points REAL,
        point_diff REAL,
        goalfor_xgoalfor_diff REAL,
        FOREIGN KEY (team_id) REFERENCES team_info(team_id)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS team_xpass (
        id TEXT PRIMARY KEY,
        team_id TEXT,
        count_games INTEGER,
        attempted_passes_for INTEGER,
        pass_completion_percentage_for REAL,
        xpass_completion_percentage_for REAL,
        passes_completed_over_expected_for REAL,
        passes_completed_over_expected_p100_for REAL,
        avg_vertical_distance_for REAL,
        attempted_passes_against INTEGER,
        pass_completion_percentage_against REAL,
        xpass_completion_percentage_against REAL,
        passes_completed_over_expected_against REAL,
        passes_completed_over_expected_p100_against REAL,
        avg_vertical_distance_against REAL,
        passes_completed_over_expected_difference REAL,
        avg_vertical_distance_difference REAL,
        season INTEGER,
        FOREIGN KEY (team_id) REFERENCES team_info(team_id)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS team_goals_added (
        id TEXT PRIMARY KEY,
        team_id TEXT,
        minutes INTEGER,
        dribbling_num_actions_for REAL,          
        dribbling_goals_added_for REAL,
        dribbling_num_actions_against INTEGER,
        dribbling_goals_added_against REAL,
        shooting_num_actions_for REAL,          
        shooting_goals_added_for REAL,
        shooting_num_actions_against INTEGER,
        shooting_goals_added_against REAL,
        passing_num_actions_for REAL,          
        passing_goals_added_for REAL,
        passing_num_actions_against INTEGER,
        passing_goals_added_against REAL,
        interrupting_num_actions_for REAL,          
        interrupting_goals_added_for REAL,
        interrupting_num_actions_against INTEGER,
        interrupting_goals_added_against REAL,
        receiving_num_actions_for REAL,          
        receiving_goals_added_for REAL,
        receiving_num_actions_against INTEGER,
        receiving_goals_added_against REAL,   
        claiming_num_actions_for REAL,          
        claiming_goals_added_for REAL,
        claiming_num_actions_against INTEGER,
        claiming_goals_added_against REAL,
        fouling_num_actions_for REAL,          
        fouling_goals_added_for REAL,
        fouling_num_actions_against INTEGER,
        fouling_goals_added_against REAL,
        season INTEGER,
        FOREIGN KEY (team_id) REFERENCES team_info(team_id)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS games (
        game_id TEXT PRIMARY KEY,
        date_time_utc TEXT,
        home_score INTEGER,
        away_score INTEGER,
        home_team_id TEXT,
        away_team_id TEXT,
        referee_id TEXT,
        stadium_id TEXT,
        home_manager_id TEXT,
        away_manager_id TEXT,
        expanded_minutes INTEGER,
        season_name TEXT,
        matchday INTEGER,
        attendance INTEGER,
        knockout_game BOOLEAN,
        last_updated_utc TEXT,
        season INTEGER,
        FOREIGN KEY (home_team_id) REFERENCES team_info(team_id)
        FOREIGN KEY (away_team_id) REFERENCES team_info(team_id)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS games_xgoals (
        game_id TEXT PRIMARY KEY,
        date_time_utc TEXT,
        home_team_id TEXT,
        home_goals INTEGER,
        home_team_xgoals REAL,
        home_player_xgoals REAL,
        away_team_id TEXT,
        away_goals INTEGER,
        away_team_xgoals REAL,
        away_player_xgoals REAL,
        goal_difference INTEGER,
        team_xgoal_difference REAL,
        player_xgoal_difference REAL,
        final_score_difference INTEGER,
        home_xpoints REAL,
        away_xpoints REAL,
        season INTEGER,
        FOREIGN KEY (home_team_id) REFERENCES team_info(team_id)
        FOREIGN KEY (away_team_id) REFERENCES team_info(team_id)
    )
''')

    # Commit the changes and close the connection
    conn.commit()
    conn.close()
    print('Tables built.')