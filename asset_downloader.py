import os
import time
import logging
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from config_manager import ConfigManager

class AssetDownloader:
    def __init__(self, config_manager=None):
        """
        Initialize AssetDownloader with configuration and logging
        
        :param config_manager: Optional ConfigManager instance
        """
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s: %(message)s',
            filename='logs/asset_download.log',
            filemode='a'
        )
        self.logger = logging.getLogger(__name__)
        
        # Load configuration
        self.config = config_manager or ConfigManager()
        self.download_settings = self.config.get_download_settings()
        self.paths = self.config.get_paths()
        
        # Ensure directories exist
        self._create_directories()
    
    def _create_directories(self):
        """
        Create necessary directories for downloads
        """
        directories = [
            self.paths['kit_folder'],
            self.paths['logo_folder'],
            self.paths['backup_folder']
        ]
        
        for dir_path in directories:
            os.makedirs(dir_path, exist_ok=True)
            self.logger.info(f"Ensured directory exists: {dir_path}")
    
    def download_asset(self, url, dest_path, asset_type='generic'):
        """
        Download an asset with retry mechanism
        
        :param url: URL of the asset to download
        :param dest_path: Destination path to save the asset
        :param asset_type: Type of asset (for logging)
        :return: Boolean indicating download success
        """
        max_retries = self.download_settings.get('retry_attempts', 3)
        retry_delay = 5  # seconds between retry attempts
        
        for attempt in range(1, max_retries + 1):
            try:
                # Create parent directory if it doesn't exist
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                
                # Download asset
                response = requests.get(url, stream=True, timeout=15)
                response.raise_for_status()
                
                with open(dest_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                self.logger.info(f"Successfully downloaded {asset_type}: {url} to {dest_path}")
                return True
            
            except requests.exceptions.RequestException as e:
                self.logger.warning(
                    f"Attempt {attempt}/{max_retries}: Failed to download {asset_type} from {url} - {e}"
                )
                
                if attempt < max_retries:
                    time.sleep(retry_delay)
                else:
                    self.logger.error(
                        f"Failed to download {asset_type} after {max_retries} attempts: {url}"
                    )
                    return False
    
    def download_team_assets(self, team_name):
        """
        Download assets for a specific team
        
        :param team_name: Name of the team
        :return: Dictionary of downloaded assets
        """
        # Sanitize team name for file paths
        safe_team_name = team_name.replace(' ', '_')
        
        # Prepare asset paths
        logo_path = os.path.join(
            self.paths['logo_folder'], 
            f"{safe_team_name}_logo.png"
        )
        kit_path = os.path.join(
            self.paths['kit_folder'], 
            f"{safe_team_name}_kit.png"
        )
        
        # Construct asset URLs (replace with actual sources)
        logo_url = f"{self.config.get_api_config()['logo_base_url']}/{team_name}"
        kit_url = f"{self.config.get_api_config()['kit_base_url']}/{team_name}"
        
        # Download assets
        assets = {
            'logo': self.download_asset(logo_url, logo_path, 'logo'),
            'kit': self.download_asset(kit_url, kit_path, 'kit')
        }
        
        return assets
    
    def download_all_team_assets(self):
        """
        Download assets for all configured teams
        """
        # Get teams from configuration
        teams = self.download_settings.get('download_teams', [])
        
        # Prepare logging
        self.logger.info(f"Starting asset download for {len(teams)} teams")
        
        # Use ThreadPoolExecutor for parallel downloads
        max_workers = self.download_settings.get('max_workers', 5)
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit download tasks
            future_to_team = {
                executor.submit(self.download_team_assets, team): team 
                for team in teams
            }
            
            # Process results
            team_results = {}
            for future in as_completed(future_to_team):
                team = future_to_team[future]
                try:
                    result = future.result()
                    team_results[team] = result
                    
                    # Log individual team download status
                    if all(result.values()):
                        self.logger.info(f"Successfully downloaded assets for {team}")
                    else:
                        self.logger.warning(f"Partial download for {team}")
                
                except Exception as e:
                    self.logger.error(f"Error processing {team}: {e}")
                    team_results[team] = None
        
        # Generate summary report
        self._generate_download_report(team_results)
        
        return team_results
    
    def _generate_download_report(self, team_results):
        """
        Generate a comprehensive download report
        
        :param team_results: Dictionary of download results
        """
        total_teams = len(team_results)
        successful_teams = sum(1 for result in team_results.values() if result and all(result.values()))
        partial_teams = sum(1 for result in team_results.values() if result and not all(result.values()))
        failed_teams = sum(1 for result in team_results.values() if result is None)
        
        report = f"""
        === Asset Download Report ===
        Total Teams: {total_teams}
        Fully Downloaded: {successful_teams}
        Partially Downloaded: {partial_teams}
        Failed Downloads: {failed_teams}
        ============================
        """
        
        self.logger.info(report)
        print(report)

def main():
    """
    Main execution for asset downloading
    """
    downloader = AssetDownloader()
    downloader.download_all_team_assets()

if __name__ == "__main__":
    main()
