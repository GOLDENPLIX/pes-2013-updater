import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_football_data_api():
    """
    Test connectivity and basic functionality of Football Data API
    """
    # Retrieve API key
    api_key = os.getenv("FOOTBALL_DATA_API_KEY")
    
    if not api_key or api_key == "your_api_key_here":
        print("API Key is not set. Please update .env file.")
        return False
    
    # API endpoints to test
    test_endpoints = [
        "https://api.football-data.org/v4/competitions",
        "https://api.football-data.org/v4/competitions/2021/matches"  # Premier League matches
    ]
    
    for endpoint in test_endpoints:
        try:
            headers = {
                "X-Auth-Token": api_key,
                "User-Agent": "PES 2013 Updater Bot/1.0"
            }
            
            response = requests.get(endpoint, headers=headers)
            
            if response.status_code == 200:
                print(f"Successful connection to {endpoint}")
                # Optionally print some basic info
                data = response.json()
                if 'competitions' in data:
                    print(f"Total Competitions: {len(data['competitions'])}")
                elif 'matches' in data:
                    print(f"Total Matches: {len(data['matches'])}")
            else:
                print(f"Failed to connect to {endpoint}")
                print(f"Status Code: {response.status_code}")
                print(f"Response: {response.text}")
                return False
        
        except requests.exceptions.RequestException as e:
            print(f"Request Error: {e}")
            return False
    
    return True

if __name__ == "__main__":
    print("Testing Football Data API Connection...")
    if test_football_data_api():
        print("API Test Completed Successfully!")
    else:
        print("API Test Failed. Check your configuration.")
