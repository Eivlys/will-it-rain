import pandas as pd
from datetime import datetime, timedelta
import os

def load_giovanni_csv(filepath: str, start_date: str, end_date: str) -> pd.DataFrame:
    """
    Load and process Giovanni MERRA-2 CSV file.
    """
    # Skip the metadata header lines (first 8 lines)
    df = pd.read_csv(filepath, skiprows=8)
    
    # Strip whitespace from column names
    df.columns = df.columns.str.strip()
    
    # Parse timestamps
    df['timestamp'] = pd.to_datetime(df['time'])
    
    # Convert precipitation from kg/m²/s to mm/hour
    precip_col = 'mean_M2T1NXFLX_5_12_4_PRECTOT'
    df['precipitation_mm'] = df[precip_col] * 3600
    
    # Extract time components
    df['year'] = df['timestamp'].dt.year
    df['month'] = df['timestamp'].dt.month
    df['day'] = df['timestamp'].dt.day
    df['hour'] = df['timestamp'].dt.hour
    
    # Filter to requested date range (any year)
    start_dt = datetime.strptime(start_date, '%Y-%m-%d')
    end_dt = datetime.strptime(end_date, '%Y-%m-%d')
    
    df_filtered = df[
        ((df['month'] == start_dt.month) & (df['day'] >= start_dt.day)) |
        ((df['month'] > start_dt.month) & (df['month'] < end_dt.month)) |
        ((df['month'] == end_dt.month) & (df['day'] <= end_dt.day))
    ]
    
    return df_filtered[['timestamp', 'precipitation_mm', 'year', 'month', 'day', 'hour']]


def fetch_giovanni_historical_average(latitude: float, longitude: float,
                                      start_date: str, end_date: str,
                                      years_back: int = 5) -> pd.DataFrame:
    """
    Fetch historical precipitation from Giovanni CSV for Waterloo only.
    """
    
    start_dt = datetime.strptime(start_date, '%Y-%m-%d')
    end_dt = datetime.strptime(end_date, '%Y-%m-%d')
    
    # Load Giovanni CSV
    waterloo_csv = os.path.join('historical_data', 'waterloo_prec_data.csv')
    
    print("Loading Giovanni CSV for Waterloo...")
    df = load_giovanni_csv(waterloo_csv, start_date, end_date)
    
    if df.empty:
        raise Exception("No data found in Giovanni CSV")
    
    print(f"  Loaded {len(df)} records from Giovanni CSV")
    
    # Calculate averages across all years
    averages = df.groupby(['month', 'day', 'hour'])['precipitation_mm'].mean().reset_index()
    averages.rename(columns={'precipitation_mm': 'historical_avg_precipitation_mm'}, inplace=True)
    
    # Format for target year
    result_data = []
    current_dt = start_dt
    while current_dt <= end_dt:
        for hour in range(24):
            timestamp = current_dt.replace(hour=hour, minute=0, second=0)
            
            avg_row = averages[
                (averages['month'] == timestamp.month) &
                (averages['day'] == timestamp.day) &
                (averages['hour'] == timestamp.hour)
            ]
            
            if not avg_row.empty:
                result_data.append({
                    'timestamp': timestamp.isoformat(),
                    'historical_avg_precipitation_mm': float(avg_row.iloc[0]['historical_avg_precipitation_mm'])
                })
        
        current_dt += timedelta(days=1)
    
    return pd.DataFrame(result_data)