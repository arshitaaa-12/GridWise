export default function Settings() {
  return (
    <div className="bg-slate-900 rounded-xl p-6 shadow-lg border border-slate-800 max-w-2xl">
      <h2 className="text-lg font-semibold text-slate-100 mb-6">User Preferences ⚙️</h2>
      
      <div className="space-y-6">
        <div>
          <label className="block text-sm font-medium text-slate-400 mb-2">Building Name</label>
          <input type="text" defaultValue="Demo Building" className="w-full bg-slate-950 border border-slate-800 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-blue-500" />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-slate-400 mb-2">Electricity Tariff Rate ($/kWh)</label>
          <input type="number" defaultValue="0.15" step="0.01" className="w-full bg-slate-950 border border-slate-800 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-blue-500" />
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-400 mb-2">Alert Sensitivity</label>
          <select className="w-full bg-slate-950 border border-slate-800 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-blue-500">
            <option>High (Catch everything)</option>
            <option>Medium (Balanced)</option>
            <option>Low (Only extreme anomalies)</option>
          </select>
        </div>

        <button className="bg-blue-600 hover:bg-blue-500 text-white px-6 py-2 rounded-lg font-medium transition-colors">
          Save Changes
        </button>
      </div>
    </div>
  );
}