import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from .forecasting import load_forecaster
from .features import build_features, FEATURE_COLS

def detect_anomalies(df: pd.DataFrame, residual_threshold: float = 2.5):
    model = load_forecaster()
    feats = build_features(df)
    if feats.empty: return feats

    iso = IsolationForest(contamination=0.02, random_state=42, n_estimators=200)
    iso.fit(feats[FEATURE_COLS])

    X = feats[FEATURE_COLS]
    predicted = model.predict(X)
    residual = feats["consumption_kwh"].values - predicted
    rolling_std = feats["rolling_std_24h"].replace(0, np.nan).fillna(1.0).values
    z = residual / rolling_std

    forecast_flag = (np.abs(z) > residual_threshold).astype(int)
    iso_flag = (iso.predict(X) == -1).astype(int)
    hybrid_flag = ((forecast_flag == 1) | ((iso_flag == 1) & (np.abs(z) > 1.5))).astype(int)

    out = feats[["timestamp", "consumption_kwh"]].copy()
    out["predicted_kwh"] = predicted.round(3)
    out["residual_z"] = np.round(z, 2)
    out["forecast_flag"] = forecast_flag
    out["iso_flag"] = iso_flag
    out["hybrid_flag"] = hybrid_flag
    return out