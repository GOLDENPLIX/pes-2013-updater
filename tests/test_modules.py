import os
import sys
import unittest
import pandas as pd
from unittest.mock import patch, MagicMock

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# Use relative imports
from Automate_File_Backups import backup_files
from web_scraping_to_get_transfer_updates import fetch_transfer_data
from config import Config

class TestPESUpdateBot(unittest.TestCase):
    def setUp(self):
        # Create temporary test directories
        self.test_source = os.path.join(os.path.dirname(__file__), 'test_source')
        self.test_backup = os.path.join(os.path.dirname(__file__), 'test_backup')
        os.makedirs(self.test_source, exist_ok=True)
        os.makedirs(self.test_backup, exist_ok=True)
        
        # Create a dummy file in source
        with open(os.path.join(self.test_source, 'test_file.txt'), 'w') as f:
            f.write('Test content')

    def tearDown(self):
        # Clean up test directories
        import shutil
        shutil.rmtree(self.test_source, ignore_errors=True)
        shutil.rmtree(self.test_backup, ignore_errors=True)

    def test_backup_files(self):
        """Test backup_files function."""
        result = backup_files(self.test_source, self.test_backup)
        self.assertTrue(result)
        self.assertTrue(os.path.exists(os.path.join(self.test_backup, 'test_file.txt')))

    @patch('web_scraping_to_get_transfer_updates.requests.get')
    def test_fetch_transfer_data(self, mock_get):
        """Test fetch_transfer_data with mocked API response."""
        # Create a mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'transfers': [
                {'player': 'John Doe', 'from_team': 'Team A', 'to_team': 'Team B'},
                {'player': 'Jane Smith', 'from_team': 'Team C', 'to_team': 'Team D'}
            ]
        }
        mock_get.return_value = mock_response

        # Temporarily set a test API key
        with patch.object(Config, 'get_api_key', return_value='test_key'):
            transfers = fetch_transfer_data()
        
        self.assertIsNotNone(transfers)
        self.assertFalse(transfers.empty)
        self.assertEqual(len(transfers), 2)

    def test_config_loading(self):
        """Test configuration loading."""
        # Check that configuration methods work
        api_key = Config.get_api_key()
        file_paths = Config.get_file_paths()
        
        self.assertIsNotNone(api_key)
        self.assertIsNotNone(file_paths)
        self.assertTrue(isinstance(file_paths, dict))

if __name__ == '__main__':
    unittest.main()
