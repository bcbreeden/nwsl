# import unittest
# from .player_xgoal_strength import *

# import unittest

# # Assume the function calculate_player_xgoal_strength and XGOAL_WEIGHTS are already defined

# class TestCalculatePlayerXGoalStrength(unittest.TestCase):

#     def test_valid_normalized_stats(self):
#         normalized_player_stats = {
#             "minutes_played": 1.0,
#             "shots": 0.9,
#             "shots_on_target": 0.8,
#             "goals": 0.7,
#             "xgoals": 0.6,
#             "key_passes": 0.5,
#             "primary_assists": 0.4,
#             "xassists": 0.3,
#             "points_added": 0.2,
#             "xpoints_added": 0.1
#         }
#         result = calculate_player_xgoal_strength(normalized_player_stats)
#         expected_strength = sum(
#             normalized_player_stats[stat] * XGOAL_WEIGHTS[stat]
#             for stat in normalized_player_stats
#         )
#         self.assertAlmostEqual(result, expected_strength)

#     def test_excluded_keys(self):
#         normalized_player_stats = {
#             "minutes_played": 0.8,
#             "goals": 0.7,
#             "season": 2023,
#             "height_ft": 6,
#             "height_in": 2
#         }
#         result = calculate_player_xgoal_strength(normalized_player_stats)
#         expected_strength = (
#             normalized_player_stats["minutes_played"] * XGOAL_WEIGHTS["minutes_played"] +
#             normalized_player_stats["goals"] * XGOAL_WEIGHTS["goals"]
#         )
#         self.assertAlmostEqual(result, expected_strength)

#     def test_missing_keys(self):
#         normalized_player_stats = {
#             "shots": 0.85,
#             "xgoals": 0.75,
#             "points_added": 0.65
#         }
#         result = calculate_player_xgoal_strength(normalized_player_stats)
#         expected_strength = (
#             normalized_player_stats["shots"] * XGOAL_WEIGHTS["shots"] +
#             normalized_player_stats["xgoals"] * XGOAL_WEIGHTS["xgoals"] +
#             normalized_player_stats["points_added"] * XGOAL_WEIGHTS["points_added"]
#         )
#         self.assertAlmostEqual(result, expected_strength)

#     def test_empty_normalized_stats(self):
#         normalized_player_stats = {}
#         result = calculate_player_xgoal_strength(normalized_player_stats)
#         self.assertEqual(result, 0)

#     def test_zero_normalized_stats(self):
#         normalized_player_stats = {
#             "minutes_played": 0,
#             "shots": 0,
#             "goals": 0,
#             "xgoals": 0
#         }
#         result = calculate_player_xgoal_strength(normalized_player_stats)
#         self.assertEqual(result, 0)

# if __name__ == "__main__":
#     unittest.main()

import unittest
from unittest.mock import patch, MagicMock
from .player_xgoal_strength import *
class TestCalculatePlayerXGoalStrength(unittest.TestCase):
    def setUp(self):
        # Define a static weights dictionary for testing.
        self.test_weights = {
            "shots": 0.5,
            "goals": 1.0,
            "xgoals": 0.8,
            "key_passes": 0.7,
            "xassists": 0.6,
            "points_added": 0.4
        }

    def test_player_below_minimum_threshold_returns_zero(self):
        normalized_stats = {"minutes_played": 200, "shots": 10, "goals": 2}
        result = calculate_player_xgoal_strength(
            normalized_stats, 
            xgoals_weight=self.test_weights
        )
        self.assertEqual(result, 0, 
            "Expected 0 for a player below the minutes threshold."
        )

    def test_player_meets_minimum_play_time(self):
        normalized_stats = {
            "minutes_played": 400,  # meets threshold exactly
            "shots": 20,           # => per-90 = 4.5
            "goals": 5,            # => 1.125
            "xgoals": 4,           # => 0.9
            "key_passes": 10,      # => 2.25
            "xassists": 3,         # => 0.675
            "points_added": 2      # => 0.45
        }
        # Include excluded metrics to ensure they're ignored
        normalized_stats["season"] = 2023
        normalized_stats["height_ft"] = 5

        result = calculate_player_xgoal_strength(
            normalized_stats, 
            xgoals_weight=self.test_weights
        )

        # Let's calculate the expected sum manually:
        # shots per-90 = (20 / 400)*90 = 4.5
        #  => 4.5 * 0.5   = 2.25
        # goals per-90 = (5 / 400)*90 = 1.125
        #  => 1.125 * 1.0 = 1.125
        # xgoals per-90 = 0.9
        #  => 0.9 * 0.8   = 0.72
        # key_passes per-90 = 2.25
        #  => 2.25 * 0.7  = 1.575
        # xassists per-90 = 0.675
        #  => 0.675 * 0.6 = 0.405
        # points_added per-90 = 0.45
        #  => 0.45 * 0.4  = 0.18
        # ---------------------------------------
        # total = 2.25 + 1.125 + 0.72 + 1.575 + 0.405 + 0.18 = 6.255
        # round(6.255, 3) => 6.255

        self.assertAlmostEqual(result, 6.255, places=3)

    def test_zero_stats_above_threshold(self):
        normalized_stats = {
            "minutes_played": 400,
            "shots": 0,
            "goals": 0,
            "xgoals": 0,
            "key_passes": 0,
            "xassists": 0,
            "points_added": 0
        }
        result = calculate_player_xgoal_strength(
            normalized_stats, 
            xgoals_weight=self.test_weights
        )
        self.assertEqual(result, 0,
            "Expected 0 for a player with all zero stats, even if above threshold."
        )

    def test_excluded_metrics_ignored_in_calculation(self):
        custom_weights = {
            "shots": 1.0,
            "goals": 1.0
        }
        normalized_stats = {
            "minutes_played": 400,
            "shots": 10,   # => per-90 = 2.25
            "goals": 5,    # => per-90 = 1.125
            # Excluded metrics
            "season": 2023,
            "height_ft": 6,
            "height_in": 2,
            "shots_on_target_perc": 0.75,
            "primary_assists_minus_xassists": 3,
            "goals_minus_xgoals": -1
        }
        result = calculate_player_xgoal_strength(
            normalized_stats, 
            xgoals_weight=custom_weights
        )
        # Weighted sum = 2.25*1.0 + 1.125*1.0 = 3.375 => round(3.375, 3)
        self.assertAlmostEqual(result, 3.375, places=3)

if __name__ == "__main__":
    unittest.main()