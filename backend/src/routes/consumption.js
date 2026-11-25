import { Router } from "express";
import { getReadings } from "../db.js";
import { callForecast } from "../mlClient.js";

const router = Router();

router.get("/:buildingId", async (req, res) => {
  res.json(await getReadings(Number(req.params.buildingId)));
});

router.get("/:buildingId/forecast", async (req, res) => {
  const history = await getReadings(Number(req.params.buildingId));
  const result = await callForecast(history, Number(req.query.horizon || 24));
  res.json(result); 
});

router.get("/:buildingId/forecast-timeseries", async (req, res) => {
  try {
    const history = await getReadings(Number(req.params.buildingId));
    const axios = (await import("axios")).default;
    const ML_URL = process.env.ML_URL || "http://localhost:8000";
    
    const { data } = await axios.post(`${ML_URL}/predict-timeseries`, { 
      history, 
      horizon: Number(req.query.horizon || 24) 
    });
    res.json(data);
  } catch (error) {
    console.error("ARIMA Forecast Error:", error.message);
    res.status(500).json({ error: "Failed to generate time-series forecast" });
  }
});

router.get("/:buildingId/cost-estimate", async (req, res) => {
  const history = await getReadings(Number(req.params.buildingId));
  const result = await callForecast(history, 24); 
  
  const totalKwh = result.xgb.reduce((sum, f) => sum + f.predicted_kwh, 0);
  const tariffRate = 0.15;
  const estimatedCost = totalKwh * tariffRate;

  res.json({
    buildingId: req.params.buildingId,
    totalPredictedKwh: totalKwh.toFixed(2),
    tariffRate: tariffRate,
    estimatedCost: estimatedCost.toFixed(2),
    currency: "USD"
  });
});

export default router;