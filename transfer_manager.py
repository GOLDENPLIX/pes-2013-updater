import os
import csv
import logging
import requests
from datetime import datetime
from typing import List, Dict, Optional

class TransferManager:
    def __init__(self, config_path: str = '.env'):
        """
        Initialize TransferManager with configuration
        
        :param config_path: Path to configuration file
        """
        self.logger = logging.getLogger(__name__)
        self.config = self._load_config(config_path)
        
        # Ensure data directories exist
        os.makedirs(self.config.get('TRANSFER_DATA_DIR', 'data/transfers'), exist_ok=True)
    
    def _load_config(self, config_path: str) -> Dict:
        """
        Load configuration from .env file
        
        :param config_path: Path to .env file
        :return: Dictionary of configuration settings
        """
        from dotenv import dotenv_values
        return dotenv_values(config_path)
    
    def fetch_transfers(self) -> List[Dict]:
        """
        Fetch latest transfer data from Football Data API
        
        :return: List of transfer dictionaries
        """
        api_key = self.config.get('FOOTBALL_DATA_API_KEY')
        base_url = self.config.get('API_BASE_URL', 'https://api.football-data.org/v4')
        
        if not api_key:
            self.logger.error("No API key found for Football Data API")
            return []
        
        headers = {
            'X-Auth-Token': api_key,
            'Content-Type': 'application/json'
        }
        
        transfers = []
        
        try:
            # Fetch transfers for configured leagues
            leagues = self.config.get('COMPETITIONS', '').split(',')
            
            for league in leagues:
                url = f"{base_url}/competitions/{league}/transfers"
                response = requests.get(url, headers=headers, timeout=15)
                response.raise_for_status()
                
                league_transfers = response.json().get('transfers', [])
                transfers.extend(self._process_transfers(league_transfers, league))
        
        except requests.RequestException as e:
            self.logger.error(f"Error fetching transfers: {e}")
        
        return transfers
    
    def _process_transfers(self, transfers: List[Dict], league: str) -> List[Dict]:
        """
        Process and clean transfer data
        
        :param transfers: Raw transfer data
        :param league: League code
        :return: Processed transfer data
        """
        processed_transfers = []
        
        for transfer in transfers:
            processed_transfer = {
                'league': league,
                'player_name': transfer.get('player', {}).get('name', 'Unknown'),
                'player_id': transfer.get('player', {}).get('id'),
                'from_team': transfer.get('transferFrom', {}).get('name', 'Unknown'),
                'to_team': transfer.get('transferTo', {}).get('name', 'Unknown'),
                'transfer_date': transfer.get('date', datetime.now().isoformat()),
                'transfer_fee': transfer.get('fee', {}).get('value', 0)
            }
            processed_transfers.append(processed_transfer)
        
        return processed_transfers
    
    def save_transfers(self, transfers: List[Dict], filename: Optional[str] = None) -> str:
        """
        Save transfers to a CSV file
        
        :param transfers: List of processed transfers
        :param filename: Optional custom filename
        :return: Path to saved transfer file
        """
        if not transfers:
            self.logger.warning("No transfers to save")
            return ''
        
        # Generate filename if not provided
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(
                self.config.get('TRANSFER_DATA_DIR', 'data/transfers'),
                f"transfers_{timestamp}.csv"
            )
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = transfers[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                writer.writerows(transfers)
            
            self.logger.info(f"Transfers saved to {filename}")
            return filename
        
        except IOError as e:
            self.logger.error(f"Error saving transfers: {e}")
            return ''
    
    def update_transfers(self) -> bool:
        """
        Comprehensive transfer update process
        
        :return: Boolean indicating update success
        """
        self.logger.info("Starting transfer data update")
        
        try:
            # Fetch transfers
            transfers = self.fetch_transfers()
            
            if not transfers:
                self.logger.warning("No transfers found")
                return False
            
            # Save transfers
            save_path = self.save_transfers(transfers)
            
            if not save_path:
                self.logger.error("Failed to save transfers")
                return False
            
            self.logger.info(f"Successfully updated transfers: {len(transfers)} records")
            return True
        
        except Exception as e:
            self.logger.error(f"Transfer update failed: {e}")
            return False

def main():
    """
    Example usage of TransferManager
    """
    logging.basicConfig(level=logging.INFO)
    transfer_manager = TransferManager()
    transfer_manager.update_transfers()

if __name__ == "__main__":
    main()
