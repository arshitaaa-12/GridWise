import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

def main():
    print("Generating EDA Images...")
    os.makedirs("eda_images", exist_ok=True)
    
    # Load data
    df = pd.read_csv("data/consumption.csv", parse_dates=["timestamp"])
    df.set_index("timestamp", inplace=True)
    sns.set_theme(style="darkgrid")

    # 1. Line Graph
    plt.figure(figsize=(15, 5))
    plt.plot(df.index[:720], df['consumption_kwh'][:720], color='#2563eb')
    plt.title('Electricity Consumption - First 30 Days')
    plt.ylabel('Consumption (kWh)')
    plt.savefig("eda_images/1_consumption_trend.png", bbox_inches='tight')
    plt.close()
    print("✅ Graph 1 done")

    # 2. Hourly Bar Chart
    df['hour'] = df.index.hour
    hourly_avg = df.groupby('hour')['consumption_kwh'].mean()
    plt.figure(figsize=(10, 5))
    sns.barplot(x=hourly_avg.index, y=hourly_avg.values, palette='viridis')
    plt.title('Average Consumption by Hour of Day')
    plt.xlabel('Hour of Day')
    plt.ylabel('Average kWh')
    plt.savefig("eda_images/2_hourly_usage.png", bbox_inches='tight')
    plt.close()
    print("✅ Graph 2 done")

    # 3. Heatmap (Safe Check)
    numeric_df = df.select_dtypes(include=['float64', 'int64'])
    if 'hour' in numeric_df.columns:
        numeric_df = numeric_df.drop(columns=['hour'])
        
    plt.figure(figsize=(8, 6))
    sns.heatmap(numeric_df.corr(), annot=True, cmap='coolwarm', fmt=".2f", linewidths=0.5)
    plt.title('Correlation Matrix')
    plt.savefig("eda_images/3_correlation_heatmap.png", bbox_inches='tight')
    plt.close()
    print("✅ Graph 3 done")

    # 4. Scatter Plot (Safe Check)
    if 'temperature_c' in df.columns:
        plt.figure(figsize=(10, 5))
        sns.scatterplot(x=df['temperature_c'], y=df['consumption_kwh'], alpha=0.3, color='#ec4899')
        plt.title('Temperature vs. Consumption')
        plt.xlabel('Temperature (°C)')
        plt.ylabel('Consumption (kWh)')
        plt.savefig("eda_images/4_temp_vs_consumption.png", bbox_inches='tight')
        plt.close()
        print("✅ Graph 4 done")
    else:
        print("❌ Could not find 'temperature_c' column for Graph 4. Skipping.")

    print("✅ All available images saved to 'ml-service/eda_images'!")

if __name__ == "__main__":
    main()