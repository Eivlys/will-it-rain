import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import pickle
import os
from typing import Dict, Optional


class PrecipitationModel:
    """ML model for predicting precipitation."""
    
    def __init__(self):
        self.model = None
        self.is_trained = False
        self.feature_names = None
    
    def engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add time-based and derived features."""
        df = df.copy()
        
        # Time features
        df['hour'] = df.index.hour
        df['day_of_year'] = df.index.dayofyear
        df['month'] = df.index.month
        
        # Lagged features (previous values)
        for col in ['T2M', 'RH2M', 'PS', 'WS10M']:
            if col in df.columns:
                df[f'{col}_lag1'] = df[col].shift(1)
                df[f'{col}_lag6'] = df[col].shift(6)
        
        # Rolling averages
        for col in ['T2M', 'RH2M']:
            if col in df.columns:
                df[f'{col}_roll6'] = df[col].rolling(window=6).mean()
        
        df = df.dropna()
        return df
    
    def train(self, X: pd.DataFrame, y: pd.Series, test_size: float = 0.2) -> Dict:
        """Train the model."""
        if len(X) == 0:
            raise ValueError("No features provided for training")
        
        self.feature_names = X.columns.tolist()
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42
        )
        
        self.model = RandomForestRegressor(
            n_estimators=200,
            max_depth=15,
            min_samples_split=5,
            random_state=42,
            n_jobs=-1
        )
        
        self.model.fit(X_train, y_train)
        self.is_trained = True
        
        y_pred = self.model.predict(X_test)
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        print(f"Model trained! R² Score: {r2:.3f}, MSE: {mse:.3f}")
        
        return {
            'mse': mse,
            'r2_score': r2,
            'train_size': len(X_train),
            'test_size': len(X_test)
        }
    
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Make predictions."""
        if not self.is_trained:
            raise ValueError("Model not trained yet")
        
        # Ensure same features
        missing = set(self.feature_names) - set(X.columns)
        if missing:
            raise ValueError(f"Missing features: {missing}")
        
        return self.model.predict(X[self.feature_names])
    
    def save(self, filepath: str = 'trained_model.pkl'):
        """Save model to file."""
        if not self.is_trained:
            raise ValueError("No trained model to save")
        
        with open(filepath, 'wb') as f:
            pickle.dump({
                'model': self.model,
                'feature_names': self.feature_names
            }, f)
        print(f"Model saved to {filepath}")
    
    def load(self, filepath: str = 'trained_model.pkl'):
        """Load model from file."""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Model file not found: {filepath}")
        
        with open(filepath, 'rb') as f:
            data = pickle.load(f)
            self.model = data['model']
            self.feature_names = data['feature_names']
            self.is_trained = True
        print(f"Model loaded from {filepath}")

