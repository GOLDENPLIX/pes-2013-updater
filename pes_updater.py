import os
import sys
import argparse
import logging
from datetime import datetime

# Import custom modules
from logging_config import setup_logging, log_system_info
from config_manager import ConfigManager
from pes_asset_scraper import PESAssetScraper
from transfer_manager import TransferManager
from database_manager import PESDatabaseManager

class PESUpdater:
    def __init__(self, config_manager=None, log_level=None):
        """
        Initialize PES Updater
        
        :param config_manager: Optional ConfigManager instance
        :param log_level: Optional logging level
        """
        # Setup logging
        self.logger = setup_logging(log_level=log_level)
        
        # Load configuration
        self.config = config_manager or ConfigManager()
        
        # Initialize managers
        self.transfer_manager = TransferManager()
        self.database_manager = PESDatabaseManager()
        
        # Log system information
        log_system_info()
    
    def update_transfers(self):
        """
        Fetch and update player transfers
        
        :return: Path to saved transfers file
        """
        self.logger.info("Starting transfer data update")
        try:
            # Use TransferManager to fetch and save transfers
            transfers_path = self.transfer_manager.update_transfers()
            return transfers_path
        except Exception as e:
            self.logger.error(f"Transfer update failed: {e}")
            return None
    
    def download_assets(self, teams=None):
        """
        Download team assets (logos and kits)
        
        :param teams: Optional list of teams to download assets for
        """
        self.logger.info("Starting asset download process")
        
        try:
            # Use PESAssetScraper for downloading
            scraper = PESAssetScraper()
            
            # If no teams specified, use configured teams
            if not teams:
                teams = self.config.get_download_settings().get('download_teams', [])
            
            # Download assets
            results = scraper.download_multiple_teams(teams)
            
            # Log summary
            successful_teams = sum(1 for result in results.values() if result)
            self.logger.info(f"Asset download complete. {successful_teams}/{len(teams)} teams processed.")
        
        except Exception as e:
            self.logger.error(f"Asset download failed: {e}")
    
    def update_pes_database(self, transfers_path=None):
        """
        Update PES database with latest transfers and assets
        
        :param transfers_path: Optional path to transfers file
        :return: Boolean indicating update success
        """
        self.logger.info("Starting PES database update")
        try:
            # Use DatabaseManager to update database
            update_success = self.database_manager.update_database(transfers_path)
            return update_success
        except Exception as e:
            self.logger.error(f"PES database update failed: {e}")
            return False
    
    def create_backup(self):
        """
        Create a backup of the current PES database
        
        :return: Path to backup file
        """
        self.logger.info("Creating PES database backup")
        try:
            backup_path = self.database_manager.backup_database()
            return backup_path
        except Exception as e:
            self.logger.error(f"Backup creation failed: {e}")
            return None
    
    def run(self, update_transfers=True, download_assets=True, update_database=True):
        """
        Run the complete PES update process
        
        :param update_transfers: Flag to update transfers
        :param download_assets: Flag to download assets
        :param update_database: Flag to update PES database
        """
        self.logger.info("Starting PES 2013 Updater")
        
        try:
            # Create backup before any updates
            backup_path = self.create_backup()
            
            # Transfers update
            transfers_path = None
            if update_transfers:
                transfers_path = self.update_transfers()
            
            # Asset download
            if download_assets:
                self.download_assets()
            
            # Database update
            if update_database and transfers_path:
                self.update_pes_database(transfers_path)
            
            self.logger.info("PES 2013 update process completed successfully")
        
        except Exception as e:
            self.logger.error(f"Update process failed: {e}")
        
        finally:
            self.logger.info("Update process finished")

def main():
    """
    Command-line interface for PES Updater
    """
    parser = argparse.ArgumentParser(description="PES 2013 Updater")
    parser.add_argument('--transfers', action='store_true', help='Update player transfers')
    parser.add_argument('--assets', action='store_true', help='Download team assets')
    parser.add_argument('--database', action='store_true', help='Update PES database')
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], 
                        default='INFO', help='Set logging level')
    
    # Parse arguments
    args = parser.parse_args()
    
    # If no specific flags are set, run all updates
    run_all = not (args.transfers or args.assets or args.database)
    
    # Initialize and run updater
    updater = PESUpdater(log_level=args.log_level)
    updater.run(
        update_transfers=run_all or args.transfers,
        download_assets=run_all or args.assets,
        update_database=run_all or args.database
    )

if __name__ == "__main__":
    main()
