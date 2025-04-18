import unittest
from .db_player_xgoals import get_player_xgoal_data, get_top_player_xgoals_stat

class TestPlayerXGoal(unittest.TestCase):
    def setUp(self):
        self.test_player_id = '7vQ7rOwOqD'
        self.test_season = 2023
        self.length_limit = 3
        self.expected_player_data = {
            "id": "7vQ7rOwOqD2023",
            "player_id": "7vQ7rOwOqD",
            "team_id": "Pk5LeeNqOW",
            "general_position": "ST",
            "minutes_played": 1284,
            "shots": 75,
            "shots_on_target": 39,
            "shots_on_target_perc": 52,
            "goals": 11,
            "xgoals": 7.78,
            "xplace": 1.39,
            "goals_minus_xgoals": 3.22,
            "key_passes": 20,
            "primary_assists": 5,
            "xassists": 2.8,
            "primary_assists_minus_xassists": 2.2,
            "xgoals_plus_xassists": 10.58,
            "points_added": 3.39,
            "xpoints_added": 3.45,
            "xgoals_xassists_per_90": 0.74,
            "season": 2023,
            "avg_minutes_played": 1104.08,
            "avg_shots": 28.54,
            "avg_shots_on_target": 12.33,
            "avg_shots_on_target_perc": 42.49,
            "avg_goals": 3.5,
            "avg_xgoals": 3.75,
            "avg_key_passes": 12.83,
            "avg_primary_assists": 1.33,
            "avg_xassists": 1.45,
            "avg_xgoals_plus_xassists": 5.2,
            "avg_points_added": 1.75,
            "avg_xpoints_added": 2.4,
            "avg_xgoals_xassists_per_90": 0.32,
            "avg_xplace": 0.02,
            "avg_goals_minus_xgoals": -0.25,
            "avg_primary_assists_minus_xassists": -0.12,
            "min_minutes_played": 476.0,
            "min_shots": 5.0,
            "min_shots_on_target": 2.0,
            "min_shots_on_target_perc": 22.22,
            "min_goals": 0.0,
            "min_xgoals": 0.32,
            "min_xplace": -2.05,
            "min_goals_minus_xgoals": -3.85,
            "min_primary_assists_minus_xassists": -2.19,
            "min_key_passes": 2.0,
            "min_primary_assists": 0.0,
            "min_xassists": 0.2,
            "min_xgoals_plus_xassists": 0.93,
            "min_points_added": 0.0,
            "min_xpoints_added": 0.22,
            "min_xgoals_xassists_per_90": 0.0,
            "max_minutes_played": 2056.0,
            "max_shots": 75.0,
            "max_shots_on_target": 39.0,
            "max_shots_on_target_perc": 66.67,
            "max_goals": 11.0,
            "max_xgoals": 12.85,
            "max_xplace": 2.6,
            "max_goals_minus_xgoals": 3.22,
            "max_primary_assists_minus_xassists": 2.2,
            "max_key_passes": 36.0,
            "max_primary_assists": 5.0,
            "max_xassists": 4.18,
            "max_xgoals_plus_xassists": 14.97,
            "max_points_added": 5.36,
            "max_xpoints_added": 8.15,
            "max_xgoals_xassists_per_90": 0.74,
            "player_name": "Sophia Wilson",
            "player_first_name": "Sophia",
            "player_last_name": "Wilson",
            "birth_date": "2000-08-10",
            "height_ft": 5,
            "height_in": 5,
            "nationality": "USA",
            "primary_broad_position": "FW",
            "primary_general_position": "ST",
            "secondary_broad_position": "Unknown Secondary Broad Position",
            "secondary_general_position": "Unknown Secondary General Position",
            "team_name": "Portland Thorns FC",
            "team_abbreviation": "POR",
            "team_short_name": "Portland"
        }

    def test_get_player_xgoal(self):
       player_data = get_player_xgoal_data(player_id=self.test_player_id, season=self.test_season)
       self.assertIsNotNone(player_data)
       for column in player_data.keys():
           self.assertAlmostEqual(self.expected_player_data[column], player_data[column], delta=0.05)
    
    def test_invalid_get_player_xgoal(self):
        data = get_player_xgoal_data(player_id='hooplah', season=self.test_season)
        self.assertIsNone(data)
        data = get_player_xgoal_data(player_id=self.test_player_id, season=1912)
        self.assertIsNone(data)

    def test_get_top_player_xgoals_limit(self):
        players_data = get_top_player_xgoals_stat(season=self.test_season, limit=self.length_limit)
        self.assertEqual(len(players_data), 3)
        xgoals_player = players_data[0]
        self.assertIsNotNone(xgoals_player)
        for column in xgoals_player.keys():
           self.assertAlmostEqual(self.expected_player_data[column], xgoals_player[column], delta=0.05)

    def test_get_top_player_xgoals_no_limit(self):
        players_data = get_top_player_xgoals_stat(season=self.test_season)
        self.assertEqual(len(players_data), 282)
        xgoals_player = players_data[0]
        self.assertIsNotNone(xgoals_player)
        for column in xgoals_player.keys():
           self.assertAlmostEqual(self.expected_player_data[column], xgoals_player[column], delta=0.05)

if __name__ == '__main__':
    unittest.main()