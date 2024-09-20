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
from .db_games_xgoals import *


SEASON = 2023

class TestDB(unittest.TestCase):
    # Goalkeeper Goals Added
    def test_get_goalkeeper_goals_added_by_season(self):
        player_data = get_goalkeeper_goals_added_by_season('0x5gW0mw57', SEASON)
        self.assertEqual(player_data['player_name'], 'Shelby Hogan')
        self.assertEqual(player_data['minutes_played'], 95)
        self.assertEqual(player_data['team_id'], 'Pk5LeeNqOW')
        self.assertEqual(player_data['team_name'], 'Portland Thorns FC')
        

    # Goalkeeper XGoals
    def test_get_goalkeeper_xgoal_data_by_season(self):
        player_data = get_goalkeeper_xgoals_by_season('0x5gW0mw57', SEASON)
        self.assertEqual(player_data['player_name'], 'Shelby Hogan')
        self.assertEqual(player_data['team_id'], 'Pk5LeeNqOW')
        self.assertEqual(player_data['minutes_played'], 95)

    def test_get_all_goalkeeper_xgoal_data_by_season(self):
        players_data = get_all_goalkeepers_xgoals_by_season(SEASON)
        self.assertTrue(len(players_data) > 1, 'The query should return more than 1 row.')
        for player in players_data:
            self.assertEqual(player['season'], SEASON)
            self.assertEqual(type(player['player_name']), str)
            self.assertGreater(len(player['player_name']), 1)
            self.assertTrue(player['id'])
            self.assertTrue(player['player_id'])
            self.assertTrue(player['team_id'])
    
    # Player Goals Added
    def test_get_player_goals_added_by_season(self):
        player_data = get_player_goals_added_by_season('0Oq6243Pq6', SEASON)
        print(player_data['dribbling_goals_added_raw'], 'HERE')
        self.assertEqual(player_data['season'], SEASON)
        self.assertEqual(player_data['player_name'], 'Lena Silano')
        self.assertEqual(player_data['minutes_played'], 369)
        self.assertEqual(player_data['team_name'], 'Washington Spirit')
    
    # Player Info
    def test_all_player_info_insert(self):
        players_info_data = get_all_players_info()
        for player in players_info_data:
            self.assertNotEqual(player['player_name'], 'Unknown Name')
            self.assertNotEqual(player['player_id'], 'Unknown ID')
        self.assertGreater(len(players_info_data), 25)
    
    def test_get_player_seasons(self):
        id = '0Oq6243Pq6'
        player_seasons_data = get_player_seasons(id)
        player_row_1 = player_seasons_data[0]
        self.assertEqual(player_row_1['player_id'], id)
        self.assertEqual(player_row_1['year'], 2023)
        for row in player_seasons_data:
            self.assertEqual(type(row['year']), int)
    
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
        data = get_player_xgoals('0Oq6243Pq6', SEASON)
        self.assertEqual(data['player_name'], 'Lena Silano')
        self.assertEqual(data['team_name'], 'Washington Spirit')
        self.assertEqual(data['minutes_played'], 369)
        self.assertEqual(data['shots_on_target'], 1)
    
    def test_get_all_players_xgoals_by_season(self):
        players_data = get_all_player_xgoals(SEASON)
        for player in players_data:
            self.assertEqual(player['season'], SEASON)
            self.assertNotEqual(player['player_id'], 'Unknown Player ID')
        self.assertGreater(len(players_data), 25)

    def test_top_xgoals(self):
        players_data = get_top_player_xgoals_stat(SEASON, 'goals', 5)
        self.assertEqual(len(players_data), 5)
        players_data = get_top_player_xgoals_stat(SEASON, 'primary_assists', 3)
        self.assertEqual(len(players_data), 3)

    # Player XPasses
    def test_get_player_xpasses_by_season(self):
        player_data = get_player_xpass('0Oq6243Pq6', SEASON)
        self.assertTrue(len(player_data) > 1, 'The query should return more than 1 row.')
    
    def test_get_all_players_xpasses_by_season(self):
        players_data = get_all_player_xpass(SEASON)
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
    def test_top_team_xgoals(self):
        data = get_top_team_xgoals_stat(SEASON, 'goals_for')
        self.assertGreater(len(data), 5)

    # Team XPasses
    def test_get_team_xpasses(self):
        team_id = 'aDQ0lzvQEv'
        team_xgoal_data = get_team_xpass(team_id, SEASON)
        self.assertGreater(len(team_xgoal_data), 5)
    
    # Team Goals Added
    def test_get_team_goals_added_by_season(self):
        team_data = get_team_goals_added_by_season('aDQ0lzvQEv', SEASON)
        self.assertTrue(len(team_data) > 1, 'The query should return more than 1 row.')
    
    # Games
    def test_get_games_by_season(self):
        games_data = get_all_games_by_season(SEASON)
        self.assertGreater(len(games_data), 5)
    
    # Games XGoals
    def test_get_games_xgoals_by_season(self):
        games_data = get_all_games_xgoals_by_season(SEASON)
        self.assertGreater(len(games_data), 5)


if __name__ == '__main__':
    unittest.main()