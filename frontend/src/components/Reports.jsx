export default function Reports({ anomalies = [] }) {
  const totalAnomalies = anomalies.length;
  const totalWastedKwh = anomalies.reduce((sum, a) => sum + (Number(a.actual_kwh) - Number(a.expected_kwh)), 0);
  const totalSavings = totalWastedKwh * 0.15;

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-slate-900 rounded-xl p-6 shadow-lg border border-slate-800">
          <div className="text-sm text-slate-400">Total Anomalies Found</div>
          <div className="text-3xl font-bold text-red-400 mt-2">{totalAnomalies}</div>
        </div>
        <div className="bg-slate-900 rounded-xl p-6 shadow-lg border border-slate-800">
          <div className="text-sm text-slate-400">Estimated Wasted Energy</div>
          <div className="text-3xl font-bold text-amber-400 mt-2">{totalWastedKwh.toFixed(1)} kWh</div>
        </div>
        <div className="bg-slate-900 rounded-xl p-6 shadow-lg border border-slate-800">
          <div className="text-sm text-slate-400">Potential Savings</div>
          <div className="text-3xl font-bold text-emerald-400 mt-2">${totalSavings.toFixed(2)}</div>
        </div>
      </div>

      <div className="bg-slate-900 rounded-xl shadow-lg border border-slate-800 overflow-hidden">
        <div className="p-6 border-b border-slate-800">
          <h2 className="text-lg font-semibold text-slate-100">Anomaly History Log</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-300">
            <thead className="bg-slate-950/50 text-slate-400">
              <tr>
                <th className="px-6 py-4">Date</th>
                <th className="px-6 py-4">Expected (kWh)</th>
                <th className="px-6 py-4">Actual (kWh)</th>
                <th className="px-6 py-4">Difference</th>
                <th className="px-6 py-4">Severity</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {anomalies.length === 0 ? (
                <tr><td colSpan="5" className="px-6 py-8 text-center text-slate-500">No anomalies logged yet.</td></tr>
              ) : (
                anomalies.map((a) => {
                  const diff = Number(a.actual_kwh) - Number(a.expected_kwh);
                  return (
                    <tr key={a.id} className="hover:bg-slate-800/50">
                      <td className="px-6 py-4 whitespace-nowrap">{new Date(a.detected_at).toLocaleString()}</td>
                      <td className="px-6 py-4">{Number(a.expected_kwh).toFixed(2)}</td>
                      <td className="px-6 py-4 font-bold text-red-400">{Number(a.actual_kwh).toFixed(2)}</td>
                      <td className="px-6 py-4 text-red-400">+{diff.toFixed(2)}</td>
                      <td className="px-6 py-4">
                        <span className="px-2 py-1 rounded-full text-xs font-bold bg-red-500/20 text-red-400">{a.severity}</span>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}