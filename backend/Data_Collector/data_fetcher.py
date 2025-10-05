import requests
import pandas as pd
from datetime import datetime
from typing import Optional

class DataFetcher:
    def __init__(self):
        self.base_url = "https://power.larc.nasa.gov/api/temporal/hourly/point"
        self.parameters = [
            'PRECTOTCORR',
            'T2M',
            'RH2M',
            'PS',
            'WS10M',
        ]
        
    def fetch_data(
        self,
        latitude: float,
        longitude: float,
        start_date: str,
        end_date: str
    ) -> Optional[pd.DataFrame]:
        """
        Fetch weather data from NASA POWER API.
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            start_date: Start date in YYYYMMDD format
            end_date: End date in YYYYMMDD format
            
        Returns:
            DataFrame with weather data or None if fetch fails
        """
        params = {
            'parameters': ','.join(self.parameters),
            'community': 'RE',
            'longitude': longitude,
            'latitude': latitude,
            'start': start_date,
            'end': end_date,
            'format': 'JSON'
        }
        
        try:
            print(f"Fetching NASA data for ({latitude}, {longitude}) from {start_date} to {end_date}...")
            response = requests.get(self.base_url, params=params, timeout=60)
            response.raise_for_status()
            
            data = response.json()
            
            if 'properties' not in data or 'parameter' not in data['properties']:
                print("ERROR: Invalid response structure")
                return None
            
            # Convert to DataFrame
            param_data = data['properties']['parameter']
            df = pd.DataFrame(param_data)
            
            # Convert index to datetime
            df.index = pd.to_datetime(df.index, format='%Y%m%d%H')
            
            print(f"✓ Fetched {len(df)} rows with {len(df.columns)} parameters")
            return df
            
        except requests.exceptions.RequestException as e:
            print(f"ERROR fetching data: {e}")
            return None
        except Exception as e:
            print(f"ERROR processing data: {e}")
            return None