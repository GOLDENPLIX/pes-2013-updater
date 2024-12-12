import os
import logging
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv

def setup_logging(log_file=None, log_level=None):
    """
    Configure comprehensive logging for the PES 2013 Updater
    
    :param log_file: Optional log file path
    :param log_level: Optional log level
    :return: Configured logger
    """
    # Load environment variables
    load_dotenv()
    
    # Default log configuration from .env
    log_file = log_file or os.getenv('LOG_FILE', 'logs/pes_updater.log')
    log_level_str = log_level or os.getenv('LOG_LEVEL', 'INFO')
    
    # Ensure log directory exists
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    # Convert log level string to logging constant
    log_level = getattr(logging, log_level_str.upper(), logging.INFO)
    
    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Create a rotating file handler
    file_handler = RotatingFileHandler(
        log_file, 
        maxBytes=10*1024*1024,  # 10 MB
        backupCount=5
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    ))
    file_handler.setLevel(log_level)
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(
        '%(asctime)s [%(levelname)s]: %(message)s',
        datefmt='%H:%M:%S'
    ))
    console_handler.setLevel(log_level)
    
    # Get root logger and add handlers
    root_logger = logging.getLogger()
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    return root_logger

def log_system_info():
    """
    Log system and environment information
    """
    logger = logging.getLogger(__name__)
    
    # Log system details
    logger.info("=== PES 2013 Updater System Information ===")
    logger.info(f"Python Version: {os.sys.version}")
    logger.info(f"Operating System: {os.sys.platform}")
    
    # Log environment variables
    logger.info("=== Environment Configuration ===")
    for key, value in os.environ.items():
        if key.startswith(('FOOTBALL', 'DOWNLOAD', 'LOG', 'PES')):
            logger.info(f"{key}: {value}")
    
    logger.info("===================================")

def main():
    """
    Demonstration of logging configuration
    """
    # Setup logging
    logger = setup_logging()
    
    # Log system information
    log_system_info()
    
    # Example logging scenarios
    logger.info("PES 2013 Updater Logging System Initialized")
    logger.debug("This is a debug message")
    logger.warning("This is a warning message")
    
    try:
        # Simulate an error
        1 / 0
    except Exception as e:
        logger.error(f"An error occurred: {e}", exc_info=True)

if __name__ == "__main__":
    main()
