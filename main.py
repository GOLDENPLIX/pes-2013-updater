import sys
import time
import traceback
from config import logger, Config
from Automate_File_Backups import backup_files
from web_scraping_to_get_transfer_updates import fetch_transfer_data
from Fetch_and_Apply_Stats import update_pes_database
from Manage_Kits_and_Logos import update_kits_and_logos

class UpdateError(Exception):
    """Custom exception for update process errors."""
    pass

def retry_operation(operation, max_retries=3, delay=5):
    """
    Retry an operation with exponential backoff.
    
    Args:
        operation (callable): Function to retry
        max_retries (int): Maximum number of retry attempts
        delay (int): Initial delay between retries
    
    Returns:
        Result of the operation or raises UpdateError
    """
    for attempt in range(max_retries):
        try:
            return operation()
        except Exception as e:
            if attempt == max_retries - 1:
                logger.error(f"Operation failed after {max_retries} attempts: {e}")
                raise UpdateError(f"Operation failed: {e}")
            
            logger.warning(f"Attempt {attempt + 1} failed. Retrying in {delay} seconds...")
            time.sleep(delay)
            delay *= 2  # Exponential backoff

def main():
    """
    Main orchestration script for PES 2013 update process.
    Handles the entire update workflow with comprehensive error handling and recovery.
    """
    try:
        logger.info("Starting PES 2013 Update Process")
        
        # Get configuration paths
        paths = Config.get_file_paths()
        
        # Step 1: Backup PES Folder
        logger.info("Step 1: Creating Backup")
        backup_success = retry_operation(
            lambda: backup_files(paths['pes_folder'], paths['backup_folder'])
        )
        
        # Step 2: Fetch Transfer Data
        logger.info("Step 2: Fetching Transfer Data")
        transfer_data = retry_operation(fetch_transfer_data)
        
        # Step 3: Update PES Database
        logger.info("Step 3: Updating PES Database")
        update_success = retry_operation(
            lambda: update_pes_database(transfer_data, paths['pes_db_path'])
        )
        
        # Step 4: Update Kits and Logos
        logger.info("Step 4: Updating Kits and Logos")
        kits_logos_success = retry_operation(
            lambda: update_kits_and_logos(
                paths['kit_folder'], 
                paths['logo_folder'], 
                paths['pes_folder']
            )
        )
        
        logger.info("PES 2013 Update Process Completed Successfully!")
        return True
    
    except UpdateError as update_err:
        logger.critical(f"Critical update error: {update_err}")
        # Optional: Implement rollback mechanism here
        return False
    except Exception as e:
        logger.error(f"Unexpected error in update process: {e}")
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
