const BASE = import.meta.env.VITE_API_URL || "http://localhost:4000";

export const getConsumption = async (id) => (await fetch(`${BASE}/api/consumption/${id}`)).json();
export const getForecast = async (id) => (await fetch(`${BASE}/api/consumption/${id}/forecast?horizon=24`)).json();
export const scanAnomalies = async (id) => (await fetch(`${BASE}/api/anomalies/${id}/scan`, { method: "POST" })).json();
export const getAnomalies = async (id) => (await fetch(`${BASE}/api/anomalies/${id}`)).json();

export const getTimeSeriesForecast = async (id) => {
  const res = await fetch(`${BASE}/api/consumption/${id}/forecast-timeseries?horizon=24`);
  const data = await res.json();
  console.log("ARIMA API RESPONSE:", data); // Add this to see it in the browser console!
  return data;
};