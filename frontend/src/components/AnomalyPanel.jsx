import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from "recharts";

export default function AnomalyPanel({ anomalies = [] }) {
  if (!anomalies.length) return (
    <div className="bg-slate-900 rounded-xl p-6 shadow-lg border border-slate-800 h-[400px] flex flex-col items-center justify-center text-slate-500">
      <span className="text-4xl mb-2 opacity-50">🛡️</span>
      <p>No anomalies detected yet.</p>
      <p className="text-sm">Click "Run AI Anomaly Scan" to analyze recent data.</p>
    </div>
  );

  const latestAnomaly = anomalies[0];
  const savings = anomalies.length * 15 * 0.15;
  
  let shapData = [];
  try {
    if (latestAnomaly.shap_explanation) {
      // SAFE PARSING: Check if it's a string before parsing
      const parsed = typeof latestAnomaly.shap_explanation === "string"
        ? JSON.parse(latestAnomaly.shap_explanation)
        : latestAnomaly.shap_explanation;

      shapData = parsed.all_contributions?.slice(0, 4).map(s => ({
        feature: s.feature.replace('_', ' ').toUpperCase(),
        impact: Number(s.shap_value)
      })) || [];
    }
  } catch(e) { 
    console.error("Failed to parse SHAP:", e); 
  }

  return (
    <div className="bg-slate-900 rounded-xl p-6 shadow-lg border border-slate-800 h-[400px] flex flex-col relative overflow-hidden">
      
      {/* Savings Badge */}
      <div className="absolute top-6 right-6 bg-emerald-500/10 text-emerald-400 px-3 py-1.5 rounded-full text-xs font-bold border border-emerald-500/20 flex items-center gap-1">
        💰 Est. Savings: ${savings.toFixed(2)}
      </div>

      <h2 className="mb-1 text-lg font-semibold text-slate-100 flex items-center gap-2">
        <span className="relative flex h-3 w-3">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
          <span className="relative inline-flex rounded-full h-3 w-3 bg-red-500"></span>
        </span>
        Latest Anomaly Alert
      </h2>
      <p className="text-sm text-slate-400 mb-4">{new Date(latestAnomaly.detected_at).toLocaleString()}</p>

      <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-3 mb-4">
        <div className="flex justify-between text-sm mb-1">
          <span className="text-slate-400">Expected:</span>
          <span className="font-semibold text-slate-200">{Number(latestAnomaly.expected_kwh).toFixed(2)} kWh</span>
        </div>
        <div className="flex justify-between text-sm mb-1">
          <span className="text-slate-400">Actual:</span>
          <span className="font-bold text-red-400">{Number(latestAnomaly.actual_kwh).toFixed(2)} kWh</span>
        </div>
        <div className="flex justify-between text-sm mt-2 pt-2 border-t border-red-500/20">
          <span className="text-red-400 font-semibold">Severity:</span>
          <span className="uppercase text-xs font-bold text-red-400 bg-red-500/20 px-2 py-0.5 rounded">{latestAnomaly.severity}</span>
        </div>
      </div>

      <div className="flex-1 min-h-[150px]">
        <p className="text-xs font-semibold text-slate-400 mb-2 uppercase tracking-wide">Why did the AI flag this? (SHAP)</p>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={shapData} layout="vertical" margin={{ left: -20, right: 20, top: 0, bottom: 0 }}>
            <XAxis type="number" hide />
            <YAxis dataKey="feature" type="category" axisLine={false} tickLine={false} tick={{fontSize: 10, fill: '#94a3b8', width: 80}} />
            <Tooltip cursor={{fill: '#1e293b'}} contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', borderRadius: '8px', color: '#f8fafc' }} />
            <Bar dataKey="impact" radius={[0, 4, 4, 0]} barSize={16}>
              {shapData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.impact > 0 ? '#ef4444' : '#3b82f6'} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}