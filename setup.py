from data import (db_games_xgoals, db_games, db_goalkeeper_goals_added,db_goalkeeper_xgoals,
                db_player_goals_added, db_player_info, db_player_xgoals, db_player_xpass,
                db_setup, db_team_goals_added, db_team_info, db_team_xgoals, db_team_xpass)

if __name__ == '__main__':
    SEASONS = [2022, 2023, 2024]
    print('Initial setup has started. This may take a few minutes.')
    db_setup.create_tables()
    db_player_info.insert_all_players_info()
    db_team_info.insert_team_info()
    for season in SEASONS:
        db_games_xgoals.insert_all_games_xgoals_by_season(season)
        db_games.insert_all_games_by_season(season)
        db_goalkeeper_goals_added.insert_goalkeeper_goals_added_by_season(season)
        db_goalkeeper_xgoals.insert_goalkeeper_xgoals_by_season(season)
        db_player_goals_added.insert_player_goals_added_by_season(season)

        db_player_xgoals.insert_player_xgoals_by_season(season)
        db_player_xgoals.update_xgoals_xassists_per_90(season)
        db_player_xgoals.update_player_xgoal_strength(season)
        
        db_player_xpass.insert_player_xpass_by_season(season)
        db_team_goals_added.insert_team_goals_added_by_season(season)
        db_team_xgoals.insert_teams_xgoals_by_season(season)
        db_team_xpass.insert_teams_xpass_by_season(season)
        print(str(season), 'season setup complete.')
    print('Initial setup completed.')