import unittest
from .normalize import *

class TestNormalize(unittest.TestCase):
    def setUp(self):
        # Sample stat ranges for normalization
        self.stat_ranges = {
            'shots': (0, 100),
            'goals': (0, 50),
            'assists': (0, 20),
            'xgoals': (0, 40)
        }

    def test_normalize_numeric_stats(self):
        player_stats = {
            'name': 'Alex Morgan',
            'team': 'San Diego Wave',
            'shots': 80,
            'goals': 25,
            'assists': 10,
            'xgoals': 30
        }
        
        # Expected normalized values based on the ranges
        expected_output = {
            'shots': 0.8,
            'goals': 0.5,
            'assists': 0.5,
            'xgoals': 0.75
        }

        normalized_stats = normalize_player_stats(player_stats, self.stat_ranges)
        self.assertEqual(normalized_stats, expected_output)

    def test_filter_non_numeric_values(self):
        player_stats = {
            'name': 'Megan Rapinoe',
            'shots': 50,
            'goals': 20,
            'season': '2023'
        }

        # Non-numeric fields should be filtered out
        normalized_stats = normalize_player_stats(player_stats, self.stat_ranges)
        self.assertNotIn('name', normalized_stats)
        self.assertNotIn('season', normalized_stats)

    def test_stat_without_range(self):
        player_stats = {
            'shots': 90,
            'goals': 40,
            'unknown_stat': 100  # This stat is not in stat_ranges
        }

        # unknown_stat should remain unchanged since it has no range
        normalized_stats = normalize_player_stats(player_stats, self.stat_ranges)
        self.assertEqual(normalized_stats['unknown_stat'], 100)

    def test_empty_player_stats(self):
        player_stats = {}
        normalized_stats = normalize_player_stats(player_stats, self.stat_ranges)
        self.assertEqual(normalized_stats, {})
    
    def test_standard_normalization(self):
        self.assertAlmostEqual(normalize(50, 0, 100), 0.5)
        self.assertAlmostEqual(normalize(75, 50, 100), 0.5)
        self.assertAlmostEqual(normalize(0, 0, 100), 0.0)
        self.assertAlmostEqual(normalize(100, 0, 100), 1.0)

    def test_negative_values(self):
        self.assertAlmostEqual(normalize(-50, -100, 0), 0.5)
        self.assertAlmostEqual(normalize(-100, -100, 0), 0.0)
        self.assertAlmostEqual(normalize(0, -100, 0), 1.0)

    def test_stat_equals_min_val(self):
        self.assertEqual(normalize(0, 0, 100), 0.0)
        self.assertEqual(normalize(-100, -100, 0), 0.0)

    def test_stat_equals_max_val(self):
        self.assertEqual(normalize(100, 0, 100), 1.0)
        self.assertEqual(normalize(0, -100, 0), 1.0)

    def test_division_by_zero(self):
        self.assertEqual(normalize(50, 50, 50), 0)
        self.assertEqual(normalize(0, 0, 0), 0)
        self.assertEqual(normalize(-100, -100, -100), 0)

    def test_out_of_bounds_values(self):
        self.assertLess(normalize(-10, 0, 100), 0.0)
        self.assertGreater(normalize(110, 0, 100), 1.0)

if __name__ == '__main__':
    unittest.main()