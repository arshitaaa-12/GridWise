# ⚡ GridWise: Intelligent Energy Consumption Forecasting & Waste Detection

GridWise is an intelligent, full-stack machine learning platform designed to forecast electricity consumption, detect abnormal usage patterns (anomalies), and explain the reasons behind them using Explainable AI (SHAP).

Unlike traditional energy monitors that only show historical data, GridWise actively predicts future demand and identifies situations where actual consumption is significantly higher than expected, providing actionable recommendations to reduce waste.

## 🚀 Key Features
* **Consumption Forecasting:** Compares three ML models (XGBoost, Random Forest, and ARIMA) to predict the next 24 hours of energy usage.
* **Hybrid Anomaly Detection:** Combines Isolation Forest, forecast residuals, and historical pattern analysis to detect abnormal spikes.
* **Explainable AI (XAI):** Uses SHAP (SHapley Additive exPlanations) to explain *why* an anomaly was flagged (e.g., "temperature pushed consumption up by 4.2 kWh").
* **Cost & Savings Estimation:** Calculates the estimated next-24h bill and potential savings if anomalies are resolved.
* **Interactive Dashboard:** A sleek, dark-mode React dashboard with real-time charts, analytics, and a generated report log.

## 🛠️ Technology Stack
* **Frontend:** React.js, Vite, Tailwind CSS, Recharts
* **Backend:** Node.js, Express.js
* **Machine Learning API:** Python, FastAPI, Scikit-learn, XGBoost, Statsmodels, SHAP
* **Database:** PostgreSQL
* **Dataset:** UCI Individual Household Electric Power Consumption (Kaggle)

## 📁 Project Structure
```text
gridwise/
├── backend/          # Node.js/Express API, Database connection, Anomaly routes
├── db/               # PostgreSQL schema definitions
├── frontend/         # React UI, Charts, Analytics, Settings
└── ml-service/       # FastAPI, ML models (XGBoost, RF, ARIMA), SHAP logic
