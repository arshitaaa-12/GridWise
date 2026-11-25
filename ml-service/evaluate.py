import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.metrics import precision_score, recall_score, f1_score
from app.features import build_features, FEATURE_COLS
from app.forecasting import load_forecaster

def run_evaluation():
    print("Loading data...")
    df = pd.read_csv("data/consumption.csv", parse_dates=["timestamp"])
    
    # We know the synthetic data has massive anomalies injected at indices 4000, 6000, 7500.
    # Let's create ground truth labels (1 = anomaly, 0 = normal) for evaluation.
    labels = pd.Series(0, index=range(len(df)))
    labels.iloc[4000] = 1
    labels.iloc[6000] = 1
    labels.iloc[7500] = 1

    feats = build_features(df)
    # Align labels with dropped NaN rows from feature engineering
    labels = labels.iloc[-len(feats):].reset_index(drop=True)
    X = feats[FEATURE_COLS]

    # --- 1. Standalone Isolation Forest ---
    iso = IsolationForest(contamination=0.01, random_state=42)
    iso.fit(X)
    iso_pred = (iso.predict(X) == -1).astype(int)

    # --- 2. Forecast-based ---
    model = load_forecaster()
    preds = model.predict(X)
    residual = feats["consumption_kwh"].values - preds
    rolling_std = feats["rolling_std_24h"].replace(0, np.nan).fillna(1.0).values
    z_scores = residual / rolling_std
    forecast_pred = (np.abs(z_scores) > 2.5).astype(int)

    # --- 3. Hybrid ---
    hybrid_pred = ((forecast_pred == 1) | ((iso_pred == 1) & (np.abs(z_scores) > 1.5))).astype(int)

    # --- Evaluation Metrics ---
    def get_metrics(name, preds):
        p = precision_score(labels, preds, zero_division=0)
        r = recall_score(labels, preds, zero_division=0)
        f1 = f1_score(labels, preds, zero_division=0)
        return {"Method": name, "Precision": round(p, 3), "Recall": round(r, 3), "F1-Score": round(f1, 3)}

    results = [
        get_metrics("Standalone (Isolation Forest)", iso_pred),
        get_metrics("Forecast-Based (Residual)", forecast_pred),
        get_metrics("Hybrid (Combined)", hybrid_pred)
    ]

    print("\n=== ANOMALY DETECTION EVALUATION ===")
    print(pd.DataFrame(results).to_string(index=False))

    # --- Simulated Energy Savings ---
    # Assume the hybrid model catches 3 anomalies, each wasting 15 kWh.
    # Cost is $0.15 per kWh.
    anomalies_caught = hybrid_pred.sum()
    wasted_kwh = anomalies_caught * 15 
    cost_saved = wasted_kwh * 0.15
    
    print("\n=== SIMULATED ENERGY SAVINGS ===")
    print(f"Anomalies Caught: {anomalies_caught}")
    print(f"Estimated Energy Wasted: {wasted_kwh} kWh")
    print(f"Estimated Cost Saved (at $0.15/kWh): ${cost_saved:.2f}")

if __name__ == "__main__":
    run_evaluation()