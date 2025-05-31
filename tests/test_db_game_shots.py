from data import db_game_shots
import unittest

class TestShotDataValidity(unittest.TestCase):
    def test_shots_data_fields_and_validity(self):
        """
        Test that shot data for a game ID includes all expected fields
        with valid types and non-empty values.
        """
        game_id = 'XVqKzNYO50'
        rows = db_game_shots.get_shots_by_game_id(game_id)
        self.assertGreater(len(rows), 0, f"No shot rows found for game_id {game_id}")

        for row in rows:
            expected_fields = {
                "game_id": str,
                "period_id": int,
                "expanded_minute": int,
                "game_minute": int,
                "team_id": str,
                "shooter_player_id": str,
                "assist_player_id": str,
                "shot_location_x": float,
                "shot_location_y": float,
                "shot_end_location_x": float,
                "shot_end_location_y": float,
                "distance_from_goal": float,
                "distance_from_goal_yds": float,
                "blocked": int,
                "blocked_x": float,
                "blocked_y": float,
                "goal": int,
                "own_goal": int,
                "home_score": int,
                "away_score": int,
                "shot_xg": float,
                "shot_psxg": float,
                "head": int,
                "assist_through_ball": int,
                "assist_cross": int,
                "pattern_of_play": str,
                "shot_order": int,
                "season": int
            }

            for key, expected_type in expected_fields.items():
                self.assertIn(key, row.keys(), f"Missing key: {key}")
                self.assertIsInstance(row[key], expected_type, f"{key} is not of type {expected_type}")

                # Assert non-empty values where appropriate (skip checks for fields that can be 0 or empty by design)
                if expected_type == str:
                    self.assertTrue(row[key], f"{key} should not be an empty string")
                if expected_type == int or expected_type == float:
                    self.assertIsNotNone(row[key], f"{key} should not be None")

class TestGetShotsByType(unittest.TestCase):
    def test_valid_shot_types(self):
        """
        Test that each valid shot type returns a list of results
        with expected fields and no exceptions.
        """
        valid_shot_types = ['regular', 'set piece', 'fastbreak', 'free kick', 'penalty']
        season = 2024  # replace with a valid season that exists in your DB

        for shot_type in valid_shot_types:
            try:
                rows = db_game_shots.get_shots_by_type(shot_type, season)
                self.assertIsInstance(rows, list)
                for row in rows:
                    self.assertIn("game_id", row)
                    self.assertIn("pattern_of_play", row)
                    self.assertEqual(row["pattern_of_play"].lower(), shot_type.lower())
            except Exception as e:
                self.fail(f"get_shots_by_type raised an exception for valid shot_type='{shot_type}': {e}")

    def test_null_season_raises(self):
        """Test that passing None as season raises a ValueError."""
        with self.assertRaises(ValueError):
            db_game_shots.get_shots_by_type('regular', None)

    def test_invalid_shot_type_raises(self):
        """Test that an invalid shot type raises a ValueError."""
        with self.assertRaises(ValueError):
            db_game_shots.get_shots_by_type('overhead bicycle kick', 2024)

class TestGetTotalPsxgByTeamAndSeason(unittest.TestCase):
    def test_total_psxg_valid_team_and_season(self):
        """
        Test that total PSxG is returned as a float and is non-negative
        for a valid team and season.
        """
        team_id = 'KPqjw8PQ6v'
        season = 2024

        result = db_game_shots.get_total_psxg_by_team_and_season(team_id, season)
        print(type(result))
        print(result)
        self.assertIsInstance(result, float, "Returned value should be a float")
        self.assertGreaterEqual(result, 0.0, "PSxG should be zero or greater")

class TestGetTotalPsxgByGameId(unittest.TestCase):
    def test_total_psxg_by_game_id(self):
        """
        Test that total PSxG per team is returned as a dictionary with float values.
        """
        game_id = 'XVqKzNYO50'
        result = db_game_shots.get_total_psxg_by_game_id(game_id)

        self.assertIsInstance(result, dict, "Result should be a dictionary")
        self.assertGreaterEqual(len(result), 1, "Should return at least one team PSxG total")

        for team_id, psxg in result.items():
            self.assertIsInstance(team_id, str, "Team ID should be a string")
            self.assertIsInstance(psxg, float, f"PSxG for team {team_id} should be a float")
            self.assertGreaterEqual(psxg, 0.0, f"PSxG for team {team_id} should be non-negative")

class TestDbGameShots(unittest.TestCase):

    def test_get_total_shots_by_game_id_valid(self):
        """Test that total shots by game ID returns a non-empty dict with correct types."""
        game_id = 'XVqKzNYO50'
        result = db_game_shots.get_total_shots_by_game_id(game_id)

        # Assert it's a dictionary
        self.assertIsInstance(result, dict)
        self.assertGreater(len(result), 0, "Result should not be empty")

        for team_id, total_shots in result.items():
            self.assertIsInstance(team_id, str)
            self.assertIsInstance(total_shots, int)
            self.assertGreaterEqual(total_shots, 0)

    def test_get_total_shots_by_game_id_invalid(self):
        """Test that passing an invalid game ID raises a ValueError."""
        with self.assertRaises(ValueError):
            db_game_shots.get_total_shots_by_game_id(None)

        with self.assertRaises(ValueError):
            db_game_shots.get_total_shots_by_game_id(123)  # Not a string

class TestGetTotalShotsOnTargetByGameId(unittest.TestCase):
    def setUp(self):
        self.valid_game_id = 'XVqKzNYO50'
        self.invalid_game_id = None

    def test_returns_dict(self):
        result = db_game_shots.get_total_shots_on_target_by_game_id(self.valid_game_id)
        self.assertIsInstance(result, dict)

    def test_counts_are_positive_ints(self):
        result = db_game_shots.get_total_shots_on_target_by_game_id(self.valid_game_id)
        self.assertTrue(all(isinstance(count, int) and count >= 0 for count in result.values()))
        self.assertGreaterEqual(sum(result.values()), 1)

    def test_raises_on_invalid_game_id(self):
        with self.assertRaises(ValueError):
            db_game_shots.get_total_shots_on_target_by_game_id(self.invalid_game_id)

if __name__ == '__main__':
    unittest.main()