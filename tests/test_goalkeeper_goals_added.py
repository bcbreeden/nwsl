import unittest
from data import db_goalkeeper_goals_added

class TestDbGoalkeeperGoalsAdded(unittest.TestCase):
    def setUp(self):
        self.valid_player_id = "ljqE2r4oQx"
        self.valid_season = 2024
        self.expected_columns = {
            "player_id": str,
            "team_id": str,
            "season": int,
            "claiming_goals_added_raw": float,
            "claiming_goals_added_above_avg": float,
            "claiming_count_actions": int,
            "fielding_goals_added_raw": float,
            "fielding_goals_added_above_avg": float,
            "fielding_count_actions": int,
            "handling_goals_added_raw": float,
            "handling_goals_added_above_avg": float,
            "handling_count_actions": int,
            "passing_goals_added_raw": float,
            "passing_goals_added_above_avg": float,
            "passing_count_actions": int,
            "shotstopping_goals_added_raw": float,
            "shotstopping_goals_added_above_avg": float,
            "shotstopping_count_actions": int,
            "sweeping_goals_added_raw": float,
            "sweeping_goals_added_above_avg": float,
            "sweeping_count_actions": int
        }

    def test_get_goalkeeper_goals_added_by_season(self):
        """Test that a specific goalkeeper's data contains expected columns, types, and values."""
        row = db_goalkeeper_goals_added.get_goalkeeper_goals_added_by_season(
            self.valid_player_id, self.valid_season
        )
        self.assertIsNotNone(row, "Expected data for valid player and season but got None")
        row_dict = dict(row)

        for col, dtype in self.expected_columns.items():
            self.assertIn(col, row_dict, f"Missing column: {col}")
            self.assertIsNotNone(row_dict[col], f"Column {col} is None")
            if dtype == float:
                self.assertIsInstance(row_dict[col], (float, int), f"{col} is not a float/int")
            else:
                self.assertIsInstance(row_dict[col], dtype, f"{col} is not of type {dtype}")

    def test_get_all_goalkeeper_goals_added_by_season(self):
        """Test that all goalkeeper records for the season are present and valid."""
        rows = db_goalkeeper_goals_added.get_all_goalkeeper_goals_added_by_season(self.valid_season)
        self.assertIsInstance(rows, list)
        self.assertGreater(len(rows), 0, "No rows returned for valid season")

        for row in rows:
            row_dict = dict(row)
            for col, dtype in self.expected_columns.items():
                self.assertIn(col, row_dict, f"Missing column: {col}")
                self.assertIsNotNone(row_dict[col], f"Column {col} is None")
                if dtype == float:
                    self.assertIsInstance(row_dict[col], (float, int), f"{col} is not a float/int")
                else:
                    self.assertIsInstance(row_dict[col], dtype, f"{col} is not of type {dtype}")

    def test_fetch_keeper_goals_added_data_valid(self):
        """Test fetch_keeper_goals_added_data returns enriched keeper dictionaries with expected fields."""
        data = db_goalkeeper_goals_added.fetch_keeper_goals_added_data(self.valid_season)

        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0, "No keeper data returned for valid season")

        # Validate that enriched keys exist for at least one keeper
        found_required_keys = False
        for keeper in data:
            if not isinstance(keeper, dict):
                continue
            for key_base in ['claiming', 'fielding', 'handling', 'passing', 'shotstopping', 'sweeping']:
                raw_key = f"{key_base}_goals_added_raw"
                avg_key = f"{key_base}_goals_added_above_avg"
                count_key = f"{key_base}_count_actions"

                if raw_key in keeper and avg_key in keeper and count_key in keeper:
                    self.assertIsInstance(keeper[raw_key], (float, int))
                    self.assertIsInstance(keeper[avg_key], (float, int))
                    self.assertIsInstance(keeper[count_key], int)
                    found_required_keys = True
        self.assertTrue(found_required_keys, "No enriched action data found in fetched keepers")

    def test_calculate_player_statistics_filters_correctly(self):
        """Test that players with minutes_played below MINIMUM_MINUTES are excluded."""
        keepers_data = [
            {"player_id": "p1", "minutes_played": 1200},
            {"player_id": "p2", "minutes_played": 300},
            {"player_id": "p3", "minutes_played": 45},  # Should be filtered out
            {"player_id": "p4", "minutes_played": 0}   # Should be filtered out
        ]

        result = db_goalkeeper_goals_added.calculate_player_statistics(keepers_data)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)
        player_ids = [p["player_id"] for p in result]
        self.assertIn("p1", player_ids)
        self.assertIn("p2", player_ids)
        self.assertNotIn("p3", player_ids)
        self.assertNotIn("p4", player_ids)

    def test_calculate_player_statistics_empty_result(self):
        """Test that an empty list is returned when all players are below threshold."""
        keepers_data = [
            {"player_id": "low1", "minutes_played": 10},
            {"player_id": "low2", "minutes_played": 0}
        ]

        result = db_goalkeeper_goals_added.calculate_player_statistics(keepers_data)
        self.assertEqual(result, [])

