import os
import csv
import logging
import shutil
from datetime import datetime
from typing import List, Dict, Optional

class PESDatabaseManager:
    def __init__(self, config_path: str = '.env'):
        """
        Initialize PES Database Manager
        
        :param config_path: Path to configuration file
        """
        self.logger = logging.getLogger(__name__)
        self.config = self._load_config(config_path)
        
        # Ensure data directories exist
        os.makedirs(self.config.get('PES_DB_DIR', 'data/pes_database'), exist_ok=True)
        os.makedirs(self.config.get('BACKUP_DIR', 'data/backup'), exist_ok=True)
    
    def _load_config(self, config_path: str) -> Dict:
        """
        Load configuration from .env file
        
        :param config_path: Path to .env file
        :return: Dictionary of configuration settings
        """
        from dotenv import dotenv_values
        return dotenv_values(config_path)
    
    def backup_database(self, database_path: Optional[str] = None) -> str:
        """
        Create a backup of the PES database
        
        :param database_path: Optional path to database file
        :return: Path to backup file
        """
        if not database_path:
            database_path = self.config.get('PES_DB_PATH', 'data/pes_database/players.csv')
        
        if not os.path.exists(database_path):
            self.logger.warning(f"Database file not found: {database_path}")
            return ''
        
        backup_dir = self.config.get('BACKUP_DIR', 'data/backup')
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"pes_database_backup_{timestamp}.csv"
        backup_path = os.path.join(backup_dir, backup_filename)
        
        try:
            shutil.copy2(database_path, backup_path)
            self.logger.info(f"Database backup created: {backup_path}")
            return backup_path
        except Exception as e:
            self.logger.error(f"Backup creation failed: {e}")
            return ''
    
    def update_database(self, transfers_path: Optional[str] = None) -> bool:
        """
        Update PES database with latest transfers
        
        :param transfers_path: Path to transfers CSV file
        :return: Boolean indicating update success
        """
        if not transfers_path:
            transfers_path = self._find_latest_transfers()
        
        if not transfers_path or not os.path.exists(transfers_path):
            self.logger.warning("No transfer data found for database update")
            return False
        
        pes_db_path = self.config.get('PES_DB_PATH', 'data/pes_database/players.csv')
        
        try:
            # Backup current database
            self.backup_database(pes_db_path)
            
            # Read existing database
            database = self._read_database(pes_db_path)
            
            # Read transfers
            transfers = self._read_transfers(transfers_path)
            
            # Update database with transfers
            updated_database = self._apply_transfers(database, transfers)
            
            # Save updated database
            self._save_database(updated_database, pes_db_path)
            
            self.logger.info(f"Database updated with {len(transfers)} transfers")
            return True
        
        except Exception as e:
            self.logger.error(f"Database update failed: {e}")
            return False
    
    def _find_latest_transfers(self) -> Optional[str]:
        """
        Find the most recent transfers file
        
        :return: Path to latest transfers file
        """
        transfers_dir = self.config.get('TRANSFER_DATA_DIR', 'data/transfers')
        
        try:
            transfers_files = [
                os.path.join(transfers_dir, f) 
                for f in os.listdir(transfers_dir) 
                if f.startswith('transfers_') and f.endswith('.csv')
            ]
            
            if not transfers_files:
                return None
            
            # Return the most recently created file
            return max(transfers_files, key=os.path.getctime)
        
        except Exception as e:
            self.logger.error(f"Error finding latest transfers: {e}")
            return None
    
    def _read_database(self, database_path: str) -> List[Dict]:
        """
        Read PES database from CSV
        
        :param database_path: Path to database CSV
        :return: List of player dictionaries
        """
        with open(database_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            return list(reader)
    
    def _read_transfers(self, transfers_path: str) -> List[Dict]:
        """
        Read transfers from CSV
        
        :param transfers_path: Path to transfers CSV
        :return: List of transfer dictionaries
        """
        with open(transfers_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            return list(reader)
    
    def _apply_transfers(self, database: List[Dict], transfers: List[Dict]) -> List[Dict]:
        """
        Apply transfers to the database
        
        :param database: Current PES database
        :param transfers: Transfer data
        :return: Updated database
        """
        # Create a mapping for quick lookups
        database_map = {
            (player.get('name'), player.get('team')): player 
            for player in database
        }
        
        # Apply transfers
        for transfer in transfers:
            player_key = (transfer['player_name'], transfer['from_team'])
            
            if player_key in database_map:
                player = database_map[player_key]
                player['team'] = transfer['to_team']
                player['transfer_date'] = transfer['transfer_date']
                player['transfer_fee'] = transfer['transfer_fee']
        
        return list(database_map.values())
    
    def _save_database(self, database: List[Dict], database_path: str):
        """
        Save updated database to CSV
        
        :param database: Updated database
        :param database_path: Path to save database
        """
        with open(database_path, 'w', newline='', encoding='utf-8') as csvfile:
            if not database:
                return
            
            fieldnames = database[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            writer.writerows(database)

def main():
    """
    Example usage of PESDatabaseManager
    """
    logging.basicConfig(level=logging.INFO)
    db_manager = PESDatabaseManager()
    db_manager.update_database()

if __name__ == "__main__":
    main()
