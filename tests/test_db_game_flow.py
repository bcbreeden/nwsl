import unittest
from data import db_game_flow  

class TestGetGameFlowByGameId(unittest.TestCase):
    def test_game_flow_fields_and_data_validity(self):
        """Test that game_flow data exists and fields contain valid non-empty values."""
        game_id = 'XVqKzNYO50'
        rows = db_game_flow.get_game_flow_by_game_id(game_id)
        self.assertGreater(len(rows), 0, f"No rows found for game_id {game_id}")

        for row in rows:
            # --- ID and structure checks ---
            self.assertTrue(row["game_id"], "game_id should not be empty")
            self.assertTrue(row["home_team_id"], "home_team_id should not be empty")
            self.assertTrue(row["away_team_id"], "away_team_id should not be empty")

            # --- Numeric fields should be real values ---
            self.assertIsInstance(row["period_id"], int)
            self.assertIsInstance(row["expanded_minute"], int)
            self.assertGreaterEqual(row["period_id"], 0)
            self.assertGreaterEqual(row["expanded_minute"], 0)

            self.assertIsInstance(row["home_team_value"], float)
            self.assertIsInstance(row["away_team_value"], float)
            self.assertGreaterEqual(row["home_team_value"], -10.0)
            self.assertGreaterEqual(row["away_team_value"], -10.0)

            # --- Team metadata should be present ---
            self.assertTrue(row["home_team_name"], "home_team_name should not be empty")
            self.assertTrue(row["away_team_name"], "away_team_name should not be empty")
            self.assertTrue(row["home_abbreviation"], "home_abbreviation should not be empty")
            self.assertTrue(row["away_abbreviation"], "away_abbreviation should not be empty")

            # Optional: Check strings are actually strings
            for key in ["home_team_name", "away_team_name", "home_abbreviation", "away_abbreviation"]:
                self.assertIsInstance(row[key], str, f"{key} should be a string")

