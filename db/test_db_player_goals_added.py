import unittest
from .db_player_goals_added import *
from .db_setup import create_tables

class TestPlayerGoalsAddedDB(unittest.TestCase):
    # Test Setup
    create_tables()
    insert_player_goals_added_by_season('2024')

    def test_get_player_goals_added_by_season(self):
        player_data = get_player_goals_added_by_season('0Oq6243Pq6', 2024)
        self.assertTrue(len(player_data) > 1, 'The query should return more than 1 row.')

if __name__ == '__main__':
    unittest.main()