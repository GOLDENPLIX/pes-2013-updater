import os
import shutil

def update_kits_and_logos(kit_folder, logo_folder, destination_folder):
    shutil.copytree(kit_folder, os.path.join(destination_folder, 'kits'), dirs_exist_ok=True)
    shutil.copytree(logo_folder, os.path.join(destination_folder, 'logos'), dirs_exist_ok=True)
    print("Kits and logos updated.")
