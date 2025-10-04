from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime, timedelta
import requests
from Prediction_Modeller.prec_modeler import PrecipitationModel
from Data_Collector.data_fetcher import DataFetcher
import pickle

app = FastAPI()

# Load trained model
# Load trained model - REPLACE THIS SECTION
# Load trained model - REPLACE THE ENTIRE TRY/EXCEPT BLOCK
# At the top after imports, REPLACE the model loading section:
model = PrecipitationModel()
try:
    model.load('trained_precipitation_model.pkl')
    print("✓ Model loaded successfully")
except Exception as e:
    print(f"⚠ Model load failed: {e}")

class PredictionRequest(BaseModel):
    latitude: float
    longitude: float
    target_time: str  # ISO format datetime
    hours_ahead: int = 24

@app.get("/")
def root():
    return {"message": "Weather Prediction API", "status": "running"}

@app.post("/predict")
async def predict_weather(req: PredictionRequest):
    print(f"RECEIVED REQUEST: {req}")  # ADD THIS
    try:
        target_dt = datetime.fromisoformat(req.target_time.replace('Z', '+00:00'))
        print(f"Parsed target_dt: {target_dt}")  # ADD THIS
        now = datetime.now()
        print(f"Now: {now}, Is past? {target_dt < now}")  # ADD THIS

        # Past date = historical lookup
        if target_dt < now:
            return await get_historical(req.latitude, req.longitude, target_dt)
        
        # Future date = ML prediction
        else:
            return await get_prediction(req.latitude, req.longitude, target_dt, req.hours_ahead)
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def get_historical(lat, lon, target_dt):
    """Fetch actual historical weather data."""
    fetcher = DataFetcher()
    date_str = target_dt.strftime('%Y%m%d')
    
    df = fetcher.fetch_data(lat, lon, date_str, date_str)
    
    if df is None or len(df) == 0:
        raise HTTPException(status_code=404, detail="No historical data found")
    
    results = []
    for idx, row in df.iterrows():
        precip_type = model.classify_precip_type(row.get('T2M', 5), row['PRECTOTCORR'])
        intensity = model.classify_intensity(row['PRECTOTCORR'], precip_type)
        
        results.append({
            "timestamp": idx.isoformat(),
            "precipitation_mm": float(row['PRECTOTCORR']),
            "type": precip_type,
            "intensity": intensity,
            "temperature_c": float(row.get('T2M', 0)),
            "is_historical": True
        })
    
    return {"predictions": results, "location": {"latitude": lat, "longitude": lon}}

async def get_prediction(lat, lon, target_dt, hours):
    """Make ML prediction for future weather."""
    print(f"ENTERING get_prediction for {lat},{lon}")
    
    # Get current weather from Node service
    try:
        print("Calling Node service...")
        response = requests.post(
            'http://localhost:3001/api/current-weather',
            json={"latitude": lat, "longitude": lon},
            timeout=5
        )
        current = response.json()
        print(f"Node service response: {current}")
    except Exception as e:
        print(f"Node service failed: {e}")
        # Fallback to NASA if Node service fails
        fetcher = DataFetcher()
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')
        df = fetcher.fetch_data(lat, lon, yesterday, yesterday)
        if df is not None and len(df) > 0:
            current = {
                "temperature": df['T2M'].iloc[-1],
                "humidity": df['RH2M'].iloc[-1],
                "wind_speed": df['WS10M'].iloc[-1],
                "precipitation": 0
            }
        else:
            raise HTTPException(status_code=503, detail="Weather data unavailable")
    
    # Fetch recent data for feature engineering
    print("Fetching recent NASA data...")
    fetcher = DataFetcher()
    start = (datetime.now() - timedelta(days=2)).strftime('%Y%m%d')
    end = datetime.now().strftime('%Y%m%d')
    df = fetcher.fetch_data(lat, lon, start, end)
    print(f"Fetched {len(df) if df is not None else 0} rows")
    
    if df is None or len(df) < 10:
        raise HTTPException(status_code=503, detail="Insufficient data for prediction")
    
    # Engineer features
    print("Engineering features...")
    df_eng = model.engineer_features(df)
    print(f"Engineered features: {len(df_eng)} rows, {len(df_eng.columns)} columns")
    
    if len(df_eng) == 0:
        raise HTTPException(status_code=503, detail="Feature engineering failed")
    
    # Use most recent data point as base
    X_latest = df_eng.drop('PRECTOTCORR', axis=1).iloc[-1:] if 'PRECTOTCORR' in df_eng.columns else df_eng.iloc[-1:]
    print(f"X_latest shape: {X_latest.shape}")
    
    # Make predictions
    results = []
    for i in range(min(hours, 24)):
        pred_time = target_dt + timedelta(hours=i)
        
        # Predict precipitation amount
        precip_pred = model.predict(X_latest)[0]
        precip_pred = max(0, precip_pred)  # No negative precipitation
        
        # Classify type and intensity
        temp = current.get('temperature', 10)
        precip_type = model.classify_precip_type(temp, precip_pred)
        intensity = model.classify_intensity(precip_pred, precip_type)
        
        results.append({
            "timestamp": pred_time.isoformat(),
            "precipitation_mm": round(float(precip_pred), 2),
            "type": precip_type,
            "intensity": intensity,
            "temperature_c": round(temp, 1),
            "is_historical": False
        })
    
    print(f"Returning {len(results)} predictions")
    return {"predictions": results, "location": {"latitude": lat, "longitude": lon}}