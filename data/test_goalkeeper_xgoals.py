import unittest

from .db_goalkeeper_xgoals import get_goalkeeper_xgoals_by_season, get_all_goalkeepers_xgoals_by_season, PlayerDataNotFoundError

class TestKeeperXGoal(unittest.TestCase):
    def setUp(self):
        self.test_player_id = "ljqE2r4oQx"
        self.test_season = 2023
        self.expected_keeper_data = {
            "id": "ljqE2r4oQx2023",
            "player_id": "ljqE2r4oQx",
            "team_id": "zeQZeazqKw",
            "season": 2023,
            "minutes_played": 2004,
            "shots_faced": 69,
            "goals_conceded": 20,
            "saves": 46,
            "share_headed_shots": 0.14,
            "xgoals_gk_faced": 18.62,
            "goals_minus_xgoals_gk": 1.38,
            "goals_divided_by_xgoals_gk": 1.07,
            "save_perc": 66.67,
            "avg_minutes_played": 1669.73,
            "avg_shots_faced": 75.87,
            "avg_goals_conceded": 20.4,
            "avg_saves": 54.2,
            "avg_share_headed_shots": 0.13,
            "avg_xgoals_gk_faced": 19.93,
            "avg_goals_minus_xgoals_gk": 0.47,
            "avg_goals_divided_by_xgoals_gk": 1.01,
            "avg_save_perc": 70.95,
            "min_minutes_played": 600,
            "min_shots_faced": 22,
            "min_goals_conceded": 5,
            "min_saves": 13,
            "min_share_headed_shots": 0.04,
            "min_xgoals_gk_faced": 6.37,
            "min_goals_minus_xgoals_gk": -5.39,
            "min_goals_divided_by_xgoals_gk": 0.78,
            "min_save_perc": 59.09,
            "max_minutes_played": 2250,
            "max_shots_faced": 129,
            "max_goals_conceded": 48,
            "max_saves": 91,
            "max_share_headed_shots": 0.21,
            "max_xgoals_gk_faced": 40.51,
            "max_goals_minus_xgoals_gk": 7.49,
            "max_goals_divided_by_xgoals_gk": 1.19,
            "max_save_perc": 80.77,
            "player_name": "Casey Murphy",
            "player_first_name": "Casey",
            "player_last_name": "Murphy",
            "birth_date": "1996-04-25",
            "height_ft": 6,
            "height_in": 1,
            "nationality": "USA",
            "primary_broad_position": "GK",
            "primary_general_position": "GK",
            "secondary_broad_position": "Unknown Secondary Broad Position",
            "secondary_general_position": "Unknown Secondary General Position",
            "team_name": "North Carolina Courage",
            "team_short_name": "North Carolina",
            "team_abbreviation": "NC"
        }

    def test_get_keeper_xgoal(self):
       keeper_data = get_goalkeeper_xgoals_by_season(player_id=self.test_player_id, season=self.test_season)
       self.assertIsNotNone(keeper_data)
       for column in keeper_data.keys():
           self.assertEqual(self.expected_keeper_data[column], keeper_data[column])
    
    def test_invalid_get_keeper_xgoal(self):
        with self.assertRaises(PlayerDataNotFoundError) as context:
            get_goalkeeper_xgoals_by_season(player_id='hooplah', season=self.test_season)
        self.assertIn("No data found", str(context.exception))
        with self.assertRaises(PlayerDataNotFoundError) as context:
            get_goalkeeper_xgoals_by_season(player_id=self.test_player_id, season=1912)
        self.assertIn("No data found", str(context.exception))

    def test_get_all_keepers_by_season(self):
        data = get_all_goalkeepers_xgoals_by_season(season=self.test_season)
        self.assertIsNotNone(data)
        self.assertEqual(24, len(data))
    
    def test_invalid_get_keepers_by_season(self):
        data = get_all_goalkeepers_xgoals_by_season(season=1999)
        self.assertEqual(len(data), 0)

if __name__ == '__main__':
    unittest.main()