import os
import numpy as np
import pandas as pd
import joblib
from xgboost import XGBRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
from .features import build_features, FEATURE_COLS

XGB_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "xgb_forecast.json")
RF_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "rf_forecast.joblib")

def train_forecaster(df: pd.DataFrame, save: bool = True):
    feats = build_features(df)
    X, y = feats[FEATURE_COLS], feats["consumption_kwh"]
    
    split = int(len(feats) * 0.8)
    X_train, X_test = X.iloc[:split], X.iloc[split:]
    y_train, y_test = y.iloc[:split], y.iloc[split:]

    # 1. XGBoost
    print("Training XGBoost...")
    xgb_model = XGBRegressor(n_estimators=200, max_depth=5, learning_rate=0.05, random_state=42)
    xgb_model.fit(X_train, y_train)
    xgb_preds = xgb_model.predict(X_test)
    xgb_mae = mean_absolute_error(y_test, xgb_preds)
    xgb_rmse = float(np.sqrt(mean_squared_error(y_test, xgb_preds)))
    print(f"[XGBoost] MAE={xgb_mae:.3f}  RMSE={xgb_rmse:.3f}")

    # 2. Random Forest
    print("Training Random Forest...")
    rf_model = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42)
    rf_model.fit(X_train, y_train)
    rf_preds = rf_model.predict(X_test)
    rf_mae = mean_absolute_error(y_test, rf_preds)
    rf_rmse = float(np.sqrt(mean_squared_error(y_test, rf_preds)))
    print(f"[Random Forest] MAE={rf_mae:.3f}  RMSE={rf_rmse:.3f}")

    if save:
        os.makedirs(os.path.dirname(XGB_PATH), exist_ok=True)
        xgb_model.save_model(XGB_PATH)
        joblib.dump(rf_model, RF_PATH)
        print("✅ Saved XGBoost and Random Forest models.")

    return xgb_model, rf_model

# --- THIS WAS MISSING, CAUSING THE CRASH ---
_model_cache = None
def load_forecaster():
    global _model_cache
    if _model_cache is None:
        _model_cache = XGBRegressor()
        _model_cache.load_model(XGB_PATH)
    return _model_cache
# ------------------------------------------

def forecast_all_models(history_df: pd.DataFrame, horizon: int = 24) -> dict:
    df = history_df.sort_values("timestamp").copy()
    xgb_results = []
    rf_results = []

    # Load models
    xgb_model = XGBRegressor()
    xgb_model.load_model(XGB_PATH)
    rf_model = joblib.load(RF_PATH)

    for _ in range(horizon):
        feats = build_features(df)
        if feats.empty: break
        last_row = feats.iloc[[-1]]
        
        xgb_pred = float(xgb_model.predict(last_row[FEATURE_COLS])[0])
        rf_pred = float(rf_model.predict(last_row[FEATURE_COLS])[0])
        
        next_ts = pd.to_datetime(df["timestamp"].iloc[-1]) + pd.Timedelta(hours=1)
        
        df = pd.concat([df, pd.DataFrame([{
            "timestamp": next_ts, "consumption_kwh": xgb_pred, 
            "temperature_c": df["temperature_c"].iloc[-1], "humidity_pct": df["humidity_pct"].iloc[-1],
        }])], ignore_index=True)
        
        xgb_results.append({"timestamp": next_ts.isoformat(), "predicted_kwh": round(xgb_pred, 3)})
        rf_results.append({"timestamp": next_ts.isoformat(), "predicted_kwh": round(rf_pred, 3)})

    return {"xgb": xgb_results, "rf": rf_results}