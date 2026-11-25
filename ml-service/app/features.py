import pandas as pd
import numpy as np

def add_time_features(df: pd.DataFrame, ts_col: str = "timestamp") -> pd.DataFrame:
    df = df.copy()
    df[ts_col] = pd.to_datetime(df[ts_col])
    df["hour"] = df[ts_col].dt.hour
    df["day_of_week"] = df[ts_col].dt.dayofweek
    df["month"] = df[ts_col].dt.month
    df["is_weekend"] = (df["day_of_week"] >= 5).astype(int)
    df["season"] = df["month"].map({12: 0, 1: 0, 2: 0, 3: 1, 4: 1, 5: 1, 6: 2, 7: 2, 8: 2, 9: 3, 10: 3, 11: 3})
    df["hour_sin"] = np.sin(2 * np.pi * df["hour"] / 24)
    df["hour_cos"] = np.cos(2 * np.pi * df["hour"] / 24)
    return df

def add_lag_features(df: pd.DataFrame, target: str = "consumption_kwh") -> pd.DataFrame:
    df = df.sort_values("timestamp").copy()
    df["lag_1h"] = df[target].shift(1)
    df["lag_24h"] = df[target].shift(24)
    df["lag_168h"] = df[target].shift(168)
    df["rolling_mean_24h"] = df[target].shift(1).rolling(24).mean()
    df["rolling_std_24h"] = df[target].shift(1).rolling(24).std()
    return df

FEATURE_COLS = [
    "hour", "day_of_week", "month", "is_weekend", "season",
    "hour_sin", "hour_cos", "temperature_c", "humidity_pct",
    "lag_1h", "lag_24h", "lag_168h", "rolling_mean_24h", "rolling_std_24h",
]

def build_features(df: pd.DataFrame) -> pd.DataFrame:
    df = add_time_features(df)
    df = add_lag_features(df)
    return df.dropna(subset=FEATURE_COLS).reset_index(drop=True)