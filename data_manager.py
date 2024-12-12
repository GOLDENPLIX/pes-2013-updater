import os
import json
import csv
import requests
from datetime import datetime
import shutil
import zipfile
import concurrent.futures
from bs4 import BeautifulSoup
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DataManager:
    def __init__(self):
        # Directories for storing data
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.transfers_dir = os.path.join(self.base_dir, 'data', 'transfers')
        self.kits_dir = os.path.join(self.base_dir, 'data', 'kits')
        self.logos_dir = os.path.join(self.base_dir, 'data', 'logos')
        self.output_dir = os.path.join(self.base_dir, 'output')
        
        # Create necessary directories
        for directory in [self.transfers_dir, self.kits_dir, self.logos_dir, self.output_dir]:
            os.makedirs(directory, exist_ok=True)
        
        # API Configuration
        self.api_key = os.getenv('FOOTBALL_DATA_API_KEY')
        self.headers = {
            'X-Auth-Token': self.api_key,
            'User-Agent': 'PES 2013 Updater Bot/1.0'
        }
        
        # Competition configurations
        self.competitions = {
            'PL': {'id': 2021, 'name': 'Premier League'},
            'PD': {'id': 2014, 'name': 'La Liga'},
            'BL1': {'id': 2002, 'name': 'Bundesliga'},
            'SA': {'id': 2019, 'name': 'Serie A'},
            'FL1': {'id': 2015, 'name': 'Ligue 1'}
        }
    
    def fetch_transfers(self, competition_code=None):
        """
        Fetch transfers for specified competition or all configured competitions
        
        :param competition_code: Optional specific competition code (e.g., 'PL')
        :return: Dictionary of transfers by competition
        """
        all_transfers = {}
        
        # Determine which competitions to fetch
        target_competitions = [competition_code] if competition_code else list(self.competitions.keys())
        
        for comp_code in target_competitions:
            try:
                # Fetch transfers for the competition
                url = f"https://api.football-data.org/v4/competitions/{self.competitions[comp_code]['id']}/matches"
                response = requests.get(url, headers=self.headers)
                
                if response.status_code == 200:
                    data = response.json()
                    # Process and extract transfers (placeholder logic)
                    transfers = self._parse_transfers(data, comp_code)
                    all_transfers[comp_code] = transfers
                else:
                    print(f"Error fetching transfers for {comp_code}: {response.status_code}")
            
            except Exception as e:
                print(f"Exception in fetch_transfers for {comp_code}: {e}")
        
        return all_transfers
    
    def _parse_transfers(self, data, competition_code):
        """
        Parse transfer data from API response
        
        :param data: API response data
        :param competition_code: Competition code
        :return: List of transfer dictionaries
        """
        transfers = []
        # Implement transfer parsing logic based on API response structure
        # This is a placeholder and needs to be adapted to the actual API response
        for match in data.get('matches', []):
            transfer = {
                'competition': self.competitions[competition_code]['name'],
                'player': 'Unknown',  # Replace with actual player name extraction
                'from_team': match.get('homeTeam', {}).get('name', 'Unknown'),
                'to_team': match.get('awayTeam', {}).get('name', 'Unknown'),
                'transfer_date': match.get('utcDate', datetime.now().isoformat())
            }
            transfers.append(transfer)
        
        return transfers
    
    def save_transfers_to_csv(self, transfers, filename=None):
        """
        Save transfers to a CSV file
        
        :param transfers: Dictionary of transfers by competition
        :param filename: Optional custom filename
        """
        if not filename:
            filename = os.path.join(self.transfers_dir, f'transfers_{datetime.now().strftime("%Y%m%d")}.csv')
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['competition', 'player', 'from_team', 'to_team', 'transfer_date']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for comp_transfers in transfers.values():
                for transfer in comp_transfers:
                    writer.writerow(transfer)
        
        print(f"Transfers saved to {filename}")
        return filename
    
    def download_team_assets(self, team_name, asset_type='logo'):
        """
        Download team assets (logos or kits)
        
        :param team_name: Name of the team
        :param asset_type: 'logo' or 'kit'
        :return: Path to downloaded asset
        """
        # Placeholder for asset download logic
        # This would typically involve finding a reliable source for team assets
        base_url = "https://example.com/pes_assets"  # Replace with actual asset source
        
        # Sanitize team name for filename
        safe_team_name = re.sub(r'[^\w\-_\. ]', '_', team_name)
        
        if asset_type == 'logo':
            save_dir = self.logos_dir
            url = f"{base_url}/logos/{safe_team_name}.png"
        else:  # kit
            save_dir = self.kits_dir
            url = f"{base_url}/kits/{safe_team_name}_home.png"
        
        # Ensure save directory exists
        os.makedirs(save_dir, exist_ok=True)
        
        # File path for saving
        file_path = os.path.join(save_dir, f"{safe_team_name}_{asset_type}.png")
        
        try:
            response = requests.get(url, stream=True)
            if response.status_code == 200:
                with open(file_path, 'wb') as f:
                    shutil.copyfileobj(response.raw, f)
                print(f"Downloaded {asset_type} for {team_name}")
                return file_path
            else:
                print(f"Failed to download {asset_type} for {team_name}")
                return None
        except Exception as e:
            print(f"Error downloading {asset_type} for {team_name}: {e}")
            return None
    
    def organize_assets(self, team_name, asset_files):
        """
        Organize downloaded assets into team-specific folders
        
        :param team_name: Name of the team
        :param asset_files: List of asset file paths
        """
        # Sanitize team name for directory
        safe_team_name = re.sub(r'[^\w\-_\. ]', '_', team_name)
        team_dir = os.path.join(self.output_dir, safe_team_name)
        
        # Create team directory
        os.makedirs(team_dir, exist_ok=True)
        
        # Move assets to team directory
        for file_path in asset_files:
            if file_path and os.path.exists(file_path):
                shutil.move(file_path, os.path.join(team_dir, os.path.basename(file_path)))
    
    def create_update_package(self, transfers=None, teams=None):
        """
        Create a ZIP package of all updates
        
        :param transfers: Optional transfers to include
        :param teams: Optional list of teams to include assets for
        :return: Path to created ZIP file
        """
        # Create a timestamped package
        package_name = f'pes_update_{datetime.now().strftime("%Y%m%d_%H%M%S")}.zip'
        package_path = os.path.join(self.output_dir, package_name)
        
        # Fetch transfers if not provided
        if not transfers:
            transfers = self.fetch_transfers()
        
        # Save transfers to CSV
        transfers_csv = self.save_transfers_to_csv(transfers)
        
        # Download assets for specified teams or all known teams
        if not teams:
            teams = ['Barcelona', 'Real Madrid', 'Liverpool', 'Manchester United']  # Example teams
        
        # Parallel download of assets
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            logo_futures = {executor.submit(self.download_team_assets, team, 'logo'): team for team in teams}
            kit_futures = {executor.submit(self.download_team_assets, team, 'kit'): team for team in teams}
        
        # Collect downloaded assets
        downloaded_assets = []
        for future in concurrent.futures.as_completed(list(logo_futures.keys()) + list(kit_futures.keys())):
            asset_path = future.result()
            if asset_path:
                downloaded_assets.append(asset_path)
        
        # Create ZIP package
        with zipfile.ZipFile(package_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add transfers CSV
            zipf.write(transfers_csv, arcname=os.path.basename(transfers_csv))
            
            # Add downloaded assets
            for asset_path in downloaded_assets:
                zipf.write(asset_path, arcname=os.path.basename(asset_path))
        
        print(f"Update package created: {package_path}")
        return package_path

# Example usage
if __name__ == '__main__':
    dm = DataManager()
    
    # Fetch and save transfers
    transfers = dm.fetch_transfers()
    
    # Create update package
    update_package = dm.create_update_package(transfers)
