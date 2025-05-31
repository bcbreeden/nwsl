from data import db_games_xgoals
import unittest

class TestDbGamesXgoals(unittest.TestCase):
    def setUp(self):
        self.valid_game_id = "wvq9w4lNMW"
        self.valid_season = 2024
        self.expected_columns = {
            "game_id": str,
            "date_time_utc": str,
            "home_team_id": str,
            "home_goals": int,
            "home_team_xgoals": float,
            "home_player_xgoals": float,
            "away_team_id": str,
            "away_goals": int,
            "away_team_xgoals": float,
            "away_player_xgoals": float,
            "goal_difference": int,
            "team_xgoal_difference": float,
            "player_xgoal_difference": float,
            "final_score_difference": int,
            "home_xpoints": float,
            "away_xpoints": float,
            "season": int
        }

    def test_get_all_games_xgoals_by_season_structure(self):
        """Test structure and types of all games returned for a valid season."""
        rows = db_games_xgoals.get_all_games_xgoals_by_season(self.valid_season)
        self.assertIsInstance(rows, list)
        self.assertGreater(len(rows), 0)

        for row in rows:
            row_dict = dict(row)
            for col, expected_type in self.expected_columns.items():
                self.assertIn(col, row_dict)
                self.assertIsNotNone(row_dict[col], msg=f"{col} is None")
                if expected_type == float:
                    self.assertIsInstance(row_dict[col], (float, int), msg=f"{col} has wrong type: {type(row_dict[col])}")
                else:
                    self.assertIsInstance(row_dict[col], expected_type, msg=f"{col} has wrong type: {type(row_dict[col])}")

    def test_get_game_xgoals_by_id_structure(self):
        """Test structure and types of a single game xgoals record by ID."""
        row = db_games_xgoals.get_game_xgoals_by_id(self.valid_game_id)
        self.assertIsNotNone(row)
        row_dict = dict(row)

        for col, expected_type in self.expected_columns.items():
            self.assertIn(col, row_dict)
            self.assertIsNotNone(row_dict[col], msg=f"{col} is None")
            if expected_type == float:
                self.assertIsInstance(row_dict[col], (float, int), msg=f"{col} has wrong type: {type(row_dict[col])}")
            else:
                self.assertIsInstance(row_dict[col], expected_type, msg=f"{col} has wrong type: {type(row_dict[col])}")


if __name__ == '__main__':
    unittest.main()