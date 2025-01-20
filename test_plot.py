import unittest
import json
import plotly
from plots import plot_spider  # Replace 'your_module' with the actual module name

class TestPlotSpider(unittest.TestCase):

    def setUp(self):
        # Simulate sqlite3.Row using a dictionary
        self.player_data = {
            'player_name': 'Test Player',
            'stat1': 15,
            'min_stat1': 10,
            'max_stat1': 20,
            'stat2': 30,
            'min_stat2': 20,
            'max_stat2': 40,
        }

    def test_plot_spider_success(self):
        stats_to_plot = ['stat1', 'stat2']
        fig_json, config_json = plot_spider(stats_to_plot, self.player_data)

        # Validate JSON structure of Plotly figure
        fig = json.loads(fig_json)
        self.assertIn('data', fig)
        self.assertIn('layout', fig)

        # Validate config JSON
        config = json.loads(config_json)
        self.assertIn('displayModeBar', config)
        self.assertFalse(config['displayModeBar'])

        # Check that the categories and data are correctly normalized
        data = fig['data'][0]
        self.assertEqual(data['r'][-1], data['r'][0])  # Closed loop
        self.assertEqual(data['theta'][-1], data['theta'][0])  # Closed loop

    def test_plot_spider_invalid_stat(self):
        stats_to_plot = ['stat1', 'invalid_stat']
        fig_json, config_json = plot_spider(stats_to_plot, self.player_data)

        # Validate that only valid stats are included
        fig = json.loads(fig_json)
        data = fig['data'][0]
        self.assertEqual(len(data['theta']), 2)  # Only one valid stat and loop closure
        self.assertIn('Stat1', data['theta'])

    def test_plot_spider_empty_stats(self):
        stats_to_plot = []
        fig_json, config_json = plot_spider(stats_to_plot, self.player_data)

        self.assertEqual(fig_json, 0)
        self.assertEqual(config_json, 0)

    def test_plot_spider_equal_min_max(self):
        # Update the data to simulate equal min and max
        self.player_data['max_stat1'] = 10  # Now min_stat1 == max_stat1
        stats_to_plot = ['stat1']

        # Call the function
        fig_json, config_json = plot_spider(stats_to_plot, self.player_data)

        self.assertEqual(fig_json, 0)
        self.assertEqual(config_json, 0)

if __name__ == '__main__':
    unittest.main()
