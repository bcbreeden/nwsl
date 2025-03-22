import unittest
from .db_goalkeeper_goals_added import get_goalkeeper_goals_added_by_season, fetch_keeper_goals_added_data, calculate_player_statistics

class TestKeeperGoalsAdded(unittest.TestCase):
    def setUp(self):
        self.test_player_id = 'ljqE2r4oQx'
        self.test_season = 2023
        self.length_limit = 3
        self.valid_api_data = fetch_keeper_goals_added_data(self.test_season)
        self.expected_player_data = {
            "id": "ljqE2r4oQx2023",
            "player_id": "ljqE2r4oQx",
            "team_id": "zeQZeazqKw",
            "season": 2023,
            "claiming_goals_added_raw": 0.06,
            "claiming_goals_added_above_avg": 0.09,
            "claiming_count_actions": 19,
            "fielding_goals_added_raw": -0.02,
            "fielding_goals_added_above_avg": 0.08,
            "fielding_count_actions": 494,
            "handling_goals_added_raw": -0.21,
            "handling_goals_added_above_avg": -0.48,
            "handling_count_actions": 46,
            "passing_goals_added_raw": 0.82,
            "passing_goals_added_above_avg": -0.3,
            "passing_count_actions": 739,
            "shotstopping_goals_added_raw": -1.38,
            "shotstopping_goals_added_above_avg": -1.05,
            "shotstopping_count_actions": 66,
            "sweeping_goals_added_raw": -0.35,
            "sweeping_goals_added_above_avg": -0.24,
            "sweeping_count_actions": 24,
            "avg_claiming_goals_added_raw": 0.01,
            "avg_claiming_goals_added_above_avg": 0.03,
            "avg_claiming_count_actions": 23.6,
            "avg_fielding_goals_added_raw": -0.08,
            "avg_fielding_goals_added_above_avg": 0.00,
            "avg_fielding_count_actions": 328.87,
            "avg_handling_goals_added_raw": 0.29,
            "avg_handling_goals_added_above_avg": 0.06,
            "avg_handling_count_actions": 54.2,
            "avg_passing_goals_added_raw": 0.8,
            "avg_passing_goals_added_above_avg": -0.13,
            "avg_passing_count_actions": 582.2,
            "avg_shotstopping_goals_added_raw": -0.47,
            "avg_shotstopping_goals_added_above_avg": -0.2,
            "avg_shotstopping_count_actions": 74.6,
            "avg_sweeping_goals_added_raw": 0.03,
            "avg_sweeping_goals_added_above_avg": 0.12,
            "avg_sweeping_count_actions": 30.33,
            "min_claiming_goals_added_raw": -0.36,
            "min_claiming_goals_added_above_avg": -0.33,
            "min_claiming_count_actions": 5,
            "min_fielding_goals_added_raw": -0.42,
            "min_fielding_goals_added_above_avg": -0.35,
            "min_fielding_count_actions": 127,
            "min_handling_goals_added_raw": -0.21,
            "min_handling_goals_added_above_avg": -0.48,
            "min_handling_count_actions": 13,
            "min_passing_goals_added_raw": 0.13,
            "min_passing_goals_added_above_avg": -0.79,
            "min_passing_count_actions": 216,
            "min_shotstopping_goals_added_raw": -7.49,
            "min_shotstopping_goals_added_above_avg": -7.17,
            "min_shotstopping_count_actions": 21,
            "min_sweeping_goals_added_raw": -0.96,
            "min_sweeping_goals_added_above_avg": -0.85,
            "min_sweeping_count_actions": 13,
            "max_claiming_goals_added_raw": 0.21,
            "max_claiming_goals_added_above_avg": 0.24,
            "max_claiming_count_actions": 42,
            "max_fielding_goals_added_raw": 0.08,
            "max_fielding_goals_added_above_avg": 0.16,
            "max_fielding_count_actions": 846,
            "max_handling_goals_added_raw": 0.66,
            "max_handling_goals_added_above_avg": 0.37,
            "max_handling_count_actions": 91,
            "max_passing_goals_added_raw": 1.86,
            "max_passing_goals_added_above_avg": 0.79,
            "max_passing_count_actions": 1047,
            "max_shotstopping_goals_added_raw": 5.39,
            "max_shotstopping_goals_added_above_avg": 5.75,
            "max_shotstopping_count_actions": 128,
            "max_sweeping_goals_added_raw": 0.52,
            "max_sweeping_goals_added_above_avg": 0.64,
            "max_sweeping_count_actions": 51,
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

    def test_get_keeper_goals_added(self):
        player_data = get_goalkeeper_goals_added_by_season(player_id=self.test_player_id, season=self.test_season)
        self.assertIsNotNone(player_data)
        for column in player_data.keys():
            print(column, player_data[column])
            self.assertEqual(self.expected_player_data[column], player_data[column])

    def test_invalid_get_keeper_goals_added(self):
        data = get_goalkeeper_goals_added_by_season(player_id='hooplah', season=self.test_season)
        self.assertIsNone(data)
        data = get_goalkeeper_goals_added_by_season(player_id=self.test_player_id, season=1912)
        self.assertIsNone(data)
    
    def test_fetch_keeper_goals_added(self):
        data = self.valid_api_data
        self.assertIsNotNone(data)
        self.assertEqual(len(data), 23)
    
    def test_invalid_fetch_keeper_goals_added(self):
        invalid_data = fetch_keeper_goals_added_data(1999)
        self.assertEqual(len(invalid_data), 0)
    
    def test_calculate_keeper_xgoal_stats(self):
        data = self.valid_api_data
        stats_default = calculate_player_statistics(data)
        for player in stats_default:
            self.assertGreaterEqual(player['minutes_played'], 500)
        stats_diff = calculate_player_statistics(data, 50)
        for player in stats_diff:
            self.assertGreaterEqual(player['minutes_played'], 50)
    
    def test_invalid_calculate_keeper_goals_added(self):
        data = self.valid_api_data
        stats_invalid = calculate_player_statistics(data, 9999999)
        self.assertEqual(len(stats_invalid), 0)

if __name__ == '__main__':
    unittest.main()