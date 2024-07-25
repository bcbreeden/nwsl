import unittest
from bs4 import BeautifulSoup
from scrape import _scrape_dynamic_content, scrape_nwsl_players

class TestFetchAndParse(unittest.TestCase):

    def test_valid_fetch_and_parse(self):
        url = "https://www.nwslsoccer.com"
        soup = _scrape_dynamic_content(url)
        # Check if the result is a BeautifulSoup object
        self.assertIsInstance(soup, BeautifulSoup)
        # Check if the soup contains expected elements
        self.assertIsNotNone(soup.find('html'))
        self.assertIsNotNone(soup.find('ul'))
        self.assertIsNotNone(soup.find('li'))
    
    def test_invalid_url(self):
        url = "https://thisisnotavalidsite.org"
        soup = _scrape_dynamic_content(url)
        # Will return a 0 if a url is invalid.
        self.assertEqual(soup, 0)

    def test_no_url(self):
        url = ""
        soup = _scrape_dynamic_content(url)
        # Will return a 0 if a url is invalid.
        self.assertEqual(soup, 0)
    
    def test_none_url(self):
        url = None
        soup = _scrape_dynamic_content(url)
        # Will return a 0 if a url is invalid.
        self.assertEqual(soup, 0)
    
    def test_player_scrape(self):
        player_data = scrape_nwsl_players()
        self.assertGreater(len(player_data), 10)

if __name__ == '__main__':
    unittest.main()