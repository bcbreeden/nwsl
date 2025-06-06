import unittest
from data import db_manager_info

EXPECTED_MANAGER_FIELDS = ['manager_id', 'manager_name', 'nationality']

class TestManagerInfo(unittest.TestCase):

    def setUp(self):
        self.valid_id = '315Vx06Q9x'

    def test_get_manager_by_id_valid(self):
        row = db_manager_info.get_manager_by_id(self.valid_id)

        # Ensure the row is returned and accessible
        self.assertIsNotNone(row)
        for field in EXPECTED_MANAGER_FIELDS:
            self.assertIn(field, row.keys())
        self.assertEqual(row['manager_id'], self.valid_id)
        self.assertIsInstance(row['manager_name'], str)
        self.assertIsInstance(row['nationality'], str)

    def test_get_manager_by_id_invalid(self):
        row = db_manager_info.get_manager_by_id('nonexistent_id_123')
        self.assertIsNone(row)

if __name__ == '__main__':
    unittest.main()
