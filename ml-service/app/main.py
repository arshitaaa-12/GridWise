from fastapi import FastAPI, HTTPException
import pandas as pd
from .schemas import ForecastRequest, AnomalyRequest
from .forecasting import forecast_all_models
from .anomaly import detect_anomalies
from .explainability import explain_anomaly
from .recommendations import generate_recommendations
from .timeseries import train_and_forecast_arima

app = FastAPI(title="GridWise ML Service")

@app.get("/health")
def health(): return {"status": "ok"}

@app.post("/predict")
def predict(req: ForecastRequest):
    df = pd.DataFrame([r.model_dump() for r in req.history])
    if len(df) < 200: raise HTTPException(400, "Need at least 200 historical rows")
    return forecast_all_models(df, horizon=req.horizon)

@app.post("/detect-anomaly")
def detect(req: AnomalyRequest):
    df = pd.DataFrame([r.model_dump() for r in req.history])
    out = detect_anomalies(df)
    anomalies = out[out["hybrid_flag"] == 1].to_dict(orient="records")

    enriched = []
    for a in anomalies:
        expl = explain_anomaly(df, a["timestamp"])
        recs = generate_recommendations({**a, "hour": pd.to_datetime(a["timestamp"]).hour}, expl.get("summary", []))
        enriched.append({**a, "explanation": expl, "recommendations": recs})
    return {"count": len(enriched), "anomalies": enriched}

@app.post("/predict-timeseries")
def predict_timeseries(req: ForecastRequest):
    df = pd.DataFrame([r.model_dump() for r in req.history])
    if len(df) < 200: raise HTTPException(400, "Need at least 200 historical rows")
    out = train_and_forecast_arima(df, horizon=req.horizon)
    return {"forecast": out.to_dict(orient="records")}