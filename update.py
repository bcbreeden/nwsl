from data import (db_games_xgoals, db_games, db_goalkeeper_goals_added,db_goalkeeper_xgoals,
                db_player_goals_added, db_player_info, db_player_xgoals, db_player_xpass,
                db_setup, db_team_goals_added, db_team_info, db_team_xgoals, db_team_xpass, db_game_flow,
                db_manager_info, db_referee_info, db_stadium_info, db_player_strength, db_game_shots,
                db_team_xgoals_boundaries, db_team_xpass_boundaries)
from datetime import datetime
import time

UPDATE_ALL_SEASONS = False

'''
Updates the tables for the current year (if applicable).

Requires tables to be setup, if setup.py has not been run, run that first.
'''
if __name__ == '__main__':
    current_year = datetime.now().year
    if  UPDATE_ALL_SEASONS:
        seasons = seasons = list(range(2016, current_year + 1))
    else:
        seasons = [datetime.now().year]

    db_player_info.insert_all_players_info()
    db_team_info.insert_team_info()
    db_manager_info.insert_all_manager_info()
    db_referee_info.insert_all_referee_info()
    db_stadium_info.insert_all_stadium_info()
    for season in seasons:
        print(f'Starting update for {season}')
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

        print('Adding game flow data...')
        game_ids = db_games.get_game_ids_by_season(season)
        for game_id in game_ids:
            db_game_shots.insert_all_game_shots(game_id, season)
            db_game_flow.insert_flow_by_game_id(game_id)
        print('Game flow data added.')
        print(f'{season} complete, buffering for API limit...')
        time.sleep(30)
