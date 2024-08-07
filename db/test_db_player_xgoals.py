import unittest
from .db_player_xgoals import *
from .db_setup import create_tables

class TestPlayerXGoalsDB(unittest.TestCase):
    # Test Setup
    create_tables()
    insert_player_xgoals_by_season('2024')

    def test_insert_player_xgoals_by_season(self):
        pass

if __name__ == '__main__':
    unittest.main()