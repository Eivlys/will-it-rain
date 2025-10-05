import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Data_Collector.data_fetcher import DataFetcher
from Prediction_Modeller.prec_modeler import PrecipitationModel
import pandas as pd

print("=" * 50)
print("TRAINING IMPROVED PRECIPITATION MODEL")
print("=" * 50)

# Multiple locations for diverse training data
locations = [
    {"name": "Waterloo", "lat": 43.4643, "lon": -80.5204},
    {"name": "Toronto", "lat": 43.6532, "lon": -79.3832},
    {"name": "Vancouver", "lat": 49.2827, "lon": -123.1207},
    {"name": "Montreal", "lat": 45.5017, "lon": -73.5673},
]

# Fetch 5 years of data
print("\n1. Fetching 5 years of data from multiple locations...")
fetcher = DataFetcher()
all_data = []

for loc in locations:
    print(f"   Fetching {loc['name']}...")
    df = fetcher.fetch_data(
        latitude=loc['lat'],
        longitude=loc['lon'],
        start_date='20200101',
        end_date='20241231',
    )
    if df is not None and len(df) > 0:
        all_data.append(df)
        print(f"   ✓ {loc['name']}: {len(df)} rows")

if len(all_data) == 0:
    print("ERROR: Failed to fetch data")
    exit(1)

# Combine all data
df_combined = pd.concat(all_data, ignore_index=False)
print(f"\n   ✓ Total: {len(df_combined)} rows from {len(all_data)} locations")

# Engineer features
print("\n2. Engineering features...")
model = PrecipitationModel()
df_engineered = model.engineer_features(df_combined)
print(f"   ✓ Final dataset: {len(df_engineered)} rows, {len(df_engineered.columns)} features")

# Prepare training data
X = df_engineered.drop('PRECTOTCORR', axis=1)
y = df_engineered['PRECTOTCORR']

print(f"\n3. Training improved model...")
print(f"   Features: {list(X.columns)}")
metrics = model.train(X, y)

print(f"\n4. Saving model...")
model.save('trained_precipitation_model.pkl')

print("\n" + "=" * 50)
print("TRAINING COMPLETE!")
print(f"R² Score: {metrics['r2_score']:.3f}")
print(f"MSE: {metrics['mse']:.3f}")
print(f"Training samples: {len(X)}")
print("=" * 50)