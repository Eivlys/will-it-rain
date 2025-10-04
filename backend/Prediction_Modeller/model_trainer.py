import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Data_Collector.data_fetcher import DataFetcher
from Prediction_Modeller.prec_modeler import PrecipitationModel

print("=" * 50)
print("TRAINING PRECIPITATION MODEL")
print("=" * 50)

# Fetch training data
print("\n1. Fetching 2 years of NASA data...")
fetcher = DataFetcher()
df = fetcher.fetch_data(
    latitude=43.4643,
    longitude=-80.5204,
    start_date='20230101',
    end_date='20241231',
)

if df is None or len(df) == 0:
    print("ERROR: Failed to fetch data")
    exit(1)

print(f"   ✓ Fetched {len(df)} rows")
print(f"   ✓ Features: {list(df.columns)}")

# Engineer features
print("\n2. Engineering features...")
model = PrecipitationModel()
df_engineered = model.engineer_features(df)
print(f"   ✓ Final dataset: {len(df_engineered)} rows, {len(df_engineered.columns)} features")

# Prepare training data
X = df_engineered.drop('PRECTOTCORR', axis=1)
y = df_engineered['PRECTOTCORR']

print(f"\n3. Training model...")
print(f"   Features: {list(X.columns)}")
metrics = model.train(X, y)

print(f"\n4. Saving model...")
model.save('trained_precipitation_model.pkl')

print("\n" + "=" * 50)
print("TRAINING COMPLETE!")
print(f"R² Score: {metrics['r2_score']:.3f}")
print(f"MSE: {metrics['mse']:.3f}")
print("=" * 50)
