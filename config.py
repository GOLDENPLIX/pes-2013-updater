import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Logging Configuration
def setup_logging():
    """Configure logging for the application."""
    try:
        log_level = getattr(logging, os.getenv('LOG_LEVEL', 'INFO'))
        log_file = os.getenv('LOG_FILE', 'pes_update.log')
        log_format = os.getenv('LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        # Ensure log directory exists
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        logging.basicConfig(
            level=log_level,
            format=log_format,
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger(__name__)
    except Exception as e:
        print(f"Error setting up logging: {e}")
        return logging.getLogger(__name__)

# Configuration Loader
class Config:
    """Centralized configuration management."""
    
    @staticmethod
    def get_api_key():
        """Retrieve API key securely."""
        api_key = os.getenv('FOOTBALL_DATA_API_KEY')
        if not api_key or api_key == 'your_api_key_here':
            raise ValueError("API key not configured. Please set FOOTBALL_DATA_API_KEY in .env")
        return api_key
    
    @staticmethod
    def get_file_paths():
        """Retrieve file paths from environment."""
        paths = {
            'pes_db_path': os.getenv('PES_DB_PATH'),
            'kit_folder': os.getenv('KIT_FOLDER'),
            'logo_folder': os.getenv('LOGO_FOLDER'),
            'pes_folder': os.getenv('PES_FOLDER'),
            'backup_folder': os.getenv('BACKUP_FOLDER')
        }
        
        # Validate paths
        for key, path in paths.items():
            if not path or path.startswith('path/to/'):
                raise ValueError(f"{key.replace('_', ' ').title()} not configured in .env")
        
        return paths

# Initialize logger
logger = setup_logging()
