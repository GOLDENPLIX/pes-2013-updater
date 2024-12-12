import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pes_updater import PESUpdater
from transfer_manager import TransferManager
from database_manager import PESDatabaseManager
from pes_asset_scraper import PESAssetScraper

class TestPESUpdaterIntegration(unittest.TestCase):
    def setUp(self):
        """
        Setup integration test environment
        """
        # Create temporary test directories
        self.test_base_dir = os.path.join(os.path.dirname(__file__), 'test_data')
        os.makedirs(self.test_base_dir, exist_ok=True)
        
        # Configure test paths
        os.environ['PES_DB_PATH'] = os.path.join(self.test_base_dir, 'pes_database.csv')
        os.environ['TRANSFER_DATA_DIR'] = os.path.join(self.test_base_dir, 'transfers')
        os.environ['BACKUP_DIR'] = os.path.join(self.test_base_dir, 'backup')
        
        # Ensure directories exist
        os.makedirs(os.environ['TRANSFER_DATA_DIR'], exist_ok=True)
        os.makedirs(os.environ['BACKUP_DIR'], exist_ok=True)
        
        # Initialize components
        self.updater = PESUpdater()
    
    def tearDown(self):
        """
        Clean up test environment
        """
        import shutil
        shutil.rmtree(self.test_base_dir, ignore_errors=True)
    
    def test_complete_update_flow(self):
        """
        Test the entire update process from transfers to database update
        """
        # Mock external dependencies to control test environment
        with (
            patch.object(TransferManager, 'fetch_transfers', 
                return_value=[{
                    'player_name': 'Test Player',
                    'from_team': 'Old Team',
                    'to_team': 'New Team',
                    'transfer_date': '2024-01-01',
                    'transfer_fee': 5000000
                }]) as mock_fetch,
            patch.object(PESAssetScraper, 'download_multiple_teams', 
                return_value={
                    'New Team': {'logo': True, 'kit': True}
                }) as mock_download_assets
        ):
            # Run update process
            self.updater.run(
                update_transfers=True, 
                download_assets=True, 
                update_database=True
            )
            
            # Verify method calls
            mock_fetch.assert_called_once()
            mock_download_assets.assert_called_once()
    
    def test_error_handling_in_update_flow(self):
        """
        Test error handling during the update process
        """
        # Simulate various failure scenarios
        with (
            patch.object(TransferManager, 'fetch_transfers', 
                side_effect=Exception("Transfer fetch failed")) as mock_fetch,
            patch.object(PESAssetScraper, 'download_multiple_teams', 
                side_effect=Exception("Asset download failed")) as mock_download_assets,
            patch.object(PESDatabaseManager, 'update_database', 
                side_effect=Exception("Database update failed")) as mock_db_update
        ):
            # Run update process and verify it doesn't raise unhandled exceptions
            try:
                self.updater.run(
                    update_transfers=True, 
                    download_assets=True, 
                    update_database=True
                )
            except Exception as e:
                self.fail(f"Unhandled exception in update flow: {e}")
            
            # Verify method calls
            mock_fetch.assert_called_once()
            mock_download_assets.assert_called_once()
            mock_db_update.assert_not_called()  # Should not update DB if transfers fail
    
    def test_partial_update_scenarios(self):
        """
        Test different partial update scenarios
        """
        test_scenarios = [
            {'transfers': True, 'assets': False, 'database': False},
            {'transfers': False, 'assets': True, 'database': False},
            {'transfers': False, 'assets': False, 'database': True}
        ]
        
        for scenario in test_scenarios:
            with self.subTest(scenario=scenario):
                try:
                    self.updater.run(**scenario)
                except Exception as e:
                    self.fail(f"Failed in scenario {scenario}: {e}")
    
    def test_configuration_flexibility(self):
        """
        Test updater's ability to handle different configuration scenarios
        """
        # Test with different log levels
        log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR']
        
        for level in log_levels:
            with self.subTest(log_level=level):
                updater = PESUpdater(log_level=level)
                
                try:
                    updater.run()
                except Exception as e:
                    self.fail(f"Failed with log level {level}: {e}")

if __name__ == '__main__':
    unittest.main()
