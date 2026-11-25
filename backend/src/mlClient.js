import axios from "axios";
const ML_URL = process.env.ML_URL || "http://localhost:8000";

export async function callForecast(history, horizon = 24) {
  const { data } = await axios.post(`${ML_URL}/predict`, { history, horizon });
  return data;
}
export async function callDetectAnomaly(history) {
  const { data } = await axios.post(`${ML_URL}/detect-anomaly`, { history });
  return data;
}