import unittest
from db_player_info import *
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
        self.assertEqual(data_row_1['player_id'], id)
        self.assertAlmostEqual(data_row_1['year'], 2023)
    
    def test_get_player_info(self):
        id = '0Oq6243Pq6'
        data = get_player_info_by_id(id)
        self.assertEqual(data['player_name'], 'Lena Silano')
        self.assertEqual(data['birth_date'], '2000-02-28')
        self.assertEqual(data['nationality'], 'USA')
        self.assertEqual(data['primary_broad_position'], 'FW')
        self.assertEqual(data['primary_general_position'], 'ST')
        self.assertEqual(data['secondary_broad_position'], 'MF')
        self.assertEqual(data['secondary_general_position'], 'W')

if __name__ == '__main__':
    unittest.main()