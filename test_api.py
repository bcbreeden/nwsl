import unittest
from api import *

class TestAPI(unittest.TestCase):
    def test_api_no_endpoint(self):
        response = make_api_call('')
        self.assertNotEqual(response[0], 200)
    
    def test_api_none_endpoint(self):
        response = make_api_call(None)
        self.assertNotEqual(response[0], 200)
    
    def test_api_valid_endpoint(self):
        response = make_api_call('nwsl/players')
        self.assertEqual(response[0], 200)
        self.assertGreater(len(response[1]), 25)

if __name__ == '__main__':
    unittest.main()