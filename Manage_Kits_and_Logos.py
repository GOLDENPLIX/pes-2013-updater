import os
import shutil
from config import logger

def update_kits_and_logos(kit_folder, logo_folder, destination_folder):
    """
    Update kits and logos in the PES 2013 folder.
    
    Args:
        kit_folder (str): Source folder for kits
        logo_folder (str): Source folder for logos
        destination_folder (str): Destination PES folder
    
    Returns:
        bool: True if update successful, False otherwise
    """
    try:
        # Validate input folders
        if not os.path.exists(kit_folder):
            logger.error(f"Kit folder not found: {kit_folder}")
            return False
        
        if not os.path.exists(logo_folder):
            logger.error(f"Logo folder not found: {logo_folder}")
            return False
        
        # Create destination subfolders if they don't exist
        kits_dest = os.path.join(destination_folder, 'kits')
        logos_dest = os.path.join(destination_folder, 'logos')
        
        os.makedirs(kits_dest, exist_ok=True)
        os.makedirs(logos_dest, exist_ok=True)
        
        # Copy kits
        shutil.copytree(kit_folder, kits_dest, dirs_exist_ok=True)
        
        # Copy logos
        shutil.copytree(logo_folder, logos_dest, dirs_exist_ok=True)
        
        logger.info("Successfully updated kits and logos")
        return True
    
    except Exception as e:
        logger.error(f"Error updating kits and logos: {e}")
        return False
