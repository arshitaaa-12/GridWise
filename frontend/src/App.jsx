import { useEffect, useState } from "react";
import { BrowserRouter, Routes, Route, Link, useLocation } from "react-router-dom";
import { getConsumption, getForecast, scanAnomalies, getAnomalies, getTimeSeriesForecast } from "./api.js";
import Dashboard from "./components/Dashboard.jsx";
import ForecastChart from "./components/ForecastChart.jsx";
import AnomalyPanel from "./components/AnomalyPanel.jsx";
import Analytics from "./components/Analytics.jsx";
import Reports from "./components/Reports.jsx";
import Settings from "./components/Settings.jsx";

function Layout({ children, onScan, scanning }) {
  const location = useLocation();
  const navItems = [
    { path: "/", label: "Dashboard", icon: "📊" },
    { path: "/analytics", label: "Analytics", icon: "📈" },
    { path: "/reports", label: "Reports", icon: "📄" },
    { path: "/settings", label: "Settings", icon: "⚙️" }
  ];

  return (
    <div className="min-h-screen bg-slate-950 font-sans text-slate-200 flex">
      <aside className="w-64 bg-slate-900 border-r border-slate-800 flex flex-col hidden md:flex">
        <div className="h-16 flex items-center px-6 text-white font-bold text-xl border-b border-slate-800">⚡ GridWise</div>
        <nav className="flex-1 p-4 space-y-2">
          {navItems.map((item) => (
            <Link key={item.path} to={item.path} className={`block px-4 py-2.5 rounded-lg font-medium transition-colors ${location.pathname === item.path ? "bg-blue-500/10 text-blue-400 border border-blue-500/20" : "text-slate-400 hover:text-white hover:bg-slate-800"}`}>
              <span className="mr-3">{item.icon}</span> {item.label}
            </Link>
          ))}
        </nav>
      </aside>
      <main className="flex-1 flex flex-col h-screen overflow-y-auto">
        <header className="h-16 bg-slate-900/80 backdrop-blur-md border-b border-slate-800 flex items-center justify-between px-8 sticky top-0 z-10">
          <h2 className="text-xl font-semibold text-white capitalize">{location.pathname === "/" ? "Energy Overview" : location.pathname.replace("/", "")}</h2>
          <button onClick={onScan} disabled={scanning} className="bg-blue-600 hover:bg-blue-500 text-white px-5 py-2 rounded-lg font-medium shadow-sm">
            {scanning ? "Scanning..." : "✨ Run AI Scan"}
          </button>
        </header>
        <div className="p-8 max-w-7xl mx-auto w-full">{children}</div>
      </main>
    </div>
  );
}

export default function App() {
  const [consumption, setConsumption] = useState([]);
  const [forecast, setForecast] = useState({ xgb: [], rf: [] }); 
  const [anomalies, setAnomalies] = useState([]);
  const [arima, setArima] = useState([]); 
  const [loading, setLoading] = useState(true);
  const [scanning, setScanning] = useState(false);

  const load = async () => {
    setLoading(true);
    try {
      const [c, f, a, t] = await Promise.all([
        getConsumption(1), 
        getForecast(1), 
        getAnomalies(1),
        getTimeSeriesForecast(1)
      ]);
      setConsumption(c || []); 
      setForecast(f || { xgb: [], rf: [] }); 
      setAnomalies(a || []); 
      
      // Safe extraction of ARIMA data
      setArima(t && t.forecast ? t.forecast : []); 
    } catch (err) { 
      console.error(err); 
    }
    setLoading(false);
  };

  useEffect(() => { load(); }, []);

  const runScan = async () => {
    setScanning(true);
    const res = await scanAnomalies(1);
    alert(`Detected ${res.count} anomalies!`);
    await load();
    setScanning(false);
  };

  if (loading) return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-slate-950 text-white">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mb-4"></div>
      <p>Running AI Models (XGBoost, RF, ARIMA)...</p>
    </div>
  );

  return (
    <BrowserRouter>
      <Layout onScan={runScan} scanning={scanning}>
        <Routes>
          <Route path="/" element={
            <div className="space-y-6">
              <Dashboard consumption={consumption} anomalies={anomalies} />
              <div className="flex flex-col gap-6">
                {/* Pass the ARIMA data as a prop */}
                <ForecastChart history={consumption} forecast={forecast} arima={arima} />
                <AnomalyPanel anomalies={anomalies} />
              </div>
            </div>
          } />
          <Route path="/analytics" element={<Analytics consumption={consumption} />} />
          <Route path="/reports" element={<Reports anomalies={anomalies} />} />
          <Route path="/settings" element={<Settings />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
}