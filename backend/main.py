from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional
import requests
from Prediction_Modeller.prec_modeler import PrecipitationModel
from Data_Collector.data_fetcher import DataFetcher

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load trained model
model = PrecipitationModel()
try:
    model.load('trained_precipitation_model.pkl')
    print("✓ Model loaded successfully")
except Exception as e:
    print(f"⚠ Model load failed: {e}")

class PredictionRequest(BaseModel):
    latitude: float
    longitude: float
    target_time: str  # ISO format datetime (start time)
    end_time: Optional[str] = None  # Optional end time
    hours_ahead: Optional[int] = 24  # Default if no end_time

@app.get("/")
def root():
    return {"message": "Weather Prediction API", "status": "running"}

@app.post("/predict")
async def predict_weather(req: PredictionRequest):
    print(f"RECEIVED REQUEST: {req}")
    try:
        target_dt = datetime.fromisoformat(req.target_time.replace('Z', '+00:00'))
        print(f"Parsed target_dt: {target_dt}")
        now = datetime.now()
        print(f"Now: {now}, Is past? {target_dt < now}")
        
        # Calculate hours_ahead from end_time if provided
        if req.end_time:
            end_dt = datetime.fromisoformat(req.end_time.replace('Z', '+00:00'))
            hours_ahead = int((end_dt - target_dt).total_seconds() / 3600)
            hours_ahead = max(1, min(hours_ahead, 72))  # Limit to 1-72 hours
            print(f"Calculated hours_ahead from end_time: {hours_ahead}")
        else:
            hours_ahead = req.hours_ahead

        # Past date = historical lookup
        if target_dt < now:
            return await get_historical(req.latitude, req.longitude, target_dt)
        
        # Future date = ML prediction
        else:
            return await get_prediction(req.latitude, req.longitude, target_dt, hours_ahead)
            
    except Exception as e:
        print(f"ERROR in predict_weather: {e}")
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
    
    if df is None or len(df) < 24:
        raise HTTPException(status_code=503, detail="Insufficient data for LSTM prediction (need 24+ hours)")
    
    # Engineer features
    print("Engineering features...")
    df_eng = model.engineer_features(df)
    print(f"Engineered features: {len(df_eng)} rows, {len(df_eng.columns)} columns")
    
    if len(df_eng) < 24:
        raise HTTPException(status_code=503, detail="Feature engineering produced insufficient data")
    
    # LSTM needs sequence of data
    X_latest = df_eng.drop('PRECTOTCORR', axis=1) if 'PRECTOTCORR' in df_eng.columns else df_eng
    print(f"X_latest shape: {X_latest.shape}")
    
    # Make predictions
    results = []
    for i in range(min(hours, 24)):
        pred_time = target_dt + timedelta(hours=i)
        
        # Predict with uncertainty quantification
        precip_mean, precip_std = model.predict(X_latest, n_samples=50)
        precip_pred = max(0, float(precip_mean))
        
        # Calculate confidence: lower std = higher confidence
        confidence = max(50, min(95, 95 - (precip_std * 9)))
        
        # Classify type and intensity
        temp = current.get('temperature', 10)
        precip_type = model.classify_precip_type(temp, precip_pred)
        intensity = model.classify_intensity(precip_pred, precip_type)
        
        results.append({
            "timestamp": pred_time.isoformat(),
            "precipitation_mm": round(float(precip_pred), 2),
            "precipitation_std": round(float(precip_std), 2),
            "confidence_percent": round(float(confidence), 0),
            "type": precip_type,
            "intensity": intensity,
            "temperature_c": round(float(temp), 1),
            "is_historical": False
        })
    
    print(f"Returning {len(results)} predictions")
    return {"predictions": results, "location": {"latitude": lat, "longitude": lon}}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
