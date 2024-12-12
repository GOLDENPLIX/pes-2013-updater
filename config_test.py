import os
import sys
import json
import logging
import requests
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed

class ConfigurationTester:
    def __init__(self):
        """
        Initialize configuration tester
        Load environment variables and set up logging
        """
        # Ensure UTF-8 encoding for console output
        sys.stdout.reconfigure(encoding='utf-8')
        
        # Load environment variables
        load_dotenv()
        
        # Configure logging
        logging.basicConfig(
            level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')),
            format='%(asctime)s - %(levelname)s: %(message)s',
            filename=os.getenv('LOG_FILE', 'logs/config_test.log')
        )
        
        self.logger = logging.getLogger(__name__)
    
    def test_api_connectivity(self):
        """
        Test Football Data API connectivity
        """
        self.logger.info("Testing Football Data API Connectivity")
        
        api_key = os.getenv('FOOTBALL_DATA_API_KEY')
        base_url = os.getenv('API_BASE_URL')
        
        if not api_key or not base_url:
            self.logger.error("Missing API Key or Base URL")
            print("Error: Missing API Key or Base URL")
            return False
        
        headers = {
            'X-Auth-Token': api_key,
            'Content-Type': 'application/json'
        }
        
        try:
            # Test competition endpoint
            competitions_url = f"{base_url}/competitions"
            response = requests.get(competitions_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                competitions = response.json().get('competitions', [])
                self.logger.info(f"Successfully retrieved {len(competitions)} competitions")
                print(f"API Test: Successfully retrieved {len(competitions)} competitions")
                return True
            else:
                self.logger.error(f"API Request Failed. Status Code: {response.status_code}")
                print(f"Error: API Request Failed. Status Code: {response.status_code}")
                return False
        
        except requests.RequestException as e:
            self.logger.error(f"API Connection Error: {e}")
            print(f"Error: API Connection Error: {e}")
            return False
    
    def test_directory_structure(self):
        """
        Validate and create necessary directories
        """
        self.logger.info("Testing Directory Structure")
        print("Testing Directory Structure...")
        
        directories = [
            os.getenv('KIT_FOLDER'),
            os.getenv('LOGO_FOLDER'),
            os.getenv('BACKUP_FOLDER'),
            os.path.dirname(os.getenv('PES_DB_PATH', 'data/transfers')),
            'logs'
        ]
        
        success = True
        for dir_path in directories:
            if dir_path:
                try:
                    os.makedirs(dir_path, exist_ok=True)
                    self.logger.info(f"Created/Verified directory: {dir_path}")
                    print(f"Directory created/verified: {dir_path}")
                except Exception as e:
                    self.logger.error(f"Error creating directory {dir_path}: {e}")
                    print(f"Error creating directory {dir_path}: {e}")
                    success = False
        
        return success
    
    def test_asset_sources(self):
        """
        Test asset source URLs
        """
        self.logger.info("Testing Asset Source URLs")
        print("Testing Asset Source URLs...")
        
        asset_urls = {
            'Logo Base URL': os.getenv('LOGO_BASE_URL'),
            'Kit Base URL': os.getenv('KIT_BASE_URL'),
            'PES Master Base URL': os.getenv('PESMASTER_BASE_URL')
        }
        
        def test_url(name, url):
            try:
                # Use get instead of head to handle more scenarios
                response = requests.get(url, timeout=5)
                status = response.status_code in [200, 302, 403]  # More lenient status checks
                self.logger.info(f"{name}: {'Accessible' if status else 'Inaccessible'}")
                print(f"{name}: {' Accessible' if status else ' Inaccessible'}")
                return status
            except requests.RequestException:
                self.logger.warning(f"{name}: Connection failed")
                print(f"{name}:  Connection failed")
                return False
        
        results = {}
        for name, url in asset_urls.items():
            if url:
                results[name] = test_url(name, url)
        
        # Consider test passed if at least one URL is accessible
        return len(results) > 0 and any(results.values())
    
    def test_configuration_parsing(self):
        """
        Test parsing of complex configuration settings
        """
        self.logger.info("Testing Configuration Parsing")
        print("Testing Configuration Parsing...")
        
        try:
            # Test team codes
            team_codes = os.getenv('TEAM_CODES', '').strip('"').split(',')
            print(f"Team Codes: {team_codes}")
            
            # Test competition mapping
            comp_mapping_str = os.getenv('COMPETITION_MAPPING', '{}')
            comp_mapping = json.loads(comp_mapping_str)
            print(f"Competition Mapping: {comp_mapping}")
            
            # Test download settings
            max_workers = int(os.getenv('MAX_DOWNLOAD_WORKERS', 5))
            retry_downloads = os.getenv('RETRY_FAILED_DOWNLOADS', 'true').lower() == 'true'
            
            print(f"Max Download Workers: {max_workers}")
            print(f"Retry Failed Downloads: {retry_downloads}")
            
            return True
        except Exception as e:
            self.logger.error(f"Configuration Parsing Error: {e}")
            print(f"Error: Configuration Parsing Error: {e}")
            return False
    
    def run_comprehensive_test(self):
        """
        Run all configuration tests
        """
        self.logger.info("Starting Comprehensive Configuration Test")
        print("\n=== PES 2013 Updater Configuration Test ===")
        
        tests = [
            ('API Connectivity', self.test_api_connectivity),
            ('Directory Structure', self.test_directory_structure),
            ('Asset Sources', self.test_asset_sources),
            ('Configuration Parsing', self.test_configuration_parsing)
        ]
        
        overall_success = True
        for test_name, test_func in tests:
            try:
                result = test_func()
                if result:
                    self.logger.info(f"{test_name} Test: PASSED")
                    print(f"{test_name} Test:  PASSED")
                else:
                    self.logger.error(f"{test_name} Test: FAILED")
                    print(f"{test_name} Test:  FAILED")
                    overall_success = False
            except Exception as e:
                self.logger.error(f"{test_name} Test Error: {e}")
                print(f"{test_name} Test:  ERROR - {e}")
                overall_success = False
        
        return overall_success

def main():
    tester = ConfigurationTester()
    success = tester.run_comprehensive_test()
    
    print("\n--- Configuration Test Results ---")
    print(f"Overall Configuration Status: {' PASSED' if success else ' FAILED'}")
    print("Check logs for detailed information.")
    
    return success

if __name__ == "__main__":
    main()
