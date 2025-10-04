from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import pandas as pd
from datetime import datetime

from Data_Collector.data_fetcher import DataFetcher
from Prediction_Modeller.prec_modeler import PrecipitationModel

app = FastAPI(title="Weather Prediction API")

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load trained model at startup
model = PrecipitationModel()
try:
    model.load('trained_precipitation_model.pkl')
    print("✓ Model loaded successfully")
except FileNotFoundError:
    print("⚠ No trained model found. Run train_and_save.py first!")

fetcher = DataFetcher()


class PredictionRequest(BaseModel):
    latitude: float
    longitude: float
    hours_ahead: int = 24


class PredictionResponse(BaseModel):
    predictions: List[dict]
    location: dict


@app.get("/")
def read_root():
    return {
        "message": "Weather Prediction API",
        "status": "Model loaded" if model.is_trained else "No model loaded",
        "endpoints": {
            "GET /": "API info",
            "GET /health": "Health check",
            "POST /predict": "Get precipitation predictions"
        }
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "model_loaded": model.is_trained,
        "timestamp": datetime.now().isoformat()
    }


@app.post("/predict", response_model=PredictionResponse)
def predict_precipitation(request: PredictionRequest):
    """Predict precipitation for the next N hours."""
    
    if not model.is_trained:
        raise HTTPException(status_code=503, detail="Model not trained")
    
    # Fetch recent data for the location
    from datetime import timedelta
    end_date = datetime.now()
    start_date = end_date - timedelta(days=2)
    
    df = fetcher.fetch_data(
        latitude=request.latitude,
        longitude=request.longitude,
        start_date=start_date.strftime('%Y%m%d'),
        end_date=end_date.strftime('%Y%m%d'),
    )
    
    if df is None or len(df) < 24:
        raise HTTPException(status_code=500, detail="Failed to fetch weather data")
    
    # Engineer features
    df_processed = model.engineer_features(df)
    
    if len(df_processed) == 0:
        raise HTTPException(status_code=500, detail="Insufficient data for prediction")
    
    # Use most recent data point for prediction
    X = df_processed.drop('PRECTOTCORR', axis=1).tail(1)
    
    # Make prediction
    prediction = model.predict(X)[0]
    
    # Generate response
    predictions = [{
        "timestamp": datetime.now().isoformat(),
        "precipitation_mm": round(max(0, prediction), 2),
        "probability": "high" if prediction > 0.5 else "low"
    }]
    
    return PredictionResponse(
        predictions=predictions,
        location={
            "latitude": request.latitude,
            "longitude": request.longitude
        }
    )


if __name__ == "__main__":
    import uvicorn