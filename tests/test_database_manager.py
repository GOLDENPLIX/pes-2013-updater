import os
import csv
import unittest
import sys
import tempfile
import shutil

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database_manager import PESDatabaseManager

class TestPESDatabaseManager(unittest.TestCase):
    def setUp(self):
        """
        Setup test environment for DatabaseManager
        """
        # Create a temporary directory for test files
        self.test_dir = tempfile.mkdtemp()
        
        # Create sample database and transfers files
        self.database_path = os.path.join(self.test_dir, 'pes_database.csv')
        self.transfers_path = os.path.join(self.test_dir, 'transfers.csv')
        
        # Create sample database
        with open(self.database_path, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=[
                'name', 'team', 'age', 'position'
            ])
            writer.writeheader()
            writer.writerows([
                {'name': 'John Doe', 'team': 'Old Team', 'age': '25', 'position': 'Forward'},
                {'name': 'Jane Smith', 'team': 'Another Team', 'age': '28', 'position': 'Midfielder'}
            ])
        
        # Create sample transfers
        with open(self.transfers_path, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=[
                'player_name', 'from_team', 'to_team', 'transfer_date', 'transfer_fee'
            ])
            writer.writeheader()
            writer.writerows([
                {
                    'player_name': 'John Doe', 
                    'from_team': 'Old Team', 
                    'to_team': 'New Team', 
                    'transfer_date': '2024-01-01', 
                    'transfer_fee': '10000000'
                }
            ])
        
        # Initialize DatabaseManager with test paths
        self.db_manager = PESDatabaseManager()
        
        # Override config paths for testing
        self.db_manager.config['PES_DB_PATH'] = self.database_path
        self.db_manager.config['BACKUP_DIR'] = self.test_dir
    
    def tearDown(self):
        """
        Clean up temporary test files
        """
        shutil.rmtree(self.test_dir)
    
    def test_backup_database(self):
        """
        Test database backup functionality
        """
        backup_path = self.db_manager.backup_database(self.database_path)
        
        # Assertions
        self.assertTrue(os.path.exists(backup_path))
        self.assertTrue('pes_database_backup' in os.path.basename(backup_path))
        self.assertTrue(backup_path.endswith('.csv'))
    
    def test_update_database(self):
        """
        Test database update with transfers
        """
        # Update database
        update_result = self.db_manager.update_database(self.transfers_path)
        
        # Assertions
        self.assertTrue(update_result)
        
        # Verify database contents
        with open(self.database_path, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            updated_players = list(reader)
        
        # Check if John Doe's team has been updated
        john_doe = next((p for p in updated_players if p['name'] == 'John Doe'), None)
        self.assertIsNotNone(john_doe)
        self.assertEqual(john_doe['team'], 'New Team')
    
    def test_update_database_no_transfers(self):
        """
        Test database update with no transfers
        """
        # Create an empty transfers file
        empty_transfers_path = os.path.join(self.test_dir, 'empty_transfers.csv')
        with open(empty_transfers_path, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=[
                'player_name', 'from_team', 'to_team', 'transfer_date', 'transfer_fee'
            ])
            writer.writeheader()
        
        # Update database
        update_result = self.db_manager.update_database(empty_transfers_path)
        
        # Assertions
        self.assertFalse(update_result)
    
    def test_apply_transfers(self):
        """
        Test the internal transfer application logic
        """
        # Existing database
        database = [
            {'name': 'John Doe', 'team': 'Old Team', 'age': '25', 'position': 'Forward'},
            {'name': 'Jane Smith', 'team': 'Another Team', 'age': '28', 'position': 'Midfielder'}
        ]
        
        # Transfers
        transfers = [
            {
                'player_name': 'John Doe', 
                'from_team': 'Old Team', 
                'to_team': 'New Team', 
                'transfer_date': '2024-01-01', 
                'transfer_fee': '10000000'
            }
        ]
        
        # Call protected method directly
        updated_database = self.db_manager._apply_transfers(database, transfers)
        
        # Assertions
        john_doe = next((p for p in updated_database if p['name'] == 'John Doe'), None)
        self.assertIsNotNone(john_doe)
        self.assertEqual(john_doe['team'], 'New Team')

if __name__ == '__main__':
    unittest.main()
