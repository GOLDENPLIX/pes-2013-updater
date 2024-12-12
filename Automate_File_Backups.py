import os
import shutil
import logging
from config import logger

def backup_files(pes_folder, backup_folder):
    """
    Create a backup of the specified folder with comprehensive error handling.
    
    Args:
        pes_folder (str): Source folder to backup
        backup_folder (str): Destination folder for backup
    
    Returns:
        bool: True if backup successful, False otherwise
    """
    try:
        # Validate input paths
        if not os.path.exists(pes_folder):
            logger.error(f"Source folder {pes_folder} does not exist.")
            return False
        
        # Create backup folder if it doesn't exist
        os.makedirs(backup_folder, exist_ok=True)
        
        # Perform backup with detailed logging
        logger.info(f"Starting backup from {pes_folder} to {backup_folder}")
        shutil.copytree(pes_folder, backup_folder, dirs_exist_ok=True)
        
        logger.info("Backup created successfully.")
        return True
    
    except PermissionError:
        logger.error("Permission denied when creating backup.")
    except shutil.Error as e:
        logger.error(f"Error during backup: {e}")
    except Exception as e:
        logger.error(f"Unexpected error occurred during backup: {e}")
    
    return False

# Example usage
if __name__ == "__main__":
    from config import Config
    
    paths = Config.get_file_paths()
    success = backup_files(paths['pes_folder'], paths['backup_folder'])
