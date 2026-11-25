
import pandas as pd
import os
import requests

INPUT_FILE = "data/household_power_consumption.txt"
OUTPUT_FILE = "data/consumption.csv"


def process_data():
    print("Loading real electricity dataset...")

    if not os.path.exists(INPUT_FILE):
        print("Dataset not found:", INPUT_FILE)
        return

    # Read original UCI/Kaggle data
    df = pd.read_csv(
        INPUT_FILE,
        sep=";",
        na_values=["?"],
        low_memory=False
    )

    df.columns = df.columns.str.strip()

    # Create timestamp
    df["timestamp"] = pd.to_datetime(
        df["Date"].astype(str) + " " + df["Time"].astype(str),
        format="%d/%m/%Y %H:%M:%S",
        errors="coerce"
    )

    df["Global_active_power"] = pd.to_numeric(
        df["Global_active_power"], errors="coerce"
    )

    df = df.dropna(
        subset=["timestamp", "Global_active_power"]
    )

    df = df.sort_values("timestamp").set_index("timestamp")

    print("Converting minute-level power into hourly energy...")

    # Each reading is kW for approximately one minute.
    # Sum valid readings and divide by 60 to get hourly kWh.
    hourly_energy = (
        df["Global_active_power"]
        .resample("h")
        .sum(min_count=60) / 60
    )

    hourly_df = hourly_energy.dropna().reset_index()
    hourly_df.columns = ["timestamp", "consumption_kwh"]

    print("Downloading historical weather data...")

    start_date = hourly_df["timestamp"].min().strftime("%Y-%m-%d")
    end_date = hourly_df["timestamp"].max().strftime("%Y-%m-%d")

    url = "https://archive-api.open-meteo.com/v1/archive"

    params = {
        "latitude": 48.776,
        "longitude": 2.293,
        "start_date": start_date,
        "end_date": end_date,
        "hourly": "temperature_2m,relative_humidity_2m",
        "timezone": "Europe/Paris"
    }

    response = requests.get(url, params=params, timeout=120)
    response.raise_for_status()

    weather = response.json()["hourly"]

    weather_df = pd.DataFrame({
        "timestamp": pd.to_datetime(weather["time"]),
        "temperature_c": weather["temperature_2m"],
        "humidity_pct": weather["relative_humidity_2m"]
    })

    # Match electricity and weather timestamps
    hourly_df["timestamp"] = pd.to_datetime(
    hourly_df["timestamp"]
)

    weather_df["timestamp"] = pd.to_datetime(
    weather_df["timestamp"]
)

    final_df = hourly_df.merge(
        weather_df,
        on="timestamp",
        how="inner"
    )

    final_df = final_df.dropna()


    final_df["consumption_kwh"] = (
        final_df["consumption_kwh"].round(4)
    )

    os.makedirs("data", exist_ok=True)

    final_df.to_csv(OUTPUT_FILE, index=False)

    print("\nDataset successfully created!")
    print("Total records:", len(final_df))
    print(final_df.head())
    print("\nSaved to:", OUTPUT_FILE)


if __name__ == "__main__":
    process_data()
