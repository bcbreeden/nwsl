import unittest
from data import  data_util

class TestAggregatePositionData(unittest.TestCase):
    
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
        
if __name__ == '__main__':
    unittest.main()