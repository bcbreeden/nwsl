import unittest
from .player_xgoal_strength import *

import unittest

# Assume the function calculate_player_xgoal_strength and XGOAL_WEIGHTS are already defined

class TestCalculatePlayerXGoalStrength(unittest.TestCase):

    def test_valid_normalized_stats(self):
        normalized_player_stats = {
            "minutes_played": 1.0,
            "shots": 0.9,
            "shots_on_target": 0.8,
            "goals": 0.7,
            "xgoals": 0.6,
            "key_passes": 0.5,
            "primary_assists": 0.4,
            "xassists": 0.3,
            "points_added": 0.2,
            "xpoints_added": 0.1
        }
        result = calculate_player_xgoal_strength(normalized_player_stats)
        expected_strength = sum(
            normalized_player_stats[stat] * XGOAL_WEIGHTS[stat]
            for stat in normalized_player_stats
        )
        self.assertAlmostEqual(result, expected_strength)

    def test_excluded_keys(self):
        normalized_player_stats = {
            "minutes_played": 0.8,
            "goals": 0.7,
            "season": 2023,
            "height_ft": 6,
            "height_in": 2
        }
        result = calculate_player_xgoal_strength(normalized_player_stats)
        expected_strength = (
            normalized_player_stats["minutes_played"] * XGOAL_WEIGHTS["minutes_played"] +
            normalized_player_stats["goals"] * XGOAL_WEIGHTS["goals"]
        )
        self.assertAlmostEqual(result, expected_strength)

    def test_missing_keys(self):
        normalized_player_stats = {
            "shots": 0.85,
            "xgoals": 0.75,
            "points_added": 0.65
        }
        result = calculate_player_xgoal_strength(normalized_player_stats)
        expected_strength = (
            normalized_player_stats["shots"] * XGOAL_WEIGHTS["shots"] +
            normalized_player_stats["xgoals"] * XGOAL_WEIGHTS["xgoals"] +
            normalized_player_stats["points_added"] * XGOAL_WEIGHTS["points_added"]
        )
        self.assertAlmostEqual(result, expected_strength)

    def test_empty_normalized_stats(self):
        normalized_player_stats = {}
        result = calculate_player_xgoal_strength(normalized_player_stats)
        self.assertEqual(result, 0)

    def test_zero_normalized_stats(self):
        normalized_player_stats = {
            "minutes_played": 0,
            "shots": 0,
            "goals": 0,
            "xgoals": 0
        }
        result = calculate_player_xgoal_strength(normalized_player_stats)
        self.assertEqual(result, 0)

if __name__ == "__main__":
    unittest.main()