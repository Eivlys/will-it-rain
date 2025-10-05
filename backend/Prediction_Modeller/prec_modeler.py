import numpy as np
import pandas as pd
from tensorflow import keras
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score
import pickle
import os
from typing import Dict, Optional


class PrecipitationModel:
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.is_trained = False
        self.feature_names = None
        self.sequence_length = 24  # Use last 24 hours to predict next hour
        
    def engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        
        # Time-based features
        df['hour'] = df.index.hour
        df['day_of_year'] = df.index.dayofyear
        df['month'] = df.index.month
        
        # Lagged features
        for feature in ['T2M', 'RH2M', 'PS', 'WS10M']:
            df[f'{feature}_lag1'] = df[feature].shift(1)
            df[f'{feature}_lag6'] = df[feature].shift(6)
        
        # Rolling averages
        for feature in ['T2M', 'RH2M', 'PS']:
            df[f'{feature}_roll6'] = df[feature].rolling(window=6).mean()
        
        # Drop NaN
        df = df.dropna()
        
        return df
    
    def create_sequences(self, X, y):
        """Create sequences for LSTM input"""
        X_seq, y_seq = [], []
        for i in range(len(X) - self.sequence_length):
            X_seq.append(X[i:i + self.sequence_length])
            y_seq.append(y[i + self.sequence_length])
        return np.array(X_seq), np.array(y_seq)
    
    def train(self, X: pd.DataFrame, y: pd.Series) -> Dict:
        self.feature_names = list(X.columns)
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Create sequences
        print(f"Creating sequences with length {self.sequence_length}...")
        X_seq, y_seq = self.create_sequences(X_scaled, y.values)
        
        print(f"Sequence shape: {X_seq.shape}")
        
        # Train/test split
        X_train, X_test, y_train, y_test = train_test_split(
            X_seq, y_seq, test_size=0.2, random_state=42
        )
        
        # Build LSTM model
        print("Building LSTM model...")
        self.model = Sequential([
            LSTM(128, return_sequences=True, input_shape=(self.sequence_length, len(self.feature_names))),
            Dropout(0.2),
            LSTM(64, return_sequences=False),
            Dropout(0.2),
            Dense(32, activation='relu'),
            Dense(1)
        ])
        
        self.model.compile(optimizer='adam', loss='mse', metrics=['mae'])
        
        print(f"Training LSTM on {len(X_train)} sequences...")
        history = self.model.fit(
            X_train, y_train,
            epochs=50,
            batch_size=64,
            validation_split=0.1,
            verbose=1
        )
        
        # Evaluate
        y_pred = self.model.predict(X_test)
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        self.is_trained = True
        
        return {
            'mse': mse,
            'r2_score': r2,
            'train_samples': len(X_train),
            'test_samples': len(X_test)
        }
    
    def predict(self, X: pd.DataFrame, n_samples=50) -> tuple:
        """
        Make prediction with uncertainty estimate using Monte Carlo Dropout.
        
        Args:
            X: Feature dataframe
            n_samples: Number of forward passes for uncertainty estimation
            
        Returns:
            tuple: (mean_prediction, std_prediction)
        """
        if not self.is_trained:
            raise ValueError("Model not trained")
        
        X_scaled = self.scaler.transform(X)
        
        if len(X_scaled) < self.sequence_length:
            raise ValueError(f"Need at least {self.sequence_length} rows for prediction")
        
        X_seq = X_scaled[-self.sequence_length:].reshape(1, self.sequence_length, -1)
        
        # Monte Carlo Dropout: run prediction multiple times with dropout enabled
        predictions = []
        for _ in range(n_samples):
            # training=True keeps dropout active during inference
            pred = self.model(X_seq, training=True)
            predictions.append(pred.numpy()[0][0])
        
        mean_pred = np.mean(predictions)
        std_pred = np.std(predictions)
        
        return mean_pred, std_pred
    
    def save(self, filepath: str):
    # Save as .keras format instead of .h5
        self.model.save(filepath.replace('.pkl', '_lstm.keras'))
        with open(filepath, 'wb') as f:
            pickle.dump({
                'scaler': self.scaler,
                'feature_names': self.feature_names,
                'sequence_length': self.sequence_length,
                'is_trained': True
            }, f)
        print(f"Model saved to {filepath}")

    def load(self, filepath: str):
        # Try .keras first, fall back to .h5
        keras_path = filepath.replace('.pkl', '_lstm.keras')
        h5_path = filepath.replace('.pkl', '_lstm.h5')
    
        if os.path.exists(keras_path):
            self.model = keras.models.load_model(keras_path)
        elif os.path.exists(h5_path):
            self.model = keras.models.load_model(h5_path, compile=False)
            # Recompile with compatible metrics
            self.model.compile(optimizer='adam', loss='mse', metrics=['mae'])
        else:
            raise FileNotFoundError(f"No model file found at {keras_path} or {h5_path}")
    
        with open(filepath, 'rb') as f:
            data = pickle.load(f)
        self.scaler = data['scaler']
        self.feature_names = data['feature_names']
        self.sequence_length = data['sequence_length']
        self.is_trained = True
        print(f"Model loaded from {filepath}")
    
    def classify_precip_type(self, temp: float, precip_amount: float) -> str:
        if precip_amount < 0.1:
            return 'none'
        elif temp < -2:
            return 'snow'
        elif temp < 2:
            return 'mixed'
        else:
            return 'rain'
    
    def classify_intensity(self, precip_amount: float, precip_type: str) -> str:
        if precip_amount < 0.1:
            return 'none'
        elif precip_type == 'snow':
            if precip_amount < 1:
                return 'light'
            elif precip_amount < 5:
                return 'moderate'
            else:
                return 'heavy'
        else:
            if precip_amount < 2.5:
                return 'light'
            elif precip_amount < 7.5:
                return 'moderate'
            else:
                return 'heavy'