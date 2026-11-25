import pandas as pd
import numpy as np
import os

os.makedirs("data", exist_ok=True)
n = 8760
ts = pd.date_range("2023-01-01", periods=n, freq="h")
hours = np.arange(n)
base = 10 + 5 * np.sin(2 * np.pi * hours / 24) + 3 * np.sin(2 * np.pi * hours / (24 * 365))
noise = np.random.normal(0, 1, n)
consumption = base + noise

# The 3 original anomalies that worked perfectly
# Inject anomalies very close to the end
consumption[-5] += 25  # Massive spike
consumption[-15] += 30 # Massive spike
consumption[-25] += 20 # Massive spike

pd.DataFrame({
    "timestamp": ts, 
    "consumption_kwh": consumption,
    "temperature_c": 25 + 8 * np.sin(2 * np.pi * hours / (24 * 365)) + np.random.normal(0, 1, n),
    "humidity_pct": 60 + np.random.normal(0, 5, n),
}).to_csv("data/consumption.csv", index=False)
print("Generated data/consumption.csv")