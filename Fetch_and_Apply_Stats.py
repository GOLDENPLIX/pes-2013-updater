import pandas as pd
from config import logger

def update_pes_database(transfer_data, pes_db_path):
    """
    Update PES database with transfer information.
    
    Args:
        transfer_data (pd.DataFrame): DataFrame containing transfer information
        pes_db_path (str): Path to the PES database CSV file
    
    Returns:
        bool: True if update successful, False otherwise
    """
    try:
        # Load existing database
        db = pd.read_csv(pes_db_path)
        
        # Update team information for transferred players
        for _, transfer in transfer_data.iterrows():
            player_name = transfer.get('player', '')
            new_team = transfer.get('to_team', '')
            
            # Update player's team in the database
            db.loc[db['PlayerName'] == player_name, 'Team'] = new_team
        
        # Save updated database
        db.to_csv(pes_db_path, index=False)
        
        logger.info(f"Successfully updated database at {pes_db_path}")
        return True
    
    except Exception as e:
        logger.error(f"Error updating database: {e}")
        return False
