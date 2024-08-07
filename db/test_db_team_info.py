import unittest
from .db_team_info import *
from .db_setup import create_tables

class TestTeamInfoDB(unittest.TestCase):
    # Test Setup
    create_tables()
    insert_team_info()

    def test_all_team_info_insert(self):
        teams_info_data = get_all_teams_info()
        self.assertGreater(len(teams_info_data), 10)
    
    def test_get_team_by_id(self):
        team_id = '315VnJ759x'
        data = get_team_info_by_id(team_id)
        self.assertEqual(data['team_name'], 'Bay FC')
        self.assertEqual(data['team_short_name'], 'Bay FC')
        self.assertEqual(data['team_abbreviation'], 'BAY')
