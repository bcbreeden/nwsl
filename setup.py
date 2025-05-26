from data import (db_games_xgoals, db_games, db_goalkeeper_goals_added,db_goalkeeper_xgoals,
                db_player_goals_added, db_player_info, db_player_xgoals, db_player_xpass,
                db_setup, db_team_goals_added, db_team_info, db_team_xgoals, db_team_xpass, db_game_flow,
                db_manager_info, db_referee_info, db_stadium_info, db_game_shots, db_player_strength,
                db_team_xgoals_boundaries, db_team_xpass_boundaries, db_team_goals_added_boundaries,
                db_game_goals)

import time

if __name__ == '__main__':
    SEASONS = [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025]
    print('Initial setup has started. This may take a few minutes.')
    db_setup.create_tables()
    db_player_info.insert_all_players_info()
    db_team_info.insert_team_info()
    db_manager_info.insert_all_manager_info()
    db_referee_info.insert_all_referee_info()
    db_stadium_info.insert_all_stadium_info()

    for season in SEASONS:
        db_games_xgoals.insert_all_games_xgoals_by_season(season)
        db_games.insert_all_games_by_season(season)

        db_goalkeeper_goals_added.insert_goalkeeper_goals_added_by_season(season)
        db_goalkeeper_xgoals.insert_goalkeeper_xgoals_by_season(season)

        db_player_goals_added.insert_player_goals_added_by_season(season)

        db_player_xgoals.insert_player_xgoals_by_season(season)
        db_player_xgoals.update_xgoals_xassists_per_90(season)

        db_player_strength.update_attacker_strength(season)
        db_player_strength.update_midfielder_strength(season)
        db_player_strength.update_defender_strength(season)
        db_player_strength.update_goalkeeper_strength(season)

        db_player_xpass.insert_player_xpass_by_season(season)

        db_team_goals_added.insert_team_goals_added_by_season(season)
        db_team_xgoals.insert_teams_xgoals_by_season(season)
        db_team_xgoals.insert_team_strength_history(season)
        db_team_xpass.insert_teams_xpass_by_season(season)
        db_team_xgoals_boundaries.insert_team_xgoal_boundaries(season)
        db_team_xpass_boundaries.insert_team_xpass_boundaries(season)
        db_team_goals_added_boundaries.insert_team_goals_add_boundaries(season)

        game_ids = db_games.get_game_ids_by_season(season)
        for game_id in game_ids:
            db_game_shots.insert_all_game_shots(game_id, season)
            db_game_flow.insert_flow_by_game_id(game_id)
            db_game_goals.insert_game_goals_by_game_id(game_id)
        print(str(season), 'season setup complete.')
        print('Buffering, next season will begin in 15 seconds.')
        time.sleep(15)
    
    print('Initial setup completed.')