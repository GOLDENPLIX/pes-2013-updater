import os
import json
import requests
import pandas as pd
from typing import Optional, Dict, Any, List, Union
from functools import lru_cache
from datetime import datetime, timedelta
from config import logger, Config

class TransferDataSource:
    """
    Abstract base class for transfer data sources.
    """
    def fetch_transfers(self, **kwargs) -> pd.DataFrame:
        """
        Fetch transfer data. To be implemented by subclasses.
        
        Returns:
            pd.DataFrame: Transfer data
        """
        raise NotImplementedError("Subclasses must implement this method")

class FootballDataOrgSource(TransferDataSource):
    """
    Transfer data source from football-data.org API.
    """
    def __init__(self, api_key: str):
        self.base_url = "https://api.football-data.org/v4/transfers"
        self.headers = {"X-Auth-Token": api_key}
    
    def fetch_transfers(self, **kwargs) -> pd.DataFrame:
        """
        Fetch transfers from football-data.org.
        
        Returns:
            pd.DataFrame: Processed transfer data
        """
        try:
            response = requests.get(self.base_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            transfers = pd.DataFrame(data.get('transfers', []))
            return transfers
        except Exception as e:
            logger.error(f"Error fetching transfers from football-data.org: {e}")
            return pd.DataFrame()

class TransferMarketSource(TransferDataSource):
    """
    Transfer data source from transfermarkt.com (simulated).
    """
    def fetch_transfers(self, **kwargs) -> pd.DataFrame:
        """
        Simulated transfer data fetch.
        
        Returns:
            pd.DataFrame: Simulated transfer data
        """
        # In a real implementation, this would use web scraping or an API
        simulated_data = {
            'player': ['Lionel Messi', 'Cristiano Ronaldo', 'Kylian Mbappé'],
            'from_team': ['PSG', 'Al Nassr', 'PSG'],
            'to_team': ['Inter Miami', 'Al Nassr', 'Real Madrid'],
            'transfer_date': ['2023-07-15', '2023-01-22', '2024-01-01']
        }
        return pd.DataFrame(simulated_data)

class TransferDataProcessor:
    """
    Advanced transfer data processing and management.
    """
    def __init__(self, sources: List[TransferDataSource], cache_dir: str = '.transfer_cache'):
        """
        Initialize transfer data processor.
        
        Args:
            sources (List[TransferDataSource]): List of data sources
            cache_dir (str): Directory for caching transfer data
        """
        self.sources = sources
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
    
    def _clean_transfer_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and transform transfer data.
        
        Args:
            df (pd.DataFrame): Raw transfer data
        
        Returns:
            pd.DataFrame: Cleaned transfer data
        """
        # Standardize column names
        column_mapping = {
            'player': 'player_name',
            'from_team': 'previous_team',
            'to_team': 'new_team'
        }
        df = df.rename(columns=column_mapping)
        
        # Data cleaning
        df['player_name'] = df['player_name'].str.strip()
        df['previous_team'] = df['previous_team'].str.strip()
        df['new_team'] = df['new_team'].str.strip()
        
        # Remove duplicates
        df = df.drop_duplicates(subset=['player_name', 'previous_team', 'new_team'])
        
        return df
    
    @lru_cache(maxsize=32)
    def fetch_and_process_transfers(self, preferred_fields: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Fetch transfers from multiple sources and process them.
        
        Args:
            preferred_fields (Optional[List[str]]): List of preferred data fields
        
        Returns:
            pd.DataFrame: Processed transfer data
        """
        all_transfers = []
        
        for source in self.sources:
            try:
                transfers = source.fetch_transfers()
                if not transfers.empty:
                    all_transfers.append(transfers)
            except Exception as e:
                logger.warning(f"Error fetching from source {source.__class__.__name__}: {e}")
        
        if not all_transfers:
            logger.error("No transfer data retrieved from any source")
            return pd.DataFrame()
        
        # Combine transfers from all sources
        combined_df = pd.concat(all_transfers, ignore_index=True)
        
        # Clean and process data
        processed_df = self._clean_transfer_data(combined_df)
        
        # Filter preferred fields if specified
        if preferred_fields:
            available_fields = set(processed_df.columns)
            selected_fields = [field for field in preferred_fields if field in available_fields]
            if selected_fields:
                processed_df = processed_df[selected_fields]
        
        return processed_df
    
    def cache_transfers(self, df: pd.DataFrame, filename: str = 'transfers.json'):
        """
        Cache transfer data to JSON file.
        
        Args:
            df (pd.DataFrame): Transfer data to cache
            filename (str): Name of cache file
        """
        cache_path = os.path.join(self.cache_dir, filename)
        try:
            df.to_json(cache_path, orient='records')
            logger.info(f"Transfer data cached to {cache_path}")
        except Exception as e:
            logger.error(f"Error caching transfer data: {e}")
    
    def load_cached_transfers(self, filename: str = 'transfers.json') -> Optional[pd.DataFrame]:
        """
        Load cached transfer data.
        
        Args:
            filename (str): Name of cache file
        
        Returns:
            Optional[pd.DataFrame]: Cached transfer data or None
        """
        cache_path = os.path.join(self.cache_dir, filename)
        try:
            if os.path.exists(cache_path):
                df = pd.read_json(cache_path, orient='records')
                cache_time = datetime.fromtimestamp(os.path.getmtime(cache_path))
                
                # Check if cache is less than 24 hours old
                if datetime.now() - cache_time < timedelta(hours=24):
                    logger.info("Using cached transfer data")
                    return df
        except Exception as e:
            logger.error(f"Error loading cached transfer data: {e}")
        
        return None

def fetch_transfer_data(api_key: Optional[str] = None, preferred_fields: Optional[List[str]] = None) -> Optional[pd.DataFrame]:
    """
    High-level function to fetch transfer data.
    
    Args:
        api_key (Optional[str]): API key for football data source
        preferred_fields (Optional[List[str]]): List of preferred data fields
    
    Returns:
        Optional[pd.DataFrame]: Processed transfer data
    """
    try:
        # Use config API key if not provided
        key = api_key or Config.get_api_key()
        
        # Initialize sources
        sources = [
            FootballDataOrgSource(key),
            TransferMarketSource()
        ]
        
        # Create processor
        processor = TransferDataProcessor(sources)
        
        # Try loading cached data first
        cached_data = processor.load_cached_transfers()
        if cached_data is not None:
            return cached_data
        
        # Fetch and process transfers
        transfers = processor.fetch_and_process_transfers(preferred_fields)
        
        # Cache the transfers
        if not transfers.empty:
            processor.cache_transfers(transfers)
        
        return transfers
    
    except Exception as e:
        logger.error(f"Unexpected error in transfer data fetching: {e}")
        return None

# Example usage with comprehensive error handling
if __name__ == "__main__":
    try:
        # Example of fetching with specific preferred fields
        preferred_fields = ['player_name', 'previous_team', 'new_team']
        transfers = fetch_transfer_data(preferred_fields=preferred_fields)
        
        if transfers is not None and not transfers.empty:
            print("Transfer Data Preview:")
            print(transfers.head())
            
            # Save to CSV for further analysis
            transfers.to_csv('transfer_data.csv', index=False)
            logger.info("Transfer data saved to transfer_data.csv")
        else:
            logger.warning("No transfer data available.")
    
    except Exception as e:
        logger.error(f"Unexpected error in main block: {e}")
        print("An error occurred. Check the log for details.")
