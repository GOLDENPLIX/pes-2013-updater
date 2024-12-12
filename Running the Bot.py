if __name__ == "__main__":
    API_KEY = "your_api_key_here"
    PES_DB_PATH = "path_to_pes_db.csv"
    KIT_FOLDER = "path_to_new_kits"
    LOGO_FOLDER = "path_to_new_logos"
    PES_FOLDER = "path_to_pes_2013"
    BACKUP_FOLDER = "path_to_backup"

    # Step 1: Backup
    backup_files(PES_FOLDER, BACKUP_FOLDER)

    # Step 2: Fetch Transfers
    transfer_data = fetch_transfer_data(API_KEY)
    if transfer_data is not None:
        update_pes_database(transfer_data, PES_DB_PATH)

    # Step 3: Update Kits and Logos
    update_kits_and_logos(KIT_FOLDER, LOGO_FOLDER, PES_FOLDER)

    print("PES 2013 updated successfully!")
