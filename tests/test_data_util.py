import unittest
import os
from data import data_util

class TestDataUtils(unittest.TestCase):
    
    def test_single_player(self):
        """Test with a single player for a single stat."""
        filtered_players = [
            {'general_position': 'Forward', 'score': 10}
        ]
        stats_to_track = ['score']
        expected = {
            'Forward': {
                'avg_score': 10.0,
                'min_score': 10,
                'max_score': 10
            }
        }
        result = data_util.aggregate_position_data(filtered_players, stats_to_track)
        self.assertEqual(result, expected)
        
    def test_multiple_players_same_position(self):
        """Test with multiple players in the same position and multiple stats."""
        filtered_players = [
            {'general_position': 'Midfielder', 'score': 5, 'assists': 2},
            {'general_position': 'Midfielder', 'score': 7, 'assists': 3}
        ]
        stats_to_track = ['score', 'assists']
        expected = {
            'Midfielder': {
                'avg_score': 6.0,
                'min_score': 5,
                'max_score': 7,
                'avg_assists': 2.5,
                'min_assists': 2,
                'max_assists': 3
            }
        }
        result = data_util.aggregate_position_data(filtered_players, stats_to_track)
        self.assertEqual(result, expected)

    def test_multiple_positions(self):
        """Test aggregation when players are in different positions."""
        filtered_players = [
            {'general_position': 'Defender', 'goals': 0},
            {'general_position': 'Forward', 'goals': 1},
            {'general_position': 'Forward', 'goals': 2},
        ]
        stats_to_track = ['goals']
        expected = {
            'Defender': {
                'avg_goals': 0.0,
                'min_goals': 0,
                'max_goals': 0,
            },
            'Forward': {
                'avg_goals': 1.5,
                'min_goals': 1,
                'max_goals': 2,
            }
        }
        result = data_util.aggregate_position_data(filtered_players, stats_to_track)
        self.assertEqual(result, expected)
    
    def test_missing_general_position(self):
        """Test that players missing the 'general_position' key are grouped under a default."""
        filtered_players = [
            {'score': 10}  # No 'general_position' key provided.
        ]
        stats_to_track = ['score']
        expected = {
            'Unknown General Position': {
                'avg_score': 10.0,
                'min_score': 10,
                'max_score': 10
            }
        }
        result = data_util.aggregate_position_data(filtered_players, stats_to_track)
        self.assertEqual(result, expected)
        
    def test_missing_stat_value(self):
        """Test that missing or None stat values default to 0."""
        filtered_players = [
            {'general_position': 'Goalkeeper', 'saves': None},
            {'general_position': 'Goalkeeper'}  # Missing 'saves' key.
        ]
        stats_to_track = ['saves']
        expected = {
            'Goalkeeper': {
                'avg_saves': 0.0,
                'min_saves': 0,
                'max_saves': 0
            }
        }
        result = data_util.aggregate_position_data(filtered_players, stats_to_track)
        self.assertEqual(result, expected)
        
    def test_empty_filtered_players(self):
        """Test the edge case where the list of players is empty."""
        filtered_players = []
        stats_to_track = ['score']
        expected = {}
        result = data_util.aggregate_position_data(filtered_players, stats_to_track)
        self.assertEqual(result, expected)
    
    def test_generate_player_season_id_basic(self):
        """Test that generate_player_season_id returns correct string for typical input."""
        result = data_util.generate_player_season_id(123, 2025)
        assert result == "1232025"

    def test_generate_player_season_id_with_zero(self):
        """Test generate_player_season_id when player_id or season is 0."""
        result = data_util.generate_player_season_id(0, 2020)
        assert result == "02020"

    def test_generate_player_season_id_with_string_input(self):
        """Test generate_player_season_id with string player_id."""
        result = data_util.generate_player_season_id("abc", 2024)
        assert result == "abc2024"

    def test_get_db_path_absolute(self):
        """Test that get_db_path returns an absolute path."""
        db_path = data_util.get_db_path()
        assert os.path.isabs(db_path)

    def test_get_db_path_filename(self):
        """Test that get_db_path ends with 'nwsl.db'."""
        db_path = data_util.get_db_path()
        assert db_path.endswith('nwsl.db')

    def test_get_db_path_location(self):
        """Test that get_db_path returns the correct location."""
        expected_dir = os.path.dirname(os.path.abspath(data_util.__file__))
        expected_path = os.path.join(expected_dir, 'nwsl.db')
        assert data_util.get_db_path() == expected_path
    
    def test_validate_id_valid(self):
        """Test that validate_id passes with a non-empty string."""
        try:
            data_util.validate_id("abc123")  # Should not raise
        except Exception as e:
            self.fail(f"validate_id raised an exception unexpectedly: {e}")

    def test_validate_id_invalid(self):
        """Test that validate_id raises ValueError with None or non-string."""
        with self.assertRaises(ValueError):
            data_util.validate_id(None)
        with self.assertRaises(ValueError):
            data_util.validate_id(123)
        with self.assertRaises(ValueError):
            data_util.validate_id("")

    def test_validate_season_valid(self):
        """Test that validate_season passes with a valid integer."""
        try:
            data_util.validate_season(2025)  # Should not raise
        except Exception as e:
            self.fail(f"validate_season raised an exception unexpectedly: {e}")

    def test_validate_season_invalid(self):
        """Test that validate_season raises ValueError with None, 0, or non-int."""
        with self.assertRaises(ValueError):
            data_util.validate_season(None)
        with self.assertRaises(ValueError):
            data_util.validate_season("2025")
        with self.assertRaises(ValueError):
            data_util.validate_season(0)

    def test_convert_utc_to_est_valid(self):
        """Test converting a valid UTC datetime string to Eastern Time formatted string."""
        utc_input = "2025-05-26 02:00:00 UTC"
        result = data_util.convert_utc_to_est(utc_input)
        self.assertIsInstance(result, str)
        self.assertIn("at", result)
        self.assertRegex(result, r"\w+, \w+ \d{1,2} at \d{1,2}:\d{2} [AP]M")

    def test_convert_utc_to_est_with_placeholder_string(self):
        """Test that placeholder string returns None."""
        placeholder = "Unknown Last Updated Time"
        result = data_util.convert_utc_to_est(placeholder)
        self.assertIsNone(result)

    def test_convert_utc_to_est_invalid_format(self):
        """Test that invalid datetime format raises a ValueError."""
        with self.assertRaises(ValueError):
            data_util.convert_utc_to_est("01-06-2024 19:00 UTC")

    def test_convert_utc_to_est_empty_string(self):
        """Test that an empty string raises a ValueError."""
        with self.assertRaises(ValueError):
            data_util.convert_utc_to_est("")
        
if __name__ == '__main__':
    unittest.main()