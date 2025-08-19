from data.normalize import normalize, normalize_player_stats
import unittest

class TestNormalizeFunctions(unittest.TestCase):
    def test_normalize_standard_case(self):
        """Test normalize function with a valid stat, min, and max."""
        result = normalize(50, 0, 100)
        self.assertAlmostEqual(result, 0.5)

    def test_normalize_zero_range(self):
        """Test normalize function when min_val == max_val (should return 0)."""
        result = normalize(10, 10, 10)
        self.assertEqual(result, 0)

    def test_normalize_negative_range(self):
        """Test normalize function with negative range values."""
        result = normalize(-25, -100, 0)
        self.assertAlmostEqual(result, 0.75)

    def test_normalize_player_stats_standard(self):
        """Test normalize_player_stats with a full set of numeric values and valid ranges."""
        player_stats = {
            'shots': 20,
            'goals': 5,
            'minutes_played': 900
        }
        stat_ranges = {
            'shots': (0, 40),
            'goals': (0, 10),
            'minutes_played': (0, 1800)
        }
        result = normalize_player_stats(player_stats, stat_ranges)
        self.assertIn('shots', result)
        self.assertIn('goals', result)
        self.assertIn('minutes_played', result)

        self.assertAlmostEqual(result['shots'], 0.5)
        self.assertAlmostEqual(result['goals'], 0.5)
        self.assertEqual(result['minutes_played'], 900)

    def test_normalize_player_stats_missing_range(self):
        """Test normalize_player_stats where a stat has no corresponding range."""
        player_stats = {
            'assists': 7,
            'minutes_played': 700
        }
        stat_ranges = {
            'minutes_played': (0, 1000)
        }
        result = normalize_player_stats(player_stats, stat_ranges)
        self.assertEqual(result['assists'], 7)  # should be preserved unnormalized
        self.assertEqual(result['minutes_played'], 700)

    def test_normalize_player_stats_non_numeric_filtered(self):
        """Test that non-numeric fields are removed from normalization."""
        player_stats = {
            'player_name': 'Jane Doe',
            'team_id': 'abc123',
            'goals': 3,
            'minutes_played': 300
        }
        stat_ranges = {
            'goals': (0, 10),
            'minutes_played': (0, 1000)
        }
        result = normalize_player_stats(player_stats, stat_ranges)
        self.assertIn('goals', result)
        self.assertIn('minutes_played', result)
        self.assertNotIn('player_name', result)
        self.assertNotIn('team_id', result)
        self.assertAlmostEqual(result['goals'], 0.3)
        self.assertEqual(result['minutes_played'], 300)

    def test_normalize_player_stats_zero_range(self):
        """Test that stats with identical min/max in stat_ranges return 0."""
        player_stats = {'xg': 1.5}
        stat_ranges = {'xg': (1.5, 1.5)}
        result = normalize_player_stats(player_stats, stat_ranges)
        self.assertEqual(result['xg'], 0)

    def test_normalize_player_stats_empty_inputs(self):
        """Test normalize_player_stats with empty dicts."""
        result = normalize_player_stats({}, {})
        self.assertEqual(result, {})

        player_stats = {'goals': 2}
        result = normalize_player_stats(player_stats, {})
        self.assertEqual(result['goals'], 2)

        result = normalize_player_stats({}, {'goals': (0, 10)})
        self.assertEqual(result, {})