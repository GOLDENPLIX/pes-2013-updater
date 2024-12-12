import os
import json
from dotenv import load_dotenv

class ConfigManager:
    def __init__(self, env_path=None):
        """
        Initialize configuration manager
        
        :param env_path: Optional path to .env file
        """
        # Load environment variables
        if env_path:
            load_dotenv(env_path)
        else:
            load_dotenv()
    
    def get_league_config(self):
        """
        Retrieve league configuration
        
        :return: Dictionary of league configurations
        """
        league_code = os.getenv('LEAGUE_CODE', 'PL')
        team_codes = os.getenv('TEAM_CODES', '').split(',')
        
        # Parse competition mapping
        comp_mapping_str = os.getenv('COMPETITION_MAPPING', '{}')
        try:
            competition_mapping = json.loads(comp_mapping_str.replace("'", '"'))
        except json.JSONDecodeError:
            competition_mapping = {
                "PL": {"id": 2021, "name": "Premier League"},
                "PD": {"id": 2014, "name": "La Liga"}
            }
        
        return {
            'league_code': league_code,
            'team_codes': team_codes,
            'competition_mapping': competition_mapping
        }
    
    def get_download_settings(self):
        """
        Retrieve download configuration
        
        :return: Dictionary of download settings
        """
        return {
            'download_teams': os.getenv('DOWNLOAD_TEAMS', '').split(','),
            'competitions': os.getenv('COMPETITIONS', '').split(','),
            'max_workers': int(os.getenv('MAX_DOWNLOAD_WORKERS', 5)),
            'retry_downloads': os.getenv('RETRY_FAILED_DOWNLOADS', 'true').lower() == 'true',
            'retry_attempts': int(os.getenv('RETRY_ATTEMPTS', 3))
        }
    
    def get_paths(self):
        """
        Retrieve file paths from configuration
        
        :return: Dictionary of file paths
        """
        return {
            'pes_db_path': os.getenv('PES_DB_PATH', 'data/transfers/pes_database.csv'),
            'kit_folder': os.getenv('KIT_FOLDER', 'data/kits/Premier_League'),
            'logo_folder': os.getenv('LOGO_FOLDER', 'data/logos/Premier_League'),
            'pes_folder': os.getenv('PES_FOLDER', 'path/to/pes_2013'),
            'backup_folder': os.getenv('BACKUP_FOLDER', 'data/backup')
        }
    
    def get_api_config(self):
        """
        Retrieve API configuration
        
        :return: Dictionary of API settings
        """
        return {
            'api_key': os.getenv('FOOTBALL_DATA_API_KEY'),
            'logo_base_url': os.getenv('LOGO_BASE_URL', 'https://api.football-data.org/v4/teams'),
            'kit_base_url': os.getenv('KIT_BASE_URL', 'https://example.com/pes_assets/kits')
        }
    
    def validate_config(self):
        """
        Validate configuration settings
        
        :return: List of configuration errors or empty list if valid
        """
        errors = []
        
        # Check API key
        if not self.get_api_config()['api_key']:
            errors.append("Missing Football Data API key")
        
        # Check download teams
        if not self.get_download_settings()['download_teams']:
            errors.append("No teams specified for download")
        
        # Check paths
        paths = self.get_paths()
        for key, path in paths.items():
            if not path or path == 'path/to/pes_2013':
                errors.append(f"Invalid path for {key}")
        
        return errors

# Example usage
if __name__ == '__main__':
    config_manager = ConfigManager()
    
    # Print configurations
    print("League Configuration:")
    print(json.dumps(config_manager.get_league_config(), indent=2))
    
    print("\nDownload Settings:")
    print(json.dumps(config_manager.get_download_settings(), indent=2))
    
    print("\nFile Paths:")
    print(json.dumps(config_manager.get_paths(), indent=2))
    
    # Validate configuration
    config_errors = config_manager.validate_config()
    if config_errors:
        print("\nConfiguration Errors:")
        for error in config_errors:
            print(f"- {error}")
    else:
        print("\nConfiguration is valid!")
