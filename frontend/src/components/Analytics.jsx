import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";

export default function Analytics({ consumption }) {
  // Group consumption by hour of the day to find peak hours
  const hourlyData = consumption.reduce((acc, curr) => {
    const hour = new Date(curr.timestamp).getHours();
    if (!acc[hour]) acc[hour] = { hour: `${hour}:00`, total: 0, count: 0 };
    acc[hour].total += Number(curr.consumption_kwh);
    acc[hour].count += 1;
    return acc;
  }, {});

  const chartData = Object.values(hourlyData).map(d => ({
    hour: d.hour,
    average: parseFloat((d.total / d.count).toFixed(2))
  }));

  return (
    <div className="bg-slate-900 rounded-xl p-6 shadow-lg border border-slate-800">
      <h2 className="text-lg font-semibold text-slate-100 mb-4">Average Usage by Hour of Day</h2>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#1e293b" />
          <XAxis dataKey="hour" tick={{fontSize: 12, fill: "#94a3b8"}} axisLine={false} />
          <YAxis tick={{fontSize: 12, fill: "#94a3b8"}} axisLine={false} />
          <Tooltip cursor={{fill: '#1e293b'}} contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', borderRadius: '8px' }} />
          <Bar dataKey="average" fill="#3b82f6" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}