
import os
import numpy as np
import pandas as pd
import joblib

from xgboost import XGBRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error

from .features import build_features, FEATURE_COLS
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_DIR = os.path.join(BASE_DIR, "models")

XGB_PATH = os.path.join(MODEL_DIR, "xgb_forecast.json")
RF_PATH = os.path.join(MODEL_DIR, "rf_forecast.joblib")

_model_cache = None


def prepare_features(df):
    df = df.copy()

    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp").reset_index(drop=True)

    feats = build_features(df)

    required_cols = FEATURE_COLS + ["consumption_kwh"]

    feats = feats.replace([np.inf, -np.inf], np.nan)
    feats = feats.dropna(subset=required_cols).reset_index(drop=True)

    if feats.empty:
        raise ValueError("No valid records available after feature processing.")

    return feats


def train_forecaster(df: pd.DataFrame, save: bool = True):

    print("Preparing real electricity consumption data...")

    feats = prepare_features(df)

    X = feats[FEATURE_COLS]
    y = feats["consumption_kwh"]

    # Chronological 80:20 split
    split = int(len(feats) * 0.8)

    X_train = X.iloc[:split]
    X_test = X.iloc[split:]

    y_train = y.iloc[:split]
    y_test = y.iloc[split:]

    if len(X_train) == 0 or len(X_test) == 0:
        raise ValueError("Not enough data for an 80:20 split.")

    print(f"Training records: {len(X_train)}")
    print(f"Testing records: {len(X_test)}")

    # 1. XGBoost
    print("\nTraining XGBoost...")

    xgb_model = XGBRegressor(
        n_estimators=200,
        max_depth=5,
        learning_rate=0.05,
        random_state=42
    )

    xgb_model.fit(X_train, y_train)

    xgb_preds = xgb_model.predict(X_test)

    # Calculate R2 score
    xgb_r2 = r2_score(y_test, xgb_preds)

    # Calculate MAPE
    non_zero = y_test != 0

    mape = np.mean(
        np.abs(
            (y_test[non_zero] - xgb_preds[non_zero])
            / y_test[non_zero]
        )
    ) * 100

    accuracy = 100 - mape

    print(f"R2 Score: {xgb_r2:.4f}")
    print(f"MAPE: {mape:.2f}%")
    print(f"MAPE-based accuracy: {accuracy:.2f}%")

    xgb_mae = mean_absolute_error(y_test, xgb_preds)
    xgb_rmse = np.sqrt(mean_squared_error(y_test, xgb_preds))

    print(f"[XGBoost] MAE = {xgb_mae:.3f}")
    print(f"[XGBoost] RMSE = {xgb_rmse:.3f}")

    # 2. Random Forest
    print("\nTraining Random Forest...")

    rf_model = RandomForestRegressor(
        n_estimators=100,
        max_depth=10,
        random_state=42,
        n_jobs=-1
    )

    rf_model.fit(X_train, y_train)

    rf_preds = rf_model.predict(X_test)

    rf_mae = mean_absolute_error(y_test, rf_preds)
    rf_rmse = np.sqrt(mean_squared_error(y_test, rf_preds))

    print(f"[Random Forest] MAE = {rf_mae:.3f}")
    print(f"[Random Forest] RMSE = {rf_rmse:.3f}")

    # Save models trained only on the first 80%
    if save:

        os.makedirs(MODEL_DIR, exist_ok=True)

        xgb_model.save_model(XGB_PATH)
        joblib.dump(rf_model, RF_PATH)

        print("\nModels saved successfully.")

    return xgb_model, rf_model


def load_forecaster():

    global _model_cache

    if _model_cache is None:

        if not os.path.exists(XGB_PATH):
            raise FileNotFoundError(
                "XGBoost model not found. Run train.py first."
            )

        _model_cache = XGBRegressor()
        _model_cache.load_model(XGB_PATH)

    return _model_cache


def forecast_all_models(history_df: pd.DataFrame, horizon: int = 24):

    if not os.path.exists(XGB_PATH) or not os.path.exists(RF_PATH):
        raise FileNotFoundError("Train both models before forecasting.")

    df = history_df.sort_values("timestamp").copy()

    xgb_model = XGBRegressor()
    xgb_model.load_model(XGB_PATH)

    rf_model = joblib.load(RF_PATH)

    xgb_results = []
    rf_results = []

    for _ in range(horizon):

        feats = build_features(df)

        if feats.empty:
            break

        last_row = feats.iloc[[-1]]

        if last_row[FEATURE_COLS].isnull().any().any():
            raise ValueError("Missing features in future forecast.")

        xgb_pred = float(
            xgb_model.predict(last_row[FEATURE_COLS])[0]
        )

        rf_pred = float(
            rf_model.predict(last_row[FEATURE_COLS])[0]
        )

        next_ts = (
            pd.to_datetime(df["timestamp"].iloc[-1])
            + pd.Timedelta(hours=1)
        )

        # Carry forward the latest known weather values.
        # These are not actual future weather observations.
        next_row = {
            "timestamp": next_ts,
            "consumption_kwh": xgb_pred,
            "temperature_c": df["temperature_c"].iloc[-1],
            "humidity_pct": df["humidity_pct"].iloc[-1]
        }

        df = pd.concat(
            [df, pd.DataFrame([next_row])],
            ignore_index=True
        )

        xgb_results.append({
            "timestamp": next_ts.isoformat(),
            "predicted_kwh": round(xgb_pred, 3)
        })

        rf_results.append({
            "timestamp": next_ts.isoformat(),
            "predicted_kwh": round(rf_pred, 3)
        })

    return {
        "xgb": xgb_results,
        "rf": rf_results
    }
