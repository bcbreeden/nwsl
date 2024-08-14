import unittest
from .db_goalkeeper_xgoals import *
from .db_setup import create_tables

class TestGoalkeeperXGoalsDB(unittest.TestCase):
    # Test Setup
    create_tables()
    insert_goalkeeper_xgoals_by_season('2024')

    def test_get_all_goalkeeper_xgoal_data_by_season(self):
        players_data = get_all_goalkeepers_xgoals_by_season(2024)
        self.assertTrue(len(players_data) > 1, 'The query should return more than 1 row.')
    
    def test_get_goalkeeper_xgoal_data_by_season(self):
        player_data = get_goalkeeper_xgoals_by_season('0x5gJ0LXM7', 2024)
        self.assertTrue(len(player_data) > 1, 'The query should return more than 1 row.')

if __name__ == '__main__':
    unittest.main()