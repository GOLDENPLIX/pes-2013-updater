import os
import requests
from bs4 import BeautifulSoup
import re
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from config_manager import ConfigManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s: %(message)s',
    filename='logs/asset_download.log'
)

class AssetScraper:
    def __init__(self, config_manager=None):
        """
        Initialize AssetScraper with configuration
        
        :param config_manager: Optional ConfigManager instance
        """
        self.config = config_manager or ConfigManager()
        
        # Get configuration settings
        self.paths = self.config.get_paths()
        self.download_settings = self.config.get_download_settings()
        
        # Ensure directories exist
        for dir_path in [self.paths['kit_folder'], self.paths['logo_folder']]:
            os.makedirs(dir_path, exist_ok=True)
    
    def download_team_assets(self, team_name):
        """
        Download assets for a specific team
        
        :param team_name: Name of the team
        :return: Dictionary of downloaded assets
        """
        try:
            # Sanitize team name
            safe_team_name = re.sub(r'[^\w\-_\. ]', '_', team_name)
            
            # Create team-specific directory
            team_dir = os.path.join(self.paths['kit_folder'], safe_team_name)
            os.makedirs(team_dir, exist_ok=True)
            
            # Attempt multiple sources
            sources = [
                self._scrape_pesmaster,
                self._scrape_fallback_source
            ]
            
            for source in sources:
                assets = source(team_name)
                if assets:
                    return assets
            
            logging.warning(f"No assets found for team: {team_name}")
            return None
        
        except Exception as e:
            logging.error(f"Error downloading assets for {team_name}: {e}")
            return None
    
    def _scrape_pesmaster(self, team_name):
        """
        Scrape assets from PES Master
        
        :param team_name: Name of the team
        :return: Dictionary of downloaded assets or None
        """
        try:
            search_url = f"https://www.pesmaster.com/search/?q={team_name.replace(' ', '+')}"
            response = requests.get(search_url, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                team_link = soup.find('a', href=re.compile(r'/team/.*'))
                
                if team_link:
                    team_url = f"https://www.pesmaster.com{team_link['href']}"
                    return self._extract_team_assets(team_url, team_name)
            
            return None
        
        except Exception as e:
            logging.error(f"PES Master scraping error for {team_name}: {e}")
            return None
    
    def _scrape_fallback_source(self, team_name):
        """
        Fallback asset scraping method
        
        :param team_name: Name of the team
        :return: Dictionary of downloaded assets or None
        """
        # Implement alternative scraping logic
        # This could be another website or a predefined set of URLs
        logging.info(f"Using fallback source for {team_name}")
        return None
    
    def _extract_team_assets(self, team_url, team_name):
        """
        Extract and download team assets
        
        :param team_url: URL of team page
        :param team_name: Name of the team
        :return: Dictionary of downloaded assets
        """
        safe_team_name = re.sub(r'[^\w\-_\. ]', '_', team_name)
        team_dir = os.path.join(self.paths['kit_folder'], safe_team_name)
        os.makedirs(team_dir, exist_ok=True)
        
        assets = {'kits': [], 'logo': None}
        
        try:
            response = requests.get(team_url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Download kits
                kit_images = soup.find_all('img', {'class': 'kit'})
                for idx, img in enumerate(kit_images):
                    if img.get('src'):
                        kit_url = f"https://www.pesmaster.com{img['src']}"
                        kit_path = os.path.join(team_dir, f'kit_{idx+1}.png')
                        
                        if self._download_image(kit_url, kit_path):
                            assets['kits'].append(kit_path)
                
                # Download logo
                logo_img = soup.find('img', {'class': 'team-logo'})
                if logo_img and logo_img.get('src'):
                    logo_url = f"https://www.pesmaster.com{logo_img['src']}"
                    logo_path = os.path.join(team_dir, 'logo.png')
                    
                    if self._download_image(logo_url, logo_path):
                        assets['logo'] = logo_path
            
            return assets
        
        except Exception as e:
            logging.error(f"Error extracting assets for {team_name}: {e}")
            return None
    
    def _download_image(self, url, save_path, max_retries=3):
        """
        Download image with retry mechanism
        
        :param url: URL of the image
        :param save_path: Path to save the image
        :param max_retries: Maximum number of download attempts
        :return: Boolean indicating success
        """
        for attempt in range(max_retries):
            try:
                response = requests.get(url, stream=True, timeout=10)
                
                if response.status_code == 200:
                    with open(save_path, 'wb') as f:
                        for chunk in response.iter_content(1024):
                            f.write(chunk)
                    
                    logging.info(f"Downloaded: {save_path}")
                    return True
                else:
                    logging.warning(f"Download failed (Attempt {attempt+1}): {url}")
            
            except Exception as e:
                logging.error(f"Download error (Attempt {attempt+1}): {e}")
        
        return False
    
    def download_all_team_assets(self):
        """
        Download assets for all configured teams
        """
        teams = self.download_settings['download_teams']
        
        with ThreadPoolExecutor(max_workers=self.download_settings['max_workers']) as executor:
            # Submit download tasks
            future_to_team = {
                executor.submit(self.download_team_assets, team): team 
                for team in teams
            }
            
            # Process results
            for future in as_completed(future_to_team):
                team = future_to_team[future]
                try:
                    result = future.result()
                    if result:
                        logging.info(f"Successfully downloaded assets for {team}")
                    else:
                        logging.warning(f"No assets found for {team}")
                except Exception as e:
                    logging.error(f"Error processing {team}: {e}")

# Example usage
if __name__ == "__main__":
    scraper = AssetScraper()
    scraper.download_all_team_assets()
