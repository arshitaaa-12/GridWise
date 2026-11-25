import pandas as pd
import numpy as np
import os

# --- CHECK THIS FILENAME ---
INPUT_FILE = "data/household_power_consumption.txt" 

def process_data():
    print(f"Loading {INPUT_FILE}...")
    
    if not os.path.exists(INPUT_FILE):
        print(f"❌ File not found at {INPUT_FILE}. Please check the name and location.")
        return

    # 1. Read and clean the file line by line
    valid_lines = []
    with open(INPUT_FILE, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            # Kaggle UCI file uses semicolons. If yours uses commas, change ';' to ','
            if ';' in line:
                # Clean weird characters and quotes
                clean_line = line.replace('"', '').strip()
                valid_lines.append(clean_line)

    print(f"Valid lines read: {len(valid_lines)}")

    # 2. Convert to Pandas DataFrame
    from io import StringIO
    csv_data = StringIO("\n".join(valid_lines))
    
    # Read the data, forcing bad lines to be skipped
    df = pd.read_csv(csv_data, sep=';', na_values=['?'], on_bad_lines='skip', low_memory=False)
    
    # Clean column names
    df.columns = [c.strip() for c in df.columns]
    print(f"Columns found: {df.columns.tolist()}")

    # 3. Create a proper timestamp
    if 'Date' in df.columns and 'Time' in df.columns:
        df['timestamp'] = pd.to_datetime(df['Date'] + ' ' + df['Time'], format='%d/%m/%Y %H:%M:%S', errors='coerce')
    elif 'timestamp' not in df.columns:
        raise ValueError("Could not find Date/Time columns. Check the column names printed above.")

    # 4. Get the consumption column
    if 'Global_active_power' in df.columns:
        df['consumption_kwh'] = pd.to_numeric(df['Global_active_power'], errors='coerce')
    elif 'consumption_kwh' not in df.columns:
        raise ValueError("Could not find Global_active_power. Check the column names printed above.")

    # 5. Drop bad rows and resample to hourly
    df = df.dropna(subset=['timestamp', 'consumption_kwh'])
    print("Resampling minute data to hourly data...")
    
        df = df.set_index('timestamp')
    # We use MEAN instead of SUM because the data is already in kW.
    # Averaging the hour gives us the kW for that hour (which is kWh).
    hourly_df = df[['consumption_kwh']].resample('h').mean().reset_index()
    hourly_df = hourly_df.dropna()
    
    # Clean the data to prevent database errors
    hourly_df['consumption_kwh'] = hourly_df['consumption_kwh'].round(3)
    
    # 6. Add Synthetic Weather (UCI dataset doesn't have weather)
    np.random.seed(42)
    n = len(hourly_df)
    hours = np.arange(n)
    hourly_df['temperature_c'] = 25 + 8 * np.sin(2 * np.pi * hours / (24 * 365)) + np.random.normal(0, 1, n)
    hourly_df['humidity_pct'] = 60 + np.random.normal(0, 5, n)

    # 7. Save it
    hourly_df.to_csv("data/consumption.csv", index=False)
    print(f"✅ Processed and saved {len(hourly_df)} hours of REAL data to data/consumption.csv")

if __name__ == "__main__":
    process_data()