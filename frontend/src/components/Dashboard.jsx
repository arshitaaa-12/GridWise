import { useState, useEffect } from "react";

export default function Dashboard({ consumption = [], anomalies = [] }) {
  const [costData, setCostData] = useState(null);

  useEffect(() => {
    fetch("http://localhost:4000/api/consumption/1/cost-estimate")
      .then(res => res.json())
      .then(data => setCostData(data))
      .catch(err => console.error(err));
  }, []);

  const total = consumption.reduce((s, r) => s + Number(r.consumption_kwh || 0), 0);

  const stats = [
    { label: "Total Consumption", value: `${total.toFixed(1)} kWh`, icon: "⚡", color: "text-blue-400" },
    { label: "Avg Hourly", value: `${(total / (consumption.length || 1)).toFixed(2)} kWh`, icon: "📊", color: "text-indigo-400" },
    { label: "Anomalies Detected", value: anomalies.length, icon: "⚠️", color: anomalies.length > 0 ? "text-red-400" : "text-slate-200" },
    { label: "Est. Next 24h Bill", value: costData ? `$${costData.estimatedCost}` : "...", icon: "💰", color: "text-emerald-400" },
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {stats.map((s, i) => (
        <div key={i} className="bg-slate-900 rounded-xl p-6 shadow-lg border border-slate-800 hover:border-slate-700 transition-colors">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-slate-400">{s.label}</span>
            <span className="text-xl opacity-80">{s.icon}</span>
          </div>
          <div className={`text-3xl font-bold ${s.color}`}>{s.value}</div>
        </div>
      ))}
    </div>
  );
}