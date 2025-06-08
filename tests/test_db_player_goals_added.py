import unittest
from data import db_player_goals_added

EXPECTED_FIELDS = [
    'id', 'player_id', 'team_id', 'general_position', 'minutes_played',
    'dribbling_goals_added_raw', 'dribbling_goals_added_above_avg', 'dribbling_count_actions',
    'fouling_goals_added_raw', 'fouling_goals_added_above_avg', 'fouling_count_actions',
    'interrupting_goals_added_raw', 'interrupting_goals_added_above_avg', 'interrupting_count_actions',
    'passing_goals_added_raw', 'passing_goals_added_above_avg', 'passing_count_actions',
    'receiving_goals_added_raw', 'receiving_goals_added_above_avg', 'receiving_count_actions',
    'shooting_goals_added_raw', 'shooting_goals_added_above_avg', 'shooting_count_actions',
    'season'
]

class TestPlayerGoalsAdded(unittest.TestCase):

    def setUp(self):
        self.season = 2024
        self.player_id = 'Oa5wVYNBM1'

    def test_get_player_goals_added_by_season(self):
        row = db_player_goals_added.get_player_goals_added_by_season(self.player_id, self.season)
        self.assertIsNotNone(row)
        self.assertIn('player_id', row.keys())
        self.assertEqual(row['player_id'], self.player_id)
        self.assertEqual(row['season'], self.season)
        for field in EXPECTED_FIELDS:
            self.assertIn(field, row.keys())

    def test_get_all_players_goals_added_by_season(self):
        rows = db_player_goals_added.get_all_players_goals_added_by_season(self.season)
        self.assertIsInstance(rows, list)
        self.assertGreater(len(rows), 0)
        for row in rows:
            self.assertIn('season', row.keys())
            self.assertEqual(row['season'], self.season)
            for field in EXPECTED_FIELDS:
                self.assertIn(field, row.keys())

    def test_fetch_players_goals_added_data(self):
        data = db_player_goals_added.fetch_players_goals_added_data(self.season)
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
        for player in data:
            self.assertIn('player_id', player)
            self.assertIn('general_position', player)
            self.assertTrue(any(k.endswith('_goals_added_raw') for k in player))

    def test_calculate_player_statistics(self):
        data = db_player_goals_added.fetch_players_goals_added_data(self.season)
        filtered = db_player_goals_added.calculate_player_statistics(data)
        self.assertIsInstance(filtered, list)
        self.assertGreaterEqual(len(filtered), 0)
        for player in filtered:
            self.assertGreaterEqual(player['minutes_played'], db_player_goals_added.MINIMUM_MINUTES)

if __name__ == '__main__':
    unittest.main()