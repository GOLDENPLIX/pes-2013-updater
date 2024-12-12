import os
from turtle import pd

def update_pes_database(transfer_data, pes_db_path):
    # Load PES database (e.g., CSV or custom tool input)
    db = pd.read_csv(pes_db_path)
    
    for _, transfer in transfer_data.iterrows():
        player = db.loc[db['PlayerName'] == transfer['player']['name']]
        if not player.empty:
            db.loc[player.index, 'Team'] = transfer['team']['name']
    
    # Save updated database
    db.to_csv(pes_db_path, index=False)
    print("Database updated successfully.")
