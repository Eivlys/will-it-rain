import pandas as pd
import requests
from datetime import datetime, timedelta

def fetch_datarods_year(latitude: float, longitude: float, start_date: str, end_date: str) -> pd.DataFrame:
    """
    Try to fetch from NASA Data Rods API.
    Returns empty DataFrame if it fails.
    """
    base_url = "http://hydro1.sci.gsfc.nasa.gov/daac-bin/access/timeseries.cgi"
    
    # Try different variable formats
    variable_formats = [
        'NLDAS_FORA0125_H.002:APCPsfc',
        'NLDAS_FORA0125_H_2.0:APCPsfc',
        'NLDAS_FORA0125_H:APCPsfc',
        'APCPsfc'
    ]
    
    for var_format in variable_formats:
        params = {
            'type': 'asc2',
            'location': f'GEOM:POINT({longitude}, {latitude})',
            'variable': var_format,
            'startDate': start_date + 'T00:00:00Z',
            'endDate': end_date + 'T23:00:00Z'
        }
        
        try:
            response = requests.get(base_url, params=params, timeout=30)
            
            if response.status_code == 200 and 'ERROR' not in response.text and '<html>' not in response.text:
                lines = response.text.strip().split('\n')
                data_lines = [line for line in lines if not line.startswith('#') and line.strip()]
                
                if data_lines:
                    records = []
                    for line in data_lines:
                        parts = line.split()
                        if len(parts) >= 2:
                            try:
                                timestamp = datetime.fromisoformat(parts[0].replace('Z', ''))
                                precip = float(parts[1])
                                records.append({
                                    'timestamp': timestamp,
                                    'precipitation_mm': precip,
                                    'year': timestamp.year,
                                    'month': timestamp.month,
                                    'day': timestamp.day,
                                    'hour': timestamp.hour
                                })
                            except:
                                continue
                    
                    if records:
                        print(f"  ✓ Data Rods succeeded")
                        return pd.DataFrame(records)
        except:
            continue
    
    return pd.DataFrame()


def fetch_nasa_power_year(latitude: float, longitude: float, start_date: str, end_date: str) -> pd.DataFrame:
    """
    Fetch from NASA POWER API as fallback.
    """
    base_url = "https://power.larc.nasa.gov/api/temporal/hourly/point"
    
    params = {
        'parameters': 'PRECTOTCORR',
        'community': 'RE',
        'longitude': longitude,
        'latitude': latitude,
        'start': start_date.replace('-', ''),
        'end': end_date.replace('-', ''),
        'format': 'JSON'
    }
    
    try:
        response = requests.get(base_url, params=params, timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            precip_data = data['properties']['parameter']['PRECTOTCORR']
            
            records = []
            for timestamp_str, precip_value in precip_data.items():
                dt = datetime.strptime(timestamp_str, '%Y%m%d%H')
                records.append({
                    'timestamp': dt,
                    'precipitation_mm': precip_value if precip_value >= 0 else 0.0,
                    'year': dt.year,
                    'month': dt.month,
                    'day': dt.day,
                    'hour': dt.hour
                })
            
            return pd.DataFrame(records)
    except:
        pass
    
    return pd.DataFrame()


def fetch_datarods_historical_average(latitude: float, longitude: float,
                                     start_date: str, end_date: str,
                                     years_back: int = 5) -> pd.DataFrame:
    """
    Fetch historical precipitation: Data Rods primary, NASA POWER fallback.
    """
    
    start_dt = datetime.strptime(start_date, '%Y-%m-%d')
    end_dt = datetime.strptime(end_date, '%Y-%m-%d')
    
    all_historical_data = []
    use_fallback = False
    
    for year_offset in range(1, years_back + 1):
        historical_year = start_dt.year - year_offset
        hist_start = start_dt.replace(year=historical_year)
        hist_end = end_dt.replace(year=historical_year)
        
        print(f"Fetching historical data for {historical_year}...")
        
        hist_start_str = hist_start.strftime('%Y-%m-%d')
        hist_end_str = hist_end.strftime('%Y-%m-%d')
        
        # Try Data Rods first (only if we haven't switched to fallback)
        if not use_fallback:
            year_data = fetch_datarods_year(latitude, longitude, hist_start_str, hist_end_str)
            
            if year_data.empty:
                print(f"  Data Rods failed, switching to NASA POWER fallback")
                use_fallback = True
            else:
                all_historical_data.append(year_data)
                print(f"  Got {len(year_data)} records from Data Rods")
                continue
        
        # Use NASA POWER fallback
        if use_fallback:
            year_data = fetch_nasa_power_year(latitude, longitude, hist_start_str, hist_end_str)
            
            if not year_data.empty:
                all_historical_data.append(year_data)
                print(f"  Got {len(year_data)} records from NASA POWER")
            else:
                print(f"  Both APIs failed for {historical_year}")
    
    if not all_historical_data:
        raise Exception("Failed to fetch historical data from any source")
    
    combined_df = pd.concat(all_historical_data, ignore_index=True)
    
    averages = combined_df.groupby(['month', 'day', 'hour'])['precipitation_mm'].mean().reset_index()
    averages.rename(columns={'precipitation_mm': 'historical_avg_precipitation_mm'}, inplace=True)
    
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