import pandas as pd
import numpy as np
from xgboost import XGBRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import GridSearchCV, TimeSeriesSplit
from sklearn.metrics import mean_absolute_error
from app.features import build_features, FEATURE_COLS
import joblib
import os

def tune_models():
    print("Loading data...")
    df = pd.read_csv("data/consumption.csv", parse_dates=["timestamp"])
    feats = build_features(df)
    X = feats[FEATURE_COLS]
    y = feats["consumption_kwh"]

    # Use TimeSeriesSplit for time-series data (prevents data leakage)
    tscv = TimeSeriesSplit(n_splits=3)

    # --- 1. Tune XGBoost ---
    print("Tuning XGBoost (this might take a minute)...")
    xgb_param_grid = {
        'n_estimators': [100, 200],
        'max_depth': [3, 5, 7],
        'learning_rate': [0.01, 0.05, 0.1]
    }
    xgb = XGBRegressor(random_state=42)
    xgb_grid = GridSearchCV(xgb, xgb_param_grid, cv=tscv, scoring='neg_mean_absolute_error', n_jobs=-1)
    xgb_grid.fit(X, y)
    
    print(f"Best XGBoost Params: {xgb_grid.best_params_}")
    print(f"Best XGBoost MAE: {-xgb_grid.best_score_:.3f}")
    
    # Save the best XGBoost model
    os.makedirs("models", exist_ok=True)
    xgb_grid.best_estimator_.save_model("models/xgb_forecast.json")
    print("✅ Saved tuned XGBoost model")

    # --- 2. Tune Random Forest ---
    print("\nTuning Random Forest...")
    rf_param_grid = {
        'n_estimators': [50, 100],
        'max_depth': [5, 10, 15],
        'min_samples_split': [2, 5]
    }
    rf = RandomForestRegressor(random_state=42)
    rf_grid = GridSearchCV(rf, rf_param_grid, cv=tscv, scoring='neg_mean_absolute_error', n_jobs=-1)
    rf_grid.fit(X, y)
    
    print(f"Best RF Params: {rf_grid.best_params_}")
    print(f"Best RF MAE: {-rf_grid.best_score_:.3f}")
    
    # Save the best Random Forest model
    joblib.dump(rf_grid.best_estimator_, "models/rf_forecast.joblib")
    print("✅ Saved tuned Random Forest model")

if __name__ == "__main__":
    tune_models()