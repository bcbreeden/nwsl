import unittest
from unittest.mock import patch, MagicMock
from .player_xgoal_strength import *

class TestCalculatePlayerXGoalStrength(unittest.TestCase):
    def setUp(self):
        """
        Common setup for all tests in this class.
        """
        # Example static weights for testing. 
        # Pass them in explicitly to avoid patching generate_player_stat_weights.
        self.mock_weights = {
            "shots": 0.5,
            "goals": 1.0,
            "xgoals": 0.8,
            "key_passes": 0.7,
            "xassists": 0.6,
            "points_added": 0.4,
        }

    def test_player_below_minimum_play_time_returns_zero(self):
        """
        If a player hasn't met MIN_PLAYING_TIME_THRESHOLD minutes,
        calculate_player_xgoal_strength should return 0.
        """
        stats = {"minutes_played": MIN_PLAYING_TIME_THRESHOLD - 1, "shots": 10, "goals": 2}
        result = calculate_player_xgoal_strength(stats, xgoals_weight=self.mock_weights)
        self.assertEqual(result, 0)

    def test_player_meets_minimum_play_time(self):
        """
        If a player has >= MIN_PLAYING_TIME_THRESHOLD minutes:
          - Convert stats to per-90 
          - Multiply by corresponding weight
          - Sum up
          - Then multiply by 100 and round to 3 decimals
        """
        stats = {
            "minutes_played": 400,
            "shots": 20,       # => per-90 = (20/400)*90 = 4.5
            "goals": 5,        # => per-90 = 1.125
            "xgoals": 4,       # => per-90 = 0.9
            "key_passes": 10,  # => per-90 = 2.25
            "xassists": 3,     # => per-90 = 0.675
            "points_added": 2, # => per-90 = 0.45
        }
        # Include excluded metrics to confirm they don't affect the result
        stats["season"] = 2023
        stats["height_ft"] = 5

        result = calculate_player_xgoal_strength(stats, xgoals_weight=self.mock_weights)

        # Let's calculate the expected sum manually (the "raw strength"):
        # -------------------------------------------------------------
        #   shots (4.5)       * 0.5  = 2.25
        #   goals (1.125)     * 1.0  = 1.125
        #   xgoals (0.9)      * 0.8  = 0.72
        #   key_passes (2.25) * 0.7  = 1.575
        #   xassists (0.675)  * 0.6  = 0.405
        #   points_added (0.45)*0.4  = 0.18
        # -------------------------------------------------------------
        #   raw_strength = 6.255
        #
        # Now the function multiplies by 100 => 6.255 * 100 = 625.5
        # and rounds to 3 decimals => 625.5
        expected = 625.5

        self.assertAlmostEqual(result, expected, places=3)

    def test_player_zero_stats(self):
        """
        If the player has zero for included stats, the result should be 0
        (provided minutes >= threshold).
        """
        stats = {
            "minutes_played": 400,
            "shots": 0,
            "goals": 0,
            "xgoals": 0,
            "key_passes": 0,
            "xassists": 0
        }
        result = calculate_player_xgoal_strength(stats, xgoals_weight=self.mock_weights)
        # raw_strength = 0 => final is 0 * 100 = 0
        self.assertEqual(result, 0)

    def test_excluded_metrics_ignored_in_calculation(self):
        """
        Excluded metrics should not contribute to the final result.
        """
        custom_weights = {
            "shots": 1.0,
            "goals": 1.0,
        }
        stats = {
            "minutes_played": 400,
            "shots": 10,   # => per-90 = 2.25
            "goals": 5,    # => per-90 = 1.125
            # Excluded metrics that should be ignored:
            "season": 2023,
            "height_ft": 6,
            "height_in": 2,
            "shots_on_target_perc": 0.75,
            "primary_assists_minus_xassists": 3,
            "goals_minus_xgoals": -1,
        }
        result = calculate_player_xgoal_strength(stats, xgoals_weight=custom_weights)
        # raw_strength = 2.25*1.0 + 1.125*1.0 = 3.375
        # => final = 3.375 * 100 = 337.5 => round(337.5,3) => 337.5
        expected = 337.5
        self.assertAlmostEqual(result, expected, places=3)

if __name__ == "__main__":
    unittest.main()