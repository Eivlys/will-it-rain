import pandas as pd
import json
import os

# Create raw_data folder if it doesn't exist
os.makedirs('../raw_data', exist_ok=True)

# Load Giovanni CSV
df = pd.read_csv('historical_data/waterloo_prec_data.csv', skiprows=8)
df.columns = df.columns.str.strip()

# Parse and convert
df['timestamp'] = pd.to_datetime(df['time'])
df['precipitation_mm'] = df['mean_M2T1NXFLX_5_12_4_PRECTOT'] * 3600

# Extract time components
df['month'] = df['timestamp'].dt.month
df['day'] = df['timestamp'].dt.day
df['hour'] = df['timestamp'].dt.hour

# Filter to Oct 5-12
df_filtered = df[
    ((df['month'] == 10) & (df['day'] >= 5) & (df['day'] <= 12))
]

# Calculate historical averages
averages = df_filtered.groupby(['month', 'day', 'hour'])['precipitation_mm'].mean().reset_index()

# Format as JSON
historical_data = []
for _, row in averages.iterrows():
    day = int(row['day'])
    hour = int(row['hour'])
    
    historical_data.append({
        'timestamp': f"2025-10-{day:02d}T{hour:02d}:00:00",
        'historical_avg_precipitation_mm': float(row['precipitation_mm'])
    })

# Write to raw_data folder
with open('../raw_data/waterloo_historical.json', 'w') as f:
    json.dump({'historical_baseline': historical_data}, f, indent=2)

print(f"Created raw_data/waterloo_historical.json with {len(historical_data)} records")