from data import db_games
import unittest
import sqlite3

class TestDbGames(unittest.TestCase):

    def setUp(self):
        self.valid_game_id = "XVqKzNYO50"
        self.valid_team_id = "Pk5LeeNqOW"
        self.invalid_team_id = "abc123"
        self.valid_season = 2024
        self.invalid_season = 2999
        self.valid_stadium_id = "p6qbX06M0G"
        self.invalid_stadium_id = "invalidStadium123"
        self.expected_keys = {
            'game_id', 'date_time_utc', 'date_time_est', 'home_score', 'away_score',
            'home_team_id', 'away_team_id', 'referee_id', 'stadium_id',
            'home_manager_id', 'away_manager_id', 'expanded_minutes', 'season_name',
            'matchday', 'attendance', 'knockout_game', 'status', 'last_updated_utc',
            'last_updated_est', 'season',
            'home_team_name', 'home_team_short_name', 'home_team_abbreviation',
            'away_team_name', 'away_team_short_name', 'away_team_abbreviation'
        }

    def test_get_game_by_id_returns_valid_data(self):
        """Test that get_game_by_id returns a row with expected keys and non-empty values."""
        row = db_games.get_game_by_id(self.valid_game_id)
        self.assertIsNotNone(row, "Expected non-None result for valid game_id")
        self.assertIsInstance(row, sqlite3.Row)

        actual_keys = set(row.keys())
        self.assertEqual(actual_keys, self.expected_keys, "Returned row keys do not match schema")
        self.assertIsNotNone(row["game_id"])
        self.assertIsInstance(row["home_score"], int)
        self.assertIsInstance(row["away_score"], int)
        self.assertTrue(len(row["home_team_name"]) > 0)
        self.assertTrue(len(row["away_team_name"]) > 0)

    def test_get_game_by_id_with_invalid_id_returns_none(self):
        """Test that get_game_by_id returns None for an invalid game_id."""
        result = db_games.get_game_by_id("nonexistent123")
        self.assertIsNone(result)

    def test_get_game_by_id_with_null_input_raises_exception(self):
        """Test that passing None as game_id raises a ValueError."""
        with self.assertRaises(ValueError):
            db_games.get_game_by_id(None)

    def test_get_game_by_id_with_non_string_input_raises_exception(self):
        """Test that passing a non-string game_id raises a ValueError."""
        with self.assertRaises(ValueError):
            db_games.get_game_by_id(12345)

    def test_get_game_ids_by_season_returns_list(self):
        """Test that get_game_ids_by_season returns a non-empty list of string IDs."""
        game_ids = db_games.get_game_ids_by_season(self.valid_season)
        self.assertIsInstance(game_ids, list)
        self.assertGreater(len(game_ids), 0)
        for game_id in game_ids:
            self.assertIsInstance(game_id, str)
            self.assertTrue(len(game_id) > 0)

    def test_get_game_ids_by_season_invalid_input_type_raises(self):
        """Test that non-integer input raises a ValueError."""
        with self.assertRaises(ValueError):
            db_games.get_game_ids_by_season("invalid")

    def test_get_game_ids_by_season_null_input_raises(self):
        """Test that None input raises a ValueError."""
        with self.assertRaises(ValueError):
            db_games.get_game_ids_by_season(None)

    def test_get_game_ids_match_all_games_query(self):
        """Test consistency between get_game_ids_by_season and get_all_games_by_season."""
        game_ids = set(db_games.get_game_ids_by_season(self.valid_season))
        all_game_ids = set(row["game_id"] for row in db_games.get_all_games_by_season(self.valid_season))
        self.assertTrue(game_ids.issubset(all_game_ids))
        self.assertGreater(len(game_ids), 0)

    def test_get_latest_manager_id_valid_team_and_season(self):
        """Test that the function returns a valid manager ID for a known team and season."""
        team_id = self.valid_team_id  # Replace with valid team_id from your test database
        season = self.valid_season
        manager_id = db_games.get_latest_manager_id_by_team_and_season(team_id, season)
        self.assertIsNotNone(manager_id, "Expected a valid manager ID")
        self.assertIsInstance(manager_id, str)
        self.assertGreater(len(manager_id), 0)

    def test_get_latest_manager_id_invalid_team(self):
        """Test that the function returns None for a nonexistent team ID."""
        team_id = "invalidTeam123"
        season = self.valid_season
        manager_id = db_games.get_latest_manager_id_by_team_and_season(team_id, season)
        self.assertIsNone(manager_id)

    def test_get_latest_manager_id_invalid_season(self):
        """Test that the function returns None for a valid team but invalid season."""
        team_id = self.valid_team_id
        season = self.invalid_season 
        manager_id = db_games.get_latest_manager_id_by_team_and_season(team_id, season)
        self.assertIsNone(manager_id)

    def test_get_latest_manager_id_invalid_input_types(self):
        """Test that the function raises ValueError for invalid input types."""
        with self.assertRaises(ValueError):
            db_games.get_latest_manager_id_by_team_and_season(None, self.valid_season)
        with self.assertRaises(ValueError):
            db_games.get_latest_manager_id_by_team_and_season(self.valid_team_id, str(self.valid_season))

    def test_get_team_record_valid_inputs(self):
        """Test that a valid team_id and season return a record with wins, losses, and draws."""
        result = db_games.get_team_record_by_season(self.valid_team_id, self.valid_season)
        self.assertIsInstance(result, dict)
        self.assertIn("wins", result)
        self.assertIn("losses", result)
        self.assertIn("draws", result)
        self.assertIsInstance(result["wins"], int)
        self.assertIsInstance(result["losses"], int)
        self.assertIsInstance(result["draws"], int)

    def test_get_team_record_invalid_team_id(self):
        """Test that an invalid team_id returns a record with None values (no games found)."""
        result = db_games.get_team_record_by_season(self.invalid_team_id, self.valid_season)
        self.assertEqual(result, {'wins': None, 'losses': None, 'draws': None})


    def test_get_team_record_invalid_season(self):
        """Test that an invalid season still returns a record with zeroed stats."""
        result = db_games.get_team_record_by_season(self.valid_team_id, self.invalid_season)
        self.assertEqual(result, {'wins': None, 'losses': None, 'draws': None})

    def test_get_team_record_with_null_team_id(self):
        """Test that passing None as team_id raises a ValueError."""
        with self.assertRaises(ValueError):
            db_games.get_team_record_by_season(None, self.valid_season)

    def test_get_team_record_with_non_string_team_id(self):
        """Test that a non-string team_id raises a ValueError."""
        with self.assertRaises(ValueError):
            db_games.get_team_record_by_season(12345, self.valid_season)

    def test_get_team_record_with_null_season(self):
        """Test that passing None as season raises a ValueError."""
        with self.assertRaises(ValueError):
            db_games.get_team_record_by_season(self.valid_team_id, None)

    def test_get_team_record_with_non_int_season(self):
        """Test that a non-integer season raises a ValueError."""
        with self.assertRaises(ValueError):
            db_games.get_team_record_by_season(self.valid_team_id, str(self.valid_season))

    def test_get_team_game_results_valid(self):
        """Test that get_team_game_results returns expected result structure and content."""
        team_id = "KPqjw8PQ6v"  # Replace with a valid team_id in your test DB
        season = self.valid_season
        results = db_games.get_team_game_results(team_id, season)

        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0, "Expected at least one result for valid team/season")

        for match in results:
            self.assertIsInstance(match, dict)
            expected_keys = {
                "game_id", "home_game", "result", "opponent", "opponent_name",
                "opponent_short_name", "opponent_abbreviation", "goals_scored",
                "goals_against", "date_time_est"
            }
            self.assertEqual(set(match.keys()), expected_keys, "Returned result keys do not match expected format")
            self.assertIn(match["result"], ["win", "loss", "draw"], "Unexpected match result value")
            self.assertIsInstance(match["home_game"], bool)
            self.assertIsInstance(match["goals_scored"], int)
            self.assertIsInstance(match["goals_against"], int)

    def test_get_team_game_results_invalid_team(self):
        """Test that get_team_game_results returns an empty list for invalid team_id."""
        results = db_games.get_team_game_results(self.invalid_team_id, self.valid_season)
        self.assertIsInstance(results, list)
        self.assertEqual(results, [], "Expected empty list for invalid team_id")

    def test_get_team_game_results_invalid_season(self):
        """Test that get_team_game_results returns an empty list for a valid team but nonexistent season."""
        results = db_games.get_team_game_results(self.valid_team_id, self.invalid_season)
        self.assertIsInstance(results, list)
        self.assertEqual(results, [], "Expected empty list for valid team_id but non-existent season")

    def test_get_team_game_results_raises_on_null(self):
        """Test that passing null values raises a ValueError."""
        with self.assertRaises(ValueError):
            db_games.get_team_game_results(None, self.valid_season)

        with self.assertRaises(ValueError):
            db_games.get_team_game_results(self.valid_team_id, None)

    def test_get_team_game_results_raises_on_invalid_types(self):
        """Test that passing incorrect types raises a ValueError."""
        with self.assertRaises(ValueError):
            db_games.get_team_game_results(123, self.valid_season)

        with self.assertRaises(ValueError):
            db_games.get_team_game_results(self.valid_team_id, str(self.valid_season))

    def test_get_most_recent_home_stadium_id_valid(self):
        """Test that the most recent home stadium ID is returned correctly for a valid team and season."""
        result = db_games.get_most_recent_home_stadium_id(self.valid_team_id, self.valid_season)
        self.assertIsNotNone(result, "Expected a stadium_id but got None")
        self.assertIsInstance(result, str)
        self.assertEqual(result, self.valid_stadium_id, "Returned stadium ID does not match expected value")

    def test_get_most_recent_home_stadium_id_invalid_team(self):
        """Test that None is returned for an invalid team ID."""
        result = db_games.get_most_recent_home_stadium_id(self.invalid_team_id, self.valid_season)
        self.assertIsNone(result, "Expected None for invalid team ID")

    def test_get_most_recent_home_stadium_id_invalid_season(self):
        """Test that None is returned for a valid team ID but invalid season."""
        result = db_games.get_most_recent_home_stadium_id(self.valid_team_id, self.invalid_season)
        self.assertIsNone(result, "Expected None for invalid season")

    def test_get_most_recent_home_stadium_id_null_team(self):
        """Test that passing None as the team_id raises a ValueError."""
        with self.assertRaises(ValueError):
            db_games.get_most_recent_home_stadium_id(None, self.valid_season)

    def test_get_most_recent_home_stadium_id_null_season(self):
        """Test that passing None as the season raises a ValueError."""
        with self.assertRaises(ValueError):
            db_games.get_most_recent_home_stadium_id(self.valid_team_id, None)

    def test_get_most_recent_home_stadium_id_non_string_team_id(self):
        """Test that a non-string team ID raises a ValueError."""
        with self.assertRaises(ValueError):
            db_games.get_most_recent_home_stadium_id(12345, self.valid_season)

    def test_get_most_recent_home_stadium_id_non_int_season(self):
        """Test that a non-integer season raises a ValueError."""
        with self.assertRaises(ValueError):
            db_games.get_most_recent_home_stadium_id(self.valid_team_id, "spring2024")
    

if __name__ == '__main__':
    unittest.main()
