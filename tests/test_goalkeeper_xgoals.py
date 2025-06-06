import unittest
from data import db_goalkeeper_xgoals

EXPECTED_FIELDS = [
    'id', 'player_id', 'team_id', 'season', 'minutes_played', 'shots_faced', 'goals_conceded',
    'saves', 'share_headed_shots', 'xgoals_gk_faced', 'goals_minus_xgoals_gk', 'goals_divided_by_xgoals_gk',
    'save_perc', 'player_strength',
    'avg_minutes_played', 'avg_shots_faced', 'avg_goals_conceded', 'avg_saves',
    'avg_share_headed_shots', 'avg_xgoals_gk_faced', 'avg_goals_minus_xgoals_gk', 'avg_goals_divided_by_xgoals_gk',
    'avg_save_perc',
    'min_minutes_played', 'min_shots_faced', 'min_goals_conceded', 'min_saves',
    'min_share_headed_shots', 'min_xgoals_gk_faced', 'min_goals_minus_xgoals_gk', 'min_goals_divided_by_xgoals_gk',
    'min_save_perc',
    'max_minutes_played', 'max_shots_faced', 'max_goals_conceded', 'max_saves',
    'max_share_headed_shots', 'max_xgoals_gk_faced', 'max_goals_minus_xgoals_gk', 'max_goals_divided_by_xgoals_gk',
    'max_save_perc'
]

class TestGoalkeeperXGoals(unittest.TestCase):

    def setUp(self):
        self.season = 2024
        self.player_id = '9vQ22r1mQK'

    def test_get_all_goalkeepers_xgoals_by_season(self):
        result = db_goalkeeper_xgoals.get_all_goalkeepers_xgoals_by_season(self.season)
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)

        for row in result:
            # Confirm we can access fields like a dictionary
            for field in EXPECTED_FIELDS:
                self.assertIn(field, row.keys())
            self.assertEqual(row['season'], self.season)

    def test_get_goalkeeper_xgoals_by_season(self):
        row = db_goalkeeper_xgoals.get_goalkeeper_xgoals_by_season(self.player_id, self.season)
        self.assertIsNotNone(row)
        self.assertIn('player_id', row.keys())
        self.assertEqual(row['player_id'], self.player_id)
        self.assertEqual(row['season'], self.season)

        for field in EXPECTED_FIELDS:
            self.assertIn(field, row.keys())

    def test_fetch_keeper_xgoal_data(self):
        result = db_goalkeeper_xgoals.fetch_keeper_xgoal_data(self.season)
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        for item in result:
            self.assertIn('player_id', item)
            self.assertIn('minutes_played', item)

    def test_calculate_player_statistics(self):
        raw_data = db_goalkeeper_xgoals.fetch_keeper_xgoal_data(self.season)
        result = db_goalkeeper_xgoals.calculate_player_statistics(raw_data)

        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)

        for player in result:
            self.assertGreaterEqual(player['minutes_played'], db_goalkeeper_xgoals.MINIMUM_MINUTES)
            self.assertIn('save_perc', player)
            self.assertIsInstance(player['save_perc'], float)

if __name__ == '__main__':
    unittest.main()
