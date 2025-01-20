import unittest
from unittest.mock import patch
from .db_player_xgoals import fetch_players_xgoal_data, calculate_shots_on_target_percentage, aggregate_position_data

class TestFetchPlayersXGoalData(unittest.TestCase):

    @patch('data.db_player_xgoals.make_asa_api_call')
    def test_fetch_with_default_excluded_positions(self, mock_make_asa_api_call):
        # Mock API response
        mock_make_asa_api_call.return_value = (None, [
            {'player_id': 1, 'general_position': 'GK'},
            {'player_id': 2, 'general_position': 'ST'},
            {'player_id': 3, 'general_position': 'CM'}
        ])

        # Call function
        season = 2023
        result = fetch_players_xgoal_data(season)

        # Assert default excluded position (empty string) does not exclude any players
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]['general_position'], 'GK')

    @patch('data.db_player_xgoals.make_asa_api_call')
    def test_fetch_with_valid_excluded_positions(self, mock_make_asa_api_call):
        # Mock API response
        mock_make_asa_api_call.return_value = (None, [
            {'player_id': 1, 'general_position': 'GK'},
            {'player_id': 2, 'general_position': 'ST'},
            {'player_id': 3, 'general_position': 'CM'}
        ])

        # Call function with excluded positions
        season = 2023
        excluded_positions = ['GK', 'CM']
        result = fetch_players_xgoal_data(season, excluded_positions)

        # Assert excluded positions are filtered out
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['general_position'], 'ST')

    @patch('data.db_player_xgoals.make_asa_api_call')
    def test_fetch_with_empty_response(self, mock_make_asa_api_call):
        # Mock API response as empty
        mock_make_asa_api_call.return_value = (None, [])

        # Call function
        season = 2023
        result = fetch_players_xgoal_data(season)

        # Assert result is empty
        self.assertEqual(result, [])

    @patch('data.db_player_xgoals.make_asa_api_call')
    def test_fetch_with_no_matching_positions(self, mock_make_asa_api_call):
        # Mock API response
        mock_make_asa_api_call.return_value = (None, [
            {'player_id': 1, 'general_position': 'GK'},
            {'player_id': 2, 'general_position': 'ST'}
        ])

        # Call function with excluded positions that don't match any player
        season = 2023
        excluded_positions = ['CB']
        result = fetch_players_xgoal_data(season, excluded_positions)

        # Assert all players are returned since no positions match excluded_positions
        self.assertEqual(len(result), 2)

    @patch('data.db_player_xgoals.make_asa_api_call')
    def test_fetch_with_all_positions_excluded(self, mock_make_asa_api_call):
        # Mock API response
        mock_make_asa_api_call.return_value = (None, [
            {'player_id': 1, 'general_position': 'GK'},
            {'player_id': 2, 'general_position': 'ST'}
        ])

        # Call function with all positions excluded
        season = 2023
        excluded_positions = ['GK', 'ST']
        result = fetch_players_xgoal_data(season, excluded_positions)

        # Assert result is empty since all positions are excluded
        self.assertEqual(result, [])

class TestCalculateShotsOnTargetPercentage(unittest.TestCase):
    def test_calculate_with_valid_data(self):
        players_data = [
            {'player_id': 1, 'shots': 10, 'shots_on_target': 5, 'minutes_played': 200},
            {'player_id': 2, 'shots': 8, 'shots_on_target': 4, 'minutes_played': 150},
            {'player_id': 3, 'shots': 0, 'shots_on_target': 0, 'minutes_played': 250},
        ]
        result = calculate_shots_on_target_percentage(players_data)

        # Assert calculations
        self.assertEqual(len(result), 2)  # Only players with >= 180 minutes should remain
        self.assertEqual(result[0]['shots_on_target_perc'], 50.0)  # 5/10 * 100
        self.assertEqual(result[1]['shots_on_target_perc'], 0)  # 0 shots

    def test_calculate_with_default_minimum_minutes(self):
        players_data = [
            {'player_id': 1, 'shots': 10, 'shots_on_target': 5, 'minutes_played': 180},
            {'player_id': 2, 'shots': 8, 'shots_on_target': 4, 'minutes_played': 179},
        ]
        result = calculate_shots_on_target_percentage(players_data)

        # Assert only players meeting the default minimum minutes remain
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['player_id'], 1)

    def test_calculate_with_custom_minimum_minutes(self):
        players_data = [
            {'player_id': 1, 'shots': 10, 'shots_on_target': 5, 'minutes_played': 180},
            {'player_id': 2, 'shots': 8, 'shots_on_target': 4, 'minutes_played': 179},
        ]
        result = calculate_shots_on_target_percentage(players_data, minimum_minutes=179)

        # Assert players meeting the custom minimum minutes remain
        self.assertEqual(len(result), 2)

    def test_calculate_with_no_shots(self):
        players_data = [
            {'player_id': 1, 'shots': 0, 'shots_on_target': 0, 'minutes_played': 200},
            {'player_id': 2, 'shots': 0, 'shots_on_target': 0, 'minutes_played': 250},
        ]
        result = calculate_shots_on_target_percentage(players_data)

        # Assert shots_on_target_perc is 0 for players with 0 shots
        self.assertEqual(len(result), 2)
        for player in result:
            self.assertEqual(player['shots_on_target_perc'], 0)

    def test_calculate_with_empty_data(self):
        players_data = []
        result = calculate_shots_on_target_percentage(players_data)

        # Assert result is empty
        self.assertEqual(result, [])

    def test_calculate_with_missing_keys(self):
        players_data = [
            {'player_id': 1, 'minutes_played': 200},  # Missing shots and shots_on_target
            {'player_id': 2, 'shots': 10, 'shots_on_target': 5},  # Missing minutes_played
        ]
        result = calculate_shots_on_target_percentage(players_data)

        # Assert calculations for available data
        self.assertEqual(len(result), 1)  # Only the first player meets the minimum minutes
        self.assertEqual(result[0]['shots_on_target_perc'], 0)  # shots_on_target_perc is 0 by default

class TestAggregatePositionData(unittest.TestCase):

    def test_aggregate_with_valid_data(self):
        filtered_players = [
            {'player_id': 1, 'general_position': 'ST', 'goals': 5, 'assists': 3},
            {'player_id': 2, 'general_position': 'ST', 'goals': 10, 'assists': 4},
            {'player_id': 3, 'general_position': 'CM', 'goals': 3, 'assists': 2},
        ]
        stats_to_track = ['goals', 'assists']
        result = aggregate_position_data(filtered_players, stats_to_track)

        expected = {
            'ST': {
                'avg_goals': 7.5,
                'min_goals': 5,
                'max_goals': 10,
                'avg_assists': 3.5,
                'min_assists': 3,
                'max_assists': 4,
            },
            'CM': {
                'avg_goals': 3.0,
                'min_goals': 3,
                'max_goals': 3,
                'avg_assists': 2.0,
                'min_assists': 2,
                'max_assists': 2,
            }
        }
        self.assertEqual(result, expected)

    def test_aggregate_with_missing_stats(self):
        filtered_players = [
            {'player_id': 1, 'general_position': 'ST', 'goals': 5},  # Missing 'assists'
            {'player_id': 2, 'general_position': 'ST', 'goals': 10, 'assists': 4},
        ]
        stats_to_track = ['goals', 'assists']
        result = aggregate_position_data(filtered_players, stats_to_track)

        expected = {
            'ST': {
                'avg_goals': 7.5,
                'min_goals': 5,
                'max_goals': 10,
                'avg_assists': 2.0,
                'min_assists': 0,  # Missing stats default to 0
                'max_assists': 4,
            }
        }
        self.assertEqual(result, expected)

    def test_aggregate_with_no_players(self):
        filtered_players = []
        stats_to_track = ['goals', 'assists']
        result = aggregate_position_data(filtered_players, stats_to_track)

        expected = {}
        self.assertEqual(result, expected)

    def test_aggregate_with_unknown_positions(self):
        filtered_players = [
            {'player_id': 1, 'general_position': 'Unknown Position', 'goals': 7, 'assists': 2},
            {'player_id': 2, 'general_position': 'Unknown Position', 'goals': 3, 'assists': 1},
        ]
        stats_to_track = ['goals', 'assists']
        result = aggregate_position_data(filtered_players, stats_to_track)

        expected = {
            'Unknown Position': {
                'avg_goals': 5.0,
                'min_goals': 3,
                'max_goals': 7,
                'avg_assists': 1.5,
                'min_assists': 1,
                'max_assists': 2,
            }
        }
        self.assertEqual(result, expected)

    def test_aggregate_with_non_numeric_stats(self):
        filtered_players = [
            {'player_id': 1, 'general_position': 'ST', 'goals': 'not_a_number', 'assists': 3},
            {'player_id': 2, 'general_position': 'ST', 'goals': 10, 'assists': 4},
        ]
        stats_to_track = ['goals', 'assists']

        # Verify that invalid data raises an exception
        with self.assertRaises(TypeError):
            aggregate_position_data(filtered_players, stats_to_track)

if __name__ == '__main__':
    unittest.main()