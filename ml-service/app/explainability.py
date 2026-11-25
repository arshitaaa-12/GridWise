import shap
import numpy as np
import pandas as pd
from .forecasting import load_forecaster
from .features import build_features, FEATURE_COLS

def explain_anomaly(history_df: pd.DataFrame, anomaly_ts: str):
    model = load_forecaster()
    feats = build_features(history_df)
    feats["timestamp"] = pd.to_datetime(feats["timestamp"])
    target = feats[feats["timestamp"] == pd.to_datetime(anomaly_ts)]
    if target.empty: return {"error": "timestamp not found"}

    explainer = shap.TreeExplainer(model)
    shap_vals = explainer.shap_values(target[FEATURE_COLS])[0]

    contrib = pd.DataFrame({"feature": FEATURE_COLS, "shap_value": np.round(shap_vals, 3)}).sort_values("shap_value", key=np.abs, ascending=False)
    summary = [f"{r.feature} pushed consumption {'up' if r.shap_value > 0 else 'down'} by {abs(r.shap_value):.2f} kWh" for r in contrib.head(4).itertuples()]

    return {"predicted_kwh": float(target["consumption_kwh"].iloc[0]), "all_contributions": contrib.to_dict(orient="records"), "summary": summary}