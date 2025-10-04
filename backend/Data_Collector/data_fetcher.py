import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import  Dict, List, Optional
import os
from dotenv import load_dotenv 

load_dotenv()
class DataFetcher:
    def __init__(self):
        self.base_url = "https://power.larc.nasa.gov/api/temporal/"
        self.api_key = os.getenv("NASA_API_KEY", "DEMO_KEY")
    def fetch_data(self, latitude, longitude, start_date, end_date, parameters=None):
        if parameters is None:
            parameters = [
                'PRECTOTCORR',  # Precipitation
                'T2M',           # Temperature at 2m
                'RH2M',          # Relative Humidity
                'PS',            # Surface Pressure
                'WS10M',         # Wind Speed at 10m
                'CLOUD_AMT',     # Cloud Amount
            ]
        params = {
            'parameters': ','.join(parameters),
            'community': 'RE',
            'longitude': longitude,
            'latitude': latitude,
            'start': start_date,
            'end': end_date,
            'format': 'JSON',
        }
        url = f"{self.base_url}hourly/point"

        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
    
            df_dict = {}
            for param in parameters:
                if param in data['properties']['parameter']:
                    df_dict[param] = data['properties']['parameter'][param]

# Create DataFrame
            df = pd.DataFrame(df_dict)
            df.index = pd.to_datetime(df.index, format='%Y%m%d%H')

            return df    
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data: {e}")
            return None 
        

