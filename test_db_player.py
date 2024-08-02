import unittest
from db_player import *
from db_setup import create_tables

class TestPlayerInfoDB(unittest.TestCase):
    # Test Setup
    create_tables()
    insert_all_players_info()

    def test_all_player_info_insert(self):
        players_info_data = get_all_players_info()
        self.assertGreater(len(players_info_data), 25)
    
    def test_get_player_seasons(self):
        id = '0Oq6243Pq6'
        data_row_1 = get_player_seasons(id)[0]
        self.assertEqual(data_row_1[1], id)
        self.assertAlmostEqual(data_row_1[2], 2023)
        

if __name__ == '__main__':
    unittest.main()