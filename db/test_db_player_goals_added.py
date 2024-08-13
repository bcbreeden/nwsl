import unittest
from .db_player_goals_added import *
from .db_setup import create_tables

class TestPlayerGoalsAddedDB(unittest.TestCase):
    # Test Setup
    create_tables()
    insert_player_goals_added_by_season('2024')

    def test_get_player_xgoals_by_season(self):
        pass

if __name__ == '__main__':
    unittest.main()