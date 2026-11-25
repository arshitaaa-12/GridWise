import argparse
import pandas as pd
from app.forecasting import train_forecaster

def main(csv_path: str):
    df = pd.read_csv(csv_path, parse_dates=["timestamp"])
    print(f"Loaded {len(df)} rows")
    train_forecaster(df)

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True)
    args = ap.parse_args()
    main(args.csv)