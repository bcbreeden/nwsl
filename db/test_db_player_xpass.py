import unittest
from .db_player_xpass import *
from .db_setup import create_tables

class TestPlayerXPassDB(unittest.TestCase):
    # Test Setup
    create_tables()
    insert_player_xpass_by_season('2024')

    def test_get_player_xgoals_by_season(self):
        player_data = get_player_xpass('0Oq6243Pq6', 2024)
        self.assertTrue(len(player_data) > 1, 'The query should return more than 1 row.')
    
    def test_get_all_players_xgoals_by_season(self):
        players_data = get_all_player_xpass(2024)
        self.assertTrue(len(players_data) > 1, 'The query should return more than 1 row.')

if __name__ == '__main__':
    unittest.main()