import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend, CartesianGrid } from "recharts";

export default function ForecastChart({ history = [], forecast = { xgb: [], rf: [] }, arima = [] }) {
  const actuals = history.slice(-24);
  const chartData = [];

  // We create exactly 24 data points
  for (let i = 0; i < 24; i++) {
    const act = actuals[i];
    const xgb = forecast.xgb ? forecast.xgb[i] : null;
    const rf = forecast.rf ? forecast.rf[i] : null;
    const ar = arima ? arima[i] : null;

    chartData.push({
      time: `Hr ${i + 1}`,
            actual: act && act.consumption_kwh ? parseFloat(act.consumption_kwh) : null,
      xgboost: xgb && xgb.predicted_kwh ? parseFloat(xgb.predicted_kwh) : null,
      random_forest: rf && rf.predicted_kwh ? parseFloat(rf.predicted_kwh) : null,
      arima: ar && ar.predicted_kwh ? parseFloat(ar.predicted_kwh) : null,
    });
  }

  return (
    <div className="bg-slate-900 rounded-xl p-6 shadow-lg border border-slate-800 h-[400px] flex flex-col">
      <h2 className="mb-4 text-lg font-semibold text-slate-100">Model Comparison (Next 24 Hours)</h2>
      <div className="flex-1">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#1e293b" />
            <XAxis dataKey="time" tick={{fontSize: 12, fill: "#94a3b8"}} axisLine={false} tickLine={false} />
            <YAxis domain={[0, 'auto']} tick={{fontSize: 12, fill: "#94a3b8"}} axisLine={false} tickLine={false} />
            <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', borderRadius: '8px', color: '#f8fafc' }} />
            <Legend verticalAlign="top" height={36} wrapperStyle={{ fontSize: '12px', color: '#cbd5e1' }}/>
            
            <Line type="monotone" dataKey="actual" name="Actual" stroke="#10b981" strokeWidth={3} dot={false} />
            <Line type="monotone" dataKey="xgboost" name="XGBoost" stroke="#f59e0b" strokeWidth={2} strokeDasharray="5 5" dot={false} />
            <Line type="monotone" dataKey="random_forest" name="Random Forest" stroke="#ec4899" strokeWidth={2} dot={false} />
            <Line type="monotone" dataKey="arima" name="ARIMA" stroke="#3b82f6" strokeWidth={2} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}