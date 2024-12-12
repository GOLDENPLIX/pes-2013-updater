import os

def create_project_structure():
    """
    Create a comprehensive folder structure for the PES 2013 Updater
    """
    # Base project directories
    base_dirs = [
        'data',
        'data/transfers',
        'data/kits',
        'data/logos',
        'data/backup',
        'logs',
        'output'
    ]

    # League-specific subdirectories
    leagues = ['Premier_League', 'La_Liga', 'Bundesliga', 'Serie_A', 'Ligue_1']
    
    for base_dir in base_dirs:
        full_path = os.path.join(os.path.dirname(__file__), base_dir)
        os.makedirs(full_path, exist_ok=True)
        print(f"Created directory: {full_path}")
    
    # Create league-specific kit and logo directories
    for league in leagues:
        for asset_type in ['kits', 'logos']:
            league_path = os.path.join(os.path.dirname(__file__), 'data', asset_type, league)
            os.makedirs(league_path, exist_ok=True)
            print(f"Created directory: {league_path}")
    
    # Create a README in each directory to explain its purpose
    for base_dir in base_dirs:
        full_path = os.path.join(os.path.dirname(__file__), base_dir)
        readme_path = os.path.join(full_path, 'README.txt')
        
        readme_content = {
            'data/transfers': "Contains CSV files with player transfer information.",
            'data/kits': "Stores team kit images organized by league.",
            'data/logos': "Stores team logo images organized by league.",
            'data/backup': "Backup of original files before updates.",
            'logs': "Log files for tracking update processes.",
            'output': "Final update packages ready for PES 2013."
        }.get(base_dir, "Project directory for PES 2013 Updater.")
        
        with open(readme_path, 'w') as f:
            f.write(readme_content)
        print(f"Created README in: {readme_path}")

def update_env_paths():
    """
    Update .env file with new directory paths
    """
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    
    with open(env_path, 'r') as f:
        env_content = f.read()
    
    # Update paths
    updated_content = env_content.replace(
        'PES_DB_PATH=data/pes_database.csv',
        'PES_DB_PATH=data/transfers/pes_database.csv'
    ).replace(
        'KIT_FOLDER=data/kits',
        'KIT_FOLDER=data/kits/Premier_League'
    ).replace(
        'LOGO_FOLDER=data/logos',
        'LOGO_FOLDER=data/logos/Premier_League'
    )
    
    with open(env_path, 'w') as f:
        f.write(updated_content)
    
    print("Updated .env file with new paths")

if __name__ == '__main__':
    create_project_structure()
    update_env_paths()
    print("\nProject structure setup complete!")
