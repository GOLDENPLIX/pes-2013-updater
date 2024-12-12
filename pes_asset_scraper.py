import os
import re
import logging
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed
from logging_config import setup_logging

class PESAssetScraper:
    def __init__(self, base_dir='data/assets'):
        """
        Initialize PES Asset Scraper
        
        :param base_dir: Base directory to save assets
        """
        # Setup logging
        self.logger = setup_logging()
        
        # Configure base directories
        self.base_dir = base_dir
        self.logo_dir = os.path.join(base_dir, 'logos')
        self.kit_dir = os.path.join(base_dir, 'kits')
        
        # Create directories
        os.makedirs(self.logo_dir, exist_ok=True)
        os.makedirs(self.kit_dir, exist_ok=True)
        
        # Known PES modding sources
        self.sources = {
            'pesmaster': {
                'base_url': 'https://www.pesmaster.com',
                'search_url': 'https://www.pesmaster.com/search/?q={}',
                'team_selector': 'a[href*="/team/"]',
                'logo_selector': 'img.team-logo',
                'kit_selector': 'img.kit'
            },
            'pes_world': {
                'base_url': 'https://www.pesworld.net',
                'search_url': 'https://www.pesworld.net/search?q={}',
                'team_selector': 'a[href*="/team/"]',
                'logo_selector': 'img.team-logo',
                'kit_selector': 'img.kit'
            }
        }
    
    def _sanitize_filename(self, filename):
        """
        Sanitize filename to remove invalid characters
        
        :param filename: Original filename
        :return: Sanitized filename
        """
        return re.sub(r'[^\w\-_\. ]', '_', filename)
    
    def _download_image(self, url, save_path, max_retries=3):
        """
        Download image with retry mechanism
        
        :param url: Image URL
        :param save_path: Path to save image
        :param max_retries: Maximum retry attempts
        :return: Boolean indicating download success
        """
        for attempt in range(max_retries):
            try:
                response = requests.get(url, stream=True, timeout=10)
                response.raise_for_status()
                
                with open(save_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                self.logger.info(f"Downloaded: {save_path}")
                return True
            
            except requests.RequestException as e:
                self.logger.warning(f"Download attempt {attempt + 1} failed: {e}")
        
        self.logger.error(f"Failed to download: {url}")
        return False
    
    def search_team(self, team_name, source='pesmaster'):
        """
        Search for a team on a specific source
        
        :param team_name: Name of the team
        :param source: Source website (default: pesmaster)
        :return: Team page URL or None
        """
        try:
            source_config = self.sources.get(source, self.sources['pesmaster'])
            search_url = source_config['search_url'].format(team_name.replace(' ', '+'))
            
            response = requests.get(search_url, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            team_link = soup.select_one(source_config['team_selector'])
            if team_link:
                return urljoin(source_config['base_url'], team_link['href'])
        
        except requests.RequestException as e:
            self.logger.error(f"Team search error for {team_name}: {e}")
        
        return None
    
    def download_team_assets(self, team_name, source='pesmaster'):
        """
        Download logo and kit for a specific team
        
        :param team_name: Name of the team
        :param source: Source website
        :return: Dictionary of downloaded assets
        """
        safe_team_name = self._sanitize_filename(team_name)
        
        # Search for team page
        team_url = self.search_team(team_name, source)
        if not team_url:
            self.logger.warning(f"No page found for team: {team_name}")
            return None
        
        try:
            response = requests.get(team_url, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            source_config = self.sources.get(source, self.sources['pesmaster'])
            
            # Prepare asset paths
            logo_path = os.path.join(self.logo_dir, f"{safe_team_name}_logo.png")
            kit_path = os.path.join(self.kit_dir, f"{safe_team_name}_kit.png")
            
            # Download logo
            logo_img = soup.select_one(source_config['logo_selector'])
            logo_url = logo_img['src'] if logo_img else None
            
            # Download kit
            kit_img = soup.select_one(source_config['kit_selector'])
            kit_url = kit_img['src'] if kit_img else None
            
            # Prepare full URLs
            logo_url = urljoin(source_config['base_url'], logo_url) if logo_url else None
            kit_url = urljoin(source_config['base_url'], kit_url) if kit_url else None
            
            # Download assets
            assets = {
                'logo': self._download_image(logo_url, logo_path) if logo_url else False,
                'kit': self._download_image(kit_url, kit_path) if kit_url else False
            }
            
            return assets
        
        except requests.RequestException as e:
            self.logger.error(f"Error downloading assets for {team_name}: {e}")
            return None
    
    def download_multiple_teams(self, teams, max_workers=5):
        """
        Download assets for multiple teams in parallel
        
        :param teams: List of team names
        :param max_workers: Maximum parallel download workers
        :return: Dictionary of team download results
        """
        results = {}
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
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
                    results[team] = result
                    
                    if result:
                        self.logger.info(f"Successfully processed assets for {team}")
                    else:
                        self.logger.warning(f"No assets found for {team}")
                
                except Exception as e:
                    self.logger.error(f"Error processing {team}: {e}")
                    results[team] = None
        
        return results

def main():
    """
    Example usage of PES Asset Scraper
    """
    # Sample teams to download
    teams = [
        "Manchester United", 
        "Liverpool", 
        "Barcelona", 
        "Real Madrid", 
        "Bayern Munich"
    ]
    
    # Initialize scraper
    scraper = PESAssetScraper()
    
    # Download team assets
    results = scraper.download_multiple_teams(teams)
    
    # Print summary
    print("\n=== Asset Download Summary ===")
    for team, assets in results.items():
        if assets:
            print(f"{team}: Logo={'✓' if assets['logo'] else '✗'}, Kit={'✓' if assets['kit'] else '✗'}")
        else:
            print(f"{team}: No assets found")

if __name__ == "__main__":
    main()
