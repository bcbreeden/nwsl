import unittest
from bs4 import BeautifulSoup
from scrape import _scrape_dynamic_content

class TestFetchAndParse(unittest.TestCase):

    def test_fetch_and_parse(self):
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

if __name__ == '__main__':
    unittest.main()