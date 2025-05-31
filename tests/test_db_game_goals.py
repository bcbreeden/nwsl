import unittest
from data import db_game_goals 

class TestGetGoalsByGameId(unittest.TestCase):
    def test_goals_data_fields_and_validity(self):
        """Test that goal data for a game ID includes all expected fields with valid types and values."""
        game_id = 'XVqKzNYO50'
        rows = db_game_goals.get_goals_by_game_id(game_id)
        self.assertGreater(len(rows), 0, f"No goal rows found for game_id {game_id}")

        for row in rows:
            expected_keys = [
                "game_id",
                "shooter_player_id",
                "assist_player_id",
                "team_id",
                "expanded_minute",
                "pattern_of_play"
            ]
            for key in expected_keys:
                self.assertIn(key, row.keys(), f"Missing key: {key}")

            # Validate types and presence
            self.assertIsInstance(row["game_id"], str)
            self.assertTrue(row["game_id"], "game_id should not be empty")

            self.assertIsInstance(row["shooter_player_id"], str)
            self.assertTrue(row["shooter_player_id"], "shooter_player_id should not be empty")

            self.assertIsInstance(row["assist_player_id"], str)
            # assist_player_id can be empty string if unassisted, so no assertTrue

            self.assertIsInstance(row["team_id"], str)
            self.assertTrue(row["team_id"], "team_id should not be empty")

            self.assertIsInstance(row["expanded_minute"], int)
            self.assertGreaterEqual(row["expanded_minute"], 0)

            self.assertIsInstance(row["pattern_of_play"], str)
            self.assertTrue(row["pattern_of_play"], "pattern_of_play should not be empty")
