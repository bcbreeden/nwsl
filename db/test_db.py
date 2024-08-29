import unittest
from .db_goalkeeper_goals_added import *
from .db_goalkeeper_xgoals import *
from .db_player_goals_added import *
from .db_player_info import *
from .db_player_xgoals import *
from .db_player_xpass import *
from .db_team_info import *
from .db_team_xgoals import *
from .db_team_xpass import *
from .db_team_goals_added import *
from .db_games import *
from .db_setup import create_tables

class TestDB(unittest.TestCase):
    # Test Setup
    SEASON = '2024'
    create_tables()
    insert_team_info()
    insert_all_players_info()
    insert_goalkeeper_goals_added_by_season(SEASON)
    insert_goalkeeper_xgoals_by_season(SEASON)
    insert_player_goals_added_by_season(SEASON)
    insert_player_xgoals_by_season(SEASON)
    insert_player_xpass_by_season(SEASON)
    insert_teams_xgoals_by_season(SEASON)
    insert_teams_xpass_by_season(SEASON)
    insert_team_goals_added_by_season(SEASON)
    insert_all_games_by_season(SEASON)
    

    # Goalkeeper Goals Added
    def test_get_goalkeeper_goals_added_by_season(self):
        player_data = get_goalkeeper_goals_added_by_season('0x5gJ0LXM7', 2024)
        self.assertTrue(len(player_data) > 1, 'The query should return more than 1 row.')
    
    def test_get_all_goalkeeper_xgoal_data_by_season(self):
        players_data = get_all_goalkeepers_xgoals_by_season(2024)
        self.assertTrue(len(players_data) > 1, 'The query should return more than 1 row.')
    
    # Goalkeeper XGoals
    def test_get_goalkeeper_xgoal_data_by_season(self):
        player_data = get_goalkeeper_xgoals_by_season('0x5gJ0LXM7', 2024)
        self.assertTrue(len(player_data) > 1, 'The query should return more than 1 row.')
    
    # Player Goals Added
    def test_get_player_goals_added_by_season(self):
        player_data = get_player_goals_added_by_season('0Oq6243Pq6', 2024)
        self.assertTrue(len(player_data) > 1, 'The query should return more than 1 row.')
    
    # Player Info
    def test_all_player_info_insert(self):
        players_info_data = get_all_players_info()
        self.assertGreater(len(players_info_data), 25)
    
    def test_get_player_seasons(self):
        id = '0Oq6243Pq6'
        data_row_1 = get_player_seasons(id)[0]
        self.assertEqual(data_row_1['player_id'], id)
        self.assertAlmostEqual(data_row_1['year'], 2023)
    
    def test_get_player_info(self):
        id = '0Oq6243Pq6'
        data = get_player_info_by_id(id)
        self.assertEqual(data['player_name'], 'Lena Silano')
        self.assertEqual(data['birth_date'], '2000-02-28')
        self.assertEqual(data['nationality'], 'USA')
        self.assertEqual(data['primary_broad_position'], 'FW')
        self.assertEqual(data['primary_general_position'], 'ST')
        self.assertEqual(data['secondary_broad_position'], 'MF')
        self.assertEqual(data['secondary_general_position'], 'W')
    
    # Player XGoals
    def test_get_player_xgoals_by_season(self):
        player_data = get_player_xgoals('0Oq6243Pq6', 2024)
        self.assertTrue(len(player_data) > 1, 'The query should return more than 1 row.')
    
    def test_get_all_players_xgoals_by_season(self):
        players_data = get_all_player_xgoals(2024)
        self.assertTrue(len(players_data) > 1, 'The query should return more than 1 row.')

    # Player XPasses
    def test_get_player_xpasses_by_season(self):
        player_data = get_player_xpass('0Oq6243Pq6', 2024)
        self.assertTrue(len(player_data) > 1, 'The query should return more than 1 row.')
    
    def test_get_all_players_xpasses_by_season(self):
        players_data = get_all_player_xpass(2024)
        self.assertTrue(len(players_data) > 1, 'The query should return more than 1 row.')

    # Team Info
    def test_all_team_info_insert(self):
        teams_info_data = get_all_teams_info()
        self.assertGreater(len(teams_info_data), 10)
    
    def test_get_team_by_id(self):
        team_id = '315VnJ759x'
        data = get_team_info_by_id(team_id)
        self.assertEqual(data['team_name'], 'Bay FC')
        self.assertEqual(data['team_short_name'], 'Bay FC')
        self.assertEqual(data['team_abbreviation'], 'BAY')

    # Team XGoals
    def test_get_team_xgoals(self):
        team_id = '315VnJ759x'
        team_xgoal_data = get_team_xgoals(team_id, 2024)
        self.assertGreater(len(team_xgoal_data), 5)
    
    # Team XPasses
    def test_get_team_xpasses(self):
        team_id = '315VnJ759x'
        team_xgoal_data = get_team_xpass(team_id, 2024)
        self.assertGreater(len(team_xgoal_data), 5)
    
    # Team Goals Added
    def test_get_team_goals_added_by_season(self):
        team_data = get_team_goals_added_by_season('315VnJ759x', 2024)
        self.assertTrue(len(team_data) > 1, 'The query should return more than 1 row.')
    
    # Games
    def test_get_games_by_season(self):
        games_data = get_all_games_by_season(2024)
        self.assertGreater(len(games_data), 5)

if __name__ == '__main__':
    unittest.main()