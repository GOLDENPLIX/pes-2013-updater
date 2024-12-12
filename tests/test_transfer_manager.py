import os
import unittest
from unittest.mock import patch, MagicMock
import sys

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from transfer_manager import TransferManager

class TestTransferManager(unittest.TestCase):
    def setUp(self):
        """
        Setup test environment for TransferManager
        """
        self.transfer_manager = TransferManager()
    
    @patch('transfer_manager.requests.get')
    def test_fetch_transfers_success(self, mock_get):
        """
        Test successful transfer fetching
        """
        # Mock API response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'transfers': [
                {
                    'player': {'name': 'John Doe', 'id': 123},
                    'transferFrom': {'name': 'Team A'},
                    'transferTo': {'name': 'Team B'},
                    'date': '2024-01-01',
                    'fee': {'value': 10000000}
                }
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Fetch transfers
        transfers = self.transfer_manager.fetch_transfers()
        
        # Assertions
        self.assertIsNotNone(transfers)
        self.assertEqual(len(transfers), 1)
        self.assertEqual(transfers[0]['player_name'], 'John Doe')
        self.assertEqual(transfers[0]['from_team'], 'Team A')
        self.assertEqual(transfers[0]['to_team'], 'Team B')
    
    @patch('transfer_manager.requests.get')
    def test_fetch_transfers_api_error(self, mock_get):
        """
        Test handling of API errors during transfer fetch
        """
        # Simulate API error
        mock_get.side_effect = Exception("API Error")
        
        # Fetch transfers
        transfers = self.transfer_manager.fetch_transfers()
        
        # Assertions
        self.assertEqual(len(transfers), 0)
    
    def test_save_transfers(self):
        """
        Test saving transfers to CSV
        """
        # Sample transfer data
        transfers = [
            {
                'league': 'PL',
                'player_name': 'John Doe',
                'player_id': 123,
                'from_team': 'Team A',
                'to_team': 'Team B',
                'transfer_date': '2024-01-01',
                'transfer_fee': 10000000
            }
        ]
        
        # Save transfers
        save_path = self.transfer_manager.save_transfers(transfers)
        
        # Assertions
        self.assertTrue(os.path.exists(save_path))
        self.assertTrue(save_path.endswith('.csv'))
        
        # Optional: Verify CSV contents
        with open(save_path, 'r') as f:
            lines = f.readlines()
            self.assertTrue(len(lines) > 1)  # Header + data
            self.assertIn('John Doe', lines[1])
    
    def test_update_transfers_full_process(self):
        """
        Test the complete transfer update process
        """
        with patch.object(self.transfer_manager, 'fetch_transfers', 
                          return_value=[{
                              'player_name': 'Test Player',
                              'from_team': 'Old Team',
                              'to_team': 'New Team',
                              'transfer_date': '2024-01-01',
                              'transfer_fee': 5000000
                          }]) as mock_fetch:
            
            result = self.transfer_manager.update_transfers()
            
            # Assertions
            self.assertTrue(result)
            mock_fetch.assert_called_once()

if __name__ == '__main__':
    unittest.main()
