import unittest
from bs4 import BeautifulSoup
from scrape import _scrape_dynamic_player_content, scrape_nwsl_players

class TestFetchAndParse(unittest.TestCase):
    def test_player_content_scrape(self):
        player_data = scrape_nwsl_players('Regular Season 2024')
        self.assertGreater(len(player_data), 10)
    
    def test_player_content_scrape_no_season(self):
        player_data = scrape_nwsl_players('')
        self.assertEqual(player_data, 0)
    
    def test_player_content_scrape_none_season(self):
        player_data = scrape_nwsl_players(None)
        self.assertEqual(player_data, 0)
    
    def test_player_content_scrape_incorrect_season(self):
        player_data = scrape_nwsl_players('Regular Season 1999')
        self.assertEqual(player_data, 0)

if __name__ == '__main__':
    unittest.main()