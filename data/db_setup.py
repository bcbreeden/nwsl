import sqlite3
from .data_util import get_db_path

def create_tables():
    # Connect to SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect(get_db_path())
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
    CREATE TABLE IF NOT EXISTS manager_info (
        manager_id TEXT PRIMARY KEY,
        manager_name TEXT,
        nationality TEXT
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS referee_info (
        referee_id TEXT PRIMARY KEY,
        referee_name TEXT,
        nationality TEXT
    )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stadium_info (
            stadium_id TEXT PRIMARY KEY,
            stadium_name TEXT,
            capacity INTEGER,
            year_built INTEGER,
            roof BOOLEAN,
            turf BOOLEAN,
            street TEXT,
            city TEXT,
            province TEXT,
            country TEXT,
            postal_code TEXT,
            latitude REAL,
            longitude REAL,
            field_x INTEGER,
            field_y INTEGER
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
            xgoals_xassists_per_90 REAL,
            season INTEGER,
            avg_minutes_played REAL,
            avg_shots REAL,
            avg_shots_on_target REAL,
            avg_shots_on_target_perc REAL,
            avg_goals REAL,
            avg_xgoals REAL,
            avg_key_passes REAL,
            avg_primary_assists REAL,
            avg_xassists REAL,
            avg_xgoals_plus_xassists REAL,
            avg_points_added REAL,
            avg_xpoints_added REAL,
            avg_xgoals_xassists_per_90 REAL,
            avg_xplace REAL,
            avg_goals_minus_xgoals REAL,
            avg_primary_assists_minus_xassists REAL,
            min_minutes_played REAL,
            min_shots REAL,
            min_shots_on_target REAL,
            min_shots_on_target_perc REAL,
            min_goals REAL,
            min_xgoals REAL,
            min_xplace REAL,
            min_goals_minus_xgoals REAL,
            min_primary_assists_minus_xassists REAL,
            min_key_passes REAL,
            min_primary_assists REAL,
            min_xassists REAL,
            min_xgoals_plus_xassists REAL,
            min_points_added REAL,
            min_xpoints_added REAL,
            min_xgoals_xassists_per_90 REAL,
            max_minutes_played REAL,
            max_shots REAL,
            max_shots_on_target REAL,
            max_shots_on_target_perc REAL,
            max_goals REAL,
            max_xgoals REAL,
            max_xplace REAL,
            max_goals_minus_xgoals REAL,
            max_primary_assists_minus_xassists REAL,
            max_key_passes REAL,
            max_primary_assists REAL,
            max_xassists REAL,
            max_xgoals_plus_xassists REAL,
            max_points_added REAL,
            max_xpoints_added REAL,
            max_xgoals_xassists_per_90 REAL,
            player_strength REAL,
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
            avg_minutes_played REAL,
            min_minutes_played REAL,
            max_minutes_played REAL,
            avg_attempted_passes REAL,
            min_attempted_passes REAL,
            max_attempted_passes REAL,
            avg_pass_completion_percentage REAL,
            min_pass_completion_percentage REAL,
            max_pass_completion_percentage REAL,
            avg_xpass_completion_percentage REAL,
            min_xpass_completion_percentage REAL,
            max_xpass_completion_percentage REAL,
            avg_passes_completed_over_expected REAL,
            min_passes_completed_over_expected REAL,
            max_passes_completed_over_expected REAL,
            avg_passes_completed_over_expected_p100 REAL,
            min_passes_completed_over_expected_p100 REAL,
            max_passes_completed_over_expected_p100 REAL,
            avg_avg_distance_yds REAL,
            min_avg_distance_yds REAL,
            max_avg_distance_yds REAL,
            avg_avg_vertical_distance_yds REAL,
            min_avg_vertical_distance_yds REAL,
            max_avg_vertical_distance_yds REAL,
            avg_share_team_touches REAL,
            min_share_team_touches REAL,
            max_share_team_touches REAL,
            avg_count_games REAL,
            min_count_games REAL,
            max_count_games REAL,
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
            avg_dribbling_goals_added_raw REAL,
            avg_dribbling_goals_added_above_avg REAL,
            avg_dribbling_count_actions REAL,
            avg_fouling_goals_added_raw REAL,
            avg_fouling_goals_added_above_avg REAL,
            avg_fouling_count_actions REAL,
            avg_interrupting_goals_added_raw REAL,
            avg_interrupting_goals_added_above_avg REAL,
            avg_interrupting_count_actions REAL,
            avg_passing_goals_added_raw REAL,
            avg_passing_goals_added_above_avg REAL,
            avg_passing_count_actions REAL,
            avg_receiving_goals_added_raw REAL,
            avg_receiving_goals_added_above_avg REAL,
            avg_receiving_count_actions REAL,
            avg_shooting_goals_added_raw REAL,
            avg_shooting_goals_added_above_avg REAL,
            avg_shooting_count_actions REAL,
            min_dribbling_goals_added_raw REAL,
            min_dribbling_goals_added_above_avg REAL,
            min_dribbling_count_actions INTEGER,
            min_fouling_goals_added_raw REAL,
            min_fouling_goals_added_above_avg REAL,
            min_fouling_count_actions INTEGER,
            min_interrupting_goals_added_raw REAL,
            min_interrupting_goals_added_above_avg REAL,
            min_interrupting_count_actions INTEGER,
            min_passing_goals_added_raw REAL,
            min_passing_goals_added_above_avg REAL,
            min_passing_count_actions INTEGER,
            min_receiving_goals_added_raw REAL,
            min_receiving_goals_added_above_avg REAL,
            min_receiving_count_actions INTEGER,
            min_shooting_goals_added_raw REAL,
            min_shooting_goals_added_above_avg REAL,
            min_shooting_count_actions INTEGER,
            max_dribbling_goals_added_raw REAL,
            max_dribbling_goals_added_above_avg REAL,
            max_dribbling_count_actions INTEGER,
            max_fouling_goals_added_raw REAL,
            max_fouling_goals_added_above_avg REAL,
            max_fouling_count_actions INTEGER,
            max_interrupting_goals_added_raw REAL,
            max_interrupting_goals_added_above_avg REAL,
            max_interrupting_count_actions INTEGER,
            max_passing_goals_added_raw REAL,
            max_passing_goals_added_above_avg REAL,
            max_passing_count_actions INTEGER,
            max_receiving_goals_added_raw REAL,
            max_receiving_goals_added_above_avg REAL,
            max_receiving_count_actions INTEGER,
            max_shooting_goals_added_raw REAL,
            max_shooting_goals_added_above_avg REAL,
            max_shooting_count_actions INTEGER,
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
        season INTEGER,
        minutes_played INTEGER,
        shots_faced INTEGER,
        goals_conceded INTEGER,
        saves INTEGER,
        share_headed_shots REAL,
        xgoals_gk_faced REAL,
        goals_minus_xgoals_gk REAL,
        goals_divided_by_xgoals_gk REAL,
        save_perc REAL,
        player_strength REAL,

        avg_minutes_played REAL,
        avg_shots_faced REAL,
        avg_goals_conceded REAL,
        avg_saves REAL,
        avg_share_headed_shots REAL,
        avg_xgoals_gk_faced REAL,
        avg_goals_minus_xgoals_gk REAL,
        avg_goals_divided_by_xgoals_gk REAL,
        avg_save_perc REAL,

        min_minutes_played INTEGER,
        min_shots_faced INTEGER,
        min_goals_conceded INTEGER,
        min_saves INTEGER,
        min_share_headed_shots REAL,
        min_xgoals_gk_faced REAL,
        min_goals_minus_xgoals_gk REAL,
        min_goals_divided_by_xgoals_gk REAL,
        min_save_perc REAL,

        max_minutes_played INTEGER,
        max_shots_faced INTEGER,
        max_goals_conceded INTEGER,
        max_saves INTEGER,
        max_share_headed_shots REAL,
        max_xgoals_gk_faced REAL,
        max_goals_minus_xgoals_gk REAL,
        max_goals_divided_by_xgoals_gk REAL,
        max_save_perc REAL,

        FOREIGN KEY (team_id) REFERENCES team_info(team_id),
        FOREIGN KEY (player_id) REFERENCES player_info(player_id)
    )
    ''')


    cursor.execute('''
    CREATE TABLE IF NOT EXISTS goalkeeper_goals_added (
        id PRIMARY KEY, 
        player_id TEXT,
        team_id TEXT,
        season INTEGER,
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
        avg_claiming_goals_added_raw REAL,
        avg_claiming_goals_added_above_avg REAL,
        avg_claiming_count_actions INTEGER,
        avg_fielding_goals_added_raw REAL,
        avg_fielding_goals_added_above_avg REAL,
        avg_fielding_count_actions INTEGER,
        avg_handling_goals_added_raw REAL,
        avg_handling_goals_added_above_avg REAL,
        avg_handling_count_actions INTEGER,
        avg_passing_goals_added_raw REAL,
        avg_passing_goals_added_above_avg REAL,
        avg_passing_count_actions INTEGER,
        avg_shotstopping_goals_added_raw REAL,
        avg_shotstopping_goals_added_above_avg REAL,
        avg_shotstopping_count_actions INTEGER,
        avg_sweeping_goals_added_raw REAL,
        avg_sweeping_goals_added_above_avg REAL,
        avg_sweeping_count_actions INTEGER,
        min_claiming_goals_added_raw REAL,
        min_claiming_goals_added_above_avg REAL,
        min_claiming_count_actions INTEGER,
        min_fielding_goals_added_raw REAL,
        min_fielding_goals_added_above_avg REAL,
        min_fielding_count_actions INTEGER,
        min_handling_goals_added_raw REAL,
        min_handling_goals_added_above_avg REAL,
        min_handling_count_actions INTEGER,
        min_passing_goals_added_raw REAL,
        min_passing_goals_added_above_avg REAL,
        min_passing_count_actions INTEGER,
        min_shotstopping_goals_added_raw REAL,
        min_shotstopping_goals_added_above_avg REAL,
        min_shotstopping_count_actions INTEGER,
        min_sweeping_goals_added_raw REAL,
        min_sweeping_goals_added_above_avg REAL,
        min_sweeping_count_actions INTEGER,
        max_claiming_goals_added_raw REAL,
        max_claiming_goals_added_above_avg REAL,
        max_claiming_count_actions INTEGER,
        max_fielding_goals_added_raw REAL,
        max_fielding_goals_added_above_avg REAL,
        max_fielding_count_actions INTEGER,
        max_handling_goals_added_raw REAL,
        max_handling_goals_added_above_avg REAL,
        max_handling_count_actions INTEGER,
        max_passing_goals_added_raw REAL,
        max_passing_goals_added_above_avg REAL,
        max_passing_count_actions INTEGER,
        max_shotstopping_goals_added_raw REAL,
        max_shotstopping_goals_added_above_avg REAL,
        max_shotstopping_count_actions INTEGER,
        max_sweeping_goals_added_raw REAL,
        max_sweeping_goals_added_above_avg REAL,
        max_sweeping_count_actions INTEGER,
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
        team_strength REAL,
        total_goals_for INTEGER,
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
        date_time_est TEXT,
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
        status TEXT,
        last_updated_utc TEXT,
        last_updated_est TEXT,
        season INTEGER,
        FOREIGN KEY (home_team_id) REFERENCES team_info(team_id)
        FOREIGN KEY (away_team_id) REFERENCES team_info(team_id)
        FOREIGN KEY (referee_id) REFERENCES referee_info(referee_id)
        FOREIGN KEY (stadium_id) REFERENCES stadium_info(stadium_id)
        FOREIGN KEY (home_manager_id) REFERENCES manager_info(manager_id)
        FOREIGN KEY (away_manager_id) REFERENCES manager_info(manager_id)
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

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS game_flow (
        game_id TEXT,
        period_id INTEGER,
        expanded_minute INTEGER,
        home_team_id TEXT,
        home_team_value REAL,
        away_team_id TEXT,
        away_team_value REAL,
        PRIMARY KEY (game_id, period_id, expanded_minute),
        FOREIGN KEY (home_team_id) REFERENCES team_info(team_id),
        FOREIGN KEY (away_team_id) REFERENCES team_info(team_id)
    )
''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS team_strength_history (
        team_id TEXT,
        season INTEGER,
        team_strength REAL,
        team_rank INTEGER,
        date_stamp TEXT,
        count_games INTEGER,
        FOREIGN KEY (team_id) REFERENCES team_info(team_id)
    )
''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS game_shots (
        game_id TEXT,
        period_id INTEGER,
        expanded_minute INTEGER,
        game_minute INTEGER,
        team_id TEXT,
        shooter_player_id TEXT,
        assist_player_id TEXT,
        shot_location_x REAL,
        shot_location_y REAL,
        shot_end_location_x REAL,
        shot_end_location_y REAL,
        distance_from_goal REAL,
        distance_from_goal_yds REAL,
        blocked INTEGER,
        blocked_x REAL,
        blocked_y REAL,
        goal INTEGER,
        own_goal INTEGER,
        home_score INTEGER,
        away_score INTEGER,
        shot_xg REAL,
        shot_psxg REAL,
        head INTEGER,
        assist_through_ball INTEGER,
        assist_cross INTEGER,
        pattern_of_play TEXT,
        shot_order INTEGER,
        season INTEGER,
        FOREIGN KEY (game_id) REFERENCES games(game_id),
        UNIQUE(game_id, shot_order)
    )
''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS team_strength (
        team_id TEXT,
        season INTEGER,
        xgoal_difference REAL,
        goal_difference REAL,
        xpoints REAL,
        points REAL,
        goal_diff_minus_xgoal_diff REAL,
        goalfor_xgoalfor_diff REAL,
        FOREIGN KEY (team_id) REFERENCES team_info(team_id),
        UNIQUE(team_id, season)
    )
''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS team_xgoals_boundaries (
        season INTEGER,

        avg_shots_for REAL,
        min_shots_for REAL,
        max_shots_for REAL,

        avg_shots_against REAL,
        min_shots_against REAL,
        max_shots_against REAL,

        avg_goals_for REAL,
        min_goals_for REAL,
        max_goals_for REAL,

        avg_goals_against REAL,
        min_goals_against REAL,
        max_goals_against REAL,

        avg_goal_difference REAL,
        min_goal_difference REAL,
        max_goal_difference REAL,

        avg_xgoals_for REAL,
        min_xgoals_for REAL,
        max_xgoals_for REAL,

        avg_xgoals_against REAL,
        min_xgoals_against REAL,
        max_xgoals_against REAL,

        avg_xgoal_difference REAL,
        min_xgoal_difference REAL,
        max_xgoal_difference REAL,

        avg_goal_difference_minus_xgoal_difference REAL,
        min_goal_difference_minus_xgoal_difference REAL,
        max_goal_difference_minus_xgoal_difference REAL,

        avg_points REAL,
        min_points REAL,
        max_points REAL,

        avg_xpoints REAL,
        min_xpoints REAL,
        max_xpoints REAL,

        avg_point_diff REAL,
        min_point_diff REAL,
        max_point_diff REAL,

        avg_goalfor_xgoalfor_diff REAL,
        min_goalfor_xgoalfor_diff REAL,
        max_goalfor_xgoalfor_diff REAL,

        UNIQUE(season)
    )
''')

    cursor.execute('''      
        CREATE TABLE IF NOT EXISTS team_xpass_boundaries (
        season INTEGER,

        avg_attempted_passes_for REAL,
        min_attempted_passes_for REAL,
        max_attempted_passes_for REAL,

        avg_pass_completion_percentage_for REAL,
        min_pass_completion_percentage_for REAL,
        max_pass_completion_percentage_for REAL,

        avg_xpass_completion_percentage_for REAL,
        min_xpass_completion_percentage_for REAL,
        max_xpass_completion_percentage_for REAL,

        avg_passes_completed_over_expected_for REAL,
        min_passes_completed_over_expected_for REAL,
        max_passes_completed_over_expected_for REAL,

        avg_passes_completed_over_expected_p100_for REAL,
        min_passes_completed_over_expected_p100_for REAL,
        max_passes_completed_over_expected_p100_for REAL,

        avg_vertical_distance_for REAL,
        min_vertical_distance_for REAL,
        max_vertical_distance_for REAL,

        avg_attempted_passes_against REAL,
        min_attempted_passes_against REAL,
        max_attempted_passes_against REAL,

        avg_pass_completion_percentage_against REAL,
        min_pass_completion_percentage_against REAL,
        max_pass_completion_percentage_against REAL,

        avg_xpass_completion_percentage_against REAL,
        min_xpass_completion_percentage_against REAL,
        max_xpass_completion_percentage_against REAL,

        avg_passes_completed_over_expected_against REAL,
        min_passes_completed_over_expected_against REAL,
        max_passes_completed_over_expected_against REAL,

        avg_passes_completed_over_expected_p100_against REAL,
        min_passes_completed_over_expected_p100_against REAL,
        max_passes_completed_over_expected_p100_against REAL,

        avg_vertical_distance_against REAL,
        min_vertical_distance_against REAL,
        max_vertical_distance_against REAL,

        avg_passes_completed_over_expected_difference REAL,
        min_passes_completed_over_expected_difference REAL,
        max_passes_completed_over_expected_difference REAL,

        avg_vertical_distance_difference REAL,
        min_vertical_distance_difference REAL,
        max_vertical_distance_difference REAL,

        UNIQUE(season)
    )
''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS team_goals_add_boundaries (
        season INTEGER,

        avg_dribbling_num_actions_for REAL,
        min_dribbling_num_actions_for REAL,
        max_dribbling_num_actions_for REAL,

        avg_dribbling_goals_added_for REAL,
        min_dribbling_goals_added_for REAL,
        max_dribbling_goals_added_for REAL,

        avg_dribbling_num_actions_against REAL,
        min_dribbling_num_actions_against REAL,
        max_dribbling_num_actions_against REAL,

        avg_dribbling_goals_added_against REAL,
        min_dribbling_goals_added_against REAL,
        max_dribbling_goals_added_against REAL,

        avg_shooting_num_actions_for REAL,
        min_shooting_num_actions_for REAL,
        max_shooting_num_actions_for REAL,

        avg_shooting_goals_added_for REAL,
        min_shooting_goals_added_for REAL,
        max_shooting_goals_added_for REAL,

        avg_shooting_num_actions_against REAL,
        min_shooting_num_actions_against REAL,
        max_shooting_num_actions_against REAL,

        avg_shooting_goals_added_against REAL,
        min_shooting_goals_added_against REAL,
        max_shooting_goals_added_against REAL,

        avg_passing_num_actions_for REAL,
        min_passing_num_actions_for REAL,
        max_passing_num_actions_for REAL,

        avg_passing_goals_added_for REAL,
        min_passing_goals_added_for REAL,
        max_passing_goals_added_for REAL,

        avg_passing_num_actions_against REAL,
        min_passing_num_actions_against REAL,
        max_passing_num_actions_against REAL,

        avg_passing_goals_added_against REAL,
        min_passing_goals_added_against REAL,
        max_passing_goals_added_against REAL,

        avg_interrupting_num_actions_for REAL,
        min_interrupting_num_actions_for REAL,
        max_interrupting_num_actions_for REAL,

        avg_interrupting_goals_added_for REAL,
        min_interrupting_goals_added_for REAL,
        max_interrupting_goals_added_for REAL,

        avg_interrupting_num_actions_against REAL,
        min_interrupting_num_actions_against REAL,
        max_interrupting_num_actions_against REAL,

        avg_interrupting_goals_added_against REAL,
        min_interrupting_goals_added_against REAL,
        max_interrupting_goals_added_against REAL,

        avg_receiving_num_actions_for REAL,
        min_receiving_num_actions_for REAL,
        max_receiving_num_actions_for REAL,

        avg_receiving_goals_added_for REAL,
        min_receiving_goals_added_for REAL,
        max_receiving_goals_added_for REAL,

        avg_receiving_num_actions_against REAL,
        min_receiving_num_actions_against REAL,
        max_receiving_num_actions_against REAL,

        avg_receiving_goals_added_against REAL,
        min_receiving_goals_added_against REAL,
        max_receiving_goals_added_against REAL,

        avg_claiming_num_actions_for REAL,
        min_claiming_num_actions_for REAL,
        max_claiming_num_actions_for REAL,

        avg_claiming_goals_added_for REAL,
        min_claiming_goals_added_for REAL,
        max_claiming_goals_added_for REAL,

        avg_claiming_num_actions_against REAL,
        min_claiming_num_actions_against REAL,
        max_claiming_num_actions_against REAL,

        avg_claiming_goals_added_against REAL,
        min_claiming_goals_added_against REAL,
        max_claiming_goals_added_against REAL,

        avg_fouling_num_actions_for REAL,
        min_fouling_num_actions_for REAL,
        max_fouling_num_actions_for REAL,

        avg_fouling_goals_added_for REAL,
        min_fouling_goals_added_for REAL,
        max_fouling_goals_added_for REAL,

        avg_fouling_num_actions_against REAL,
        min_fouling_num_actions_against REAL,
        max_fouling_num_actions_against REAL,

        avg_fouling_goals_added_against REAL,
        min_fouling_goals_added_against REAL,
        max_fouling_goals_added_against REAL,

        UNIQUE(season)
    )
''')




    # Commit the changes and close the connection
    conn.commit()
    conn.close()
    print('Tables built.')