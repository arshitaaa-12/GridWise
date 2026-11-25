
import pandas as pd
import numpy as np

from sklearn.ensemble import IsolationForest
from sklearn.metrics import mean_absolute_error, mean_squared_error

from app.features import build_features, FEATURE_COLS
from app.forecasting import load_forecaster


def run_evaluation():

    # 1. Load real processed Kaggle data
    print("Loading real electricity consumption data...")

    df = pd.read_csv(
        "data/consumption.csv",
        parse_dates=["timestamp"]
    )

    df = df.sort_values("timestamp").reset_index(drop=True)

    print(f"Total records: {len(df)}")

    # 2. Build features
    feats = build_features(df)

    feats = feats.dropna(subset=FEATURE_COLS + ["consumption_kwh"])

    X = feats[FEATURE_COLS]
    y = feats["consumption_kwh"]

    # 3. Chronological 80-20 train-test split
    split_index = int(len(feats) * 0.80)

    X_train = X.iloc[:split_index]
    X_test = X.iloc[split_index:]

    y_test = y.iloc[split_index:]

    test_data = feats.iloc[split_index:]

    print(f"Training records: {len(X_train)}")
    print(f"Testing records: {len(X_test)}")

    # 4. Standalone Isolation Forest
    iso = IsolationForest(
        contamination=0.01,
        random_state=42
    )

    iso.fit(X_train)

    iso_pred = (iso.predict(X_test) == -1).astype(int)

    # 5. Forecast-based anomaly detection
    model = load_forecaster()

    preds = model.predict(X_test)

    residual = y_test.values - preds

    rolling_std = (
        test_data["rolling_std_24h"]
        .replace(0, np.nan)
        .fillna(1.0)
        .values
    )

    z_scores = residual / rolling_std

    forecast_pred = (np.abs(z_scores) > 2.5).astype(int)

    # 6. Hybrid anomaly detection
    hybrid_pred = (
        (forecast_pred == 1) |
        ((iso_pred == 1) & (np.abs(z_scores) > 1.5))
    ).astype(int)

    # 7. Forecast performance metrics
    mae = mean_absolute_error(y_test, preds)

    rmse = np.sqrt(mean_squared_error(y_test, preds))

    print("\n=== FORECASTING PERFORMANCE ===")

    print(f"MAE:  {mae:.4f} kWh")
    print(f"RMSE: {rmse:.4f} kWh")

    # 8. Anomaly detection results
    print("\n=== ANOMALY DETECTION RESULTS ===")

    results = pd.DataFrame({
        "Method": [
            "Isolation Forest",
            "Forecast-Based",
            "Hybrid"
        ],
        "Anomalies Detected": [
            int(iso_pred.sum()),
            int(forecast_pred.sum()),
            int(hybrid_pred.sum())
        ],
        "Percentage of Test Data": [
            round(iso_pred.mean() * 100, 2),
            round(forecast_pred.mean() * 100, 2),
            round(hybrid_pred.mean() * 100, 2)
        ]
    })

    print(results.to_string(index=False))

    # 9. Save actual detected anomalies
    anomaly_results = test_data[
        ["timestamp", "consumption_kwh"]
    ].copy()

    anomaly_results["isolation_forest"] = iso_pred
    anomaly_results["forecast_based"] = forecast_pred
    anomaly_results["hybrid"] = hybrid_pred
    anomaly_results["z_score"] = z_scores

    anomaly_results.to_csv(
        "data/anomaly_results.csv",
        index=False
    )

    print("\nAnomaly results saved to data/anomaly_results.csv")

    print("\nEvaluation completed successfully.")


if __name__ == "__main__":
    run_evaluation()
