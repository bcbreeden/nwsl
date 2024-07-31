import unittest
from db_player import *
from db_setup import create_tables

class TestPlayerInfoDB(unittest.TestCase):
    def test_all_player_info_insert(self):
        create_tables()
        insert_all_players_info()
        players_info_data = get_all_players_info()
        self.assertGreater(len(players_info_data), 25)

if __name__ == '__main__':
    unittest.main()