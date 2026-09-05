import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import StatCard from '../components/StatCard';
import RiskChart from '../components/RiskChart';
import RiskBadge from '../components/RiskBadge';
import EventTimeline from '../components/EventTimeline';
import {
  Activity,
  AlertTriangle,
  ShieldAlert,
  Camera,
  ShieldCheck,
  TrendingUp,
  Volume2,
  Video,
  ArrowUpRight,
  Layers,
  MapPin,
  Zap
} from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
  PieChart,
  Pie,
} from 'recharts';
import {
  getDashboardSummary,
  getHighRiskEvents,
  getTrends,
  getBehaviours,
  getLocations,
  getAlerts,
  audioAlerts
} from '../services/api';
import {
  DashboardSummary,
  Event,
  RiskTrend,
  BehaviourStats,
  LocationStats,
  AlertData
} from '../types';

export default function Dashboard() {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [events, setEvents] = useState<Event[]>([]);
  const [trends, setTrends] = useState<RiskTrend[]>([]);
  const [behaviours, setBehaviours] = useState<BehaviourStats[]>([]);
  const [locations, setLocations] = useState<LocationStats[]>([]);
  const [alerts, setAlerts] = useState<AlertData[]>([]);
  const [loading, setLoading] = useState(true);

  const navigate = useNavigate();

  useEffect(() => {
    Promise.all([
      getDashboardSummary(),
      getHighRiskEvents(),
      getTrends(),
      getBehaviours(),
      getLocations(),
      getAlerts()
    ]).then(([s, e, t, b, l, a]) => {
      setSummary(s);
      setEvents(e);
      setTrends(t);
      setBehaviours(b);
      setLocations(l);
      setAlerts(a);
      setLoading(false);
    });
  }, []);

  const [tasks, setTasks] = useState([
    { id: 1, title: 'Verify Bay 2 pallet alignment and forklift clearance', completed: false, tag: 'High Priority' },
    { id: 2, title: 'Confirm two-person lift protocol for heavy cartons at Bay 3', completed: true, tag: 'Coaching' },
    { id: 3, title: 'Inspect Bay 5 carton drop packaging before rack staging', completed: false, tag: 'Inspection' },
  ]);

  const toggleTask = (id: number) => {
    setTasks((prev) =>
      prev.map((t) => (t.id === id ? { ...t, completed: !t.completed } : t))
    );
  };

  const triggerTestAlert = () => {
    audioAlerts.playChime('CRITICAL');
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] text-slate-400 gap-3">
        <Activity className="w-8 h-8 text-blue-500 animate-spin" />
        <p className="text-sm font-semibold tracking-wide">Loading dock logs and camera reports...</p>
      </div>
    );
  }

  const pieData = [
    { name: 'Critical', value: summary?.critical || 8, color: '#ef4444' },
    { name: 'High Risk', value: summary?.highRisk || 54, color: '#f97316' },
    { name: 'Caution', value: 142, color: '#f59e0b' },
    { name: 'Safe Handling', value: 224, color: '#10b981' },
  ];

  return (
    <div className="space-y-6 w-full">
      {/* 1. TOP ROW: 4 Elevated Warehouse StatCards Straddling the Canopy */}
      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4 -mt-12 sm:-mt-14 relative z-20">
        <StatCard
          title="Handled Items (30d)"
          value={summary?.totalEvents || 428}
          subtitle="Monitored across 6 active dock bays"
          badge="Throughput"
          badgeType="info"
          variant="blue"
          trend={{ value: 14, isPositive: true, label: 'vs previous 30 days' }}
          miniBars={[
            { label: 'May', value: 310, color: 'bg-blue-400' },
            { label: 'Jun', value: 375, color: 'bg-indigo-400' },
            { label: 'Jul', value: 428, color: 'bg-blue-600' },
          ]}
          chartHeader="Monthly Vol"
        />
        <StatCard
          title="Critical Flags"
          value={summary?.critical || 8}
          subtitle="Requires shift supervisor sign-off"
          badge="8 Open Flags"
          badgeType="danger"
          variant="rose"
          trend={{ value: 25, isPositive: false, label: 'drops reduced vs last week' }}
          miniBars={[
            { label: 'W1', value: 14, color: 'bg-rose-300' },
            { label: 'W2', value: 11, color: 'bg-rose-400' },
            { label: 'W3', value: 8, color: 'bg-rose-500' },
          ]}
          chartHeader="Weekly Trend"
        />
        <StatCard
          title="Active Dock Bays"
          value={`${summary?.activeCameras || 6}/6`}
          subtitle="Loading Bays 1 through 6 streaming"
          badge="All Online"
          badgeType="success"
          variant="emerald"
          miniBars={[
            { label: 'B1-2', value: 92, color: 'bg-emerald-400' },
            { label: 'B3-4', value: 98, color: 'bg-emerald-500' },
            { label: 'B5-6', value: 95, color: 'bg-emerald-600' },
          ]}
          chartHeader="Uptime 100%"
        />
        <StatCard
          title="Safe Handling Rate"
          value={`${summary?.preventionRate || 95.8}%`}
          subtitle="Handled without impact or drop"
          badge="Shift Lead"
          badgeType="success"
          variant="amber"
          trend={{ value: 3.2, isPositive: true, label: 'shift improvement' }}
          miniBars={[
            { label: 'Morn', value: 94, color: 'bg-amber-400' },
            { label: 'Aft', value: 92, color: 'bg-amber-500' },
            { label: 'Eve', value: 96, color: 'bg-amber-600' },
          ]}
          chartHeader="By Shift"
        />
      </div>

      {/* 2. MAIN BENTO GRID: Analytical Trends + Live Dock Stream */}
      <div className="grid grid-cols-1 xl:grid-cols-12 gap-6">
        {/* Left 8 Columns: Trends, Frequent Issues, Bay Matrix, and Shift Checklist */}
        <div className="xl:col-span-8 space-y-6">
          {/* Main 7-Day Trend Chart Card */}
          <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200/80 dark:border-slate-800 shadow-xs hover:shadow-md transition-all p-6">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-4 pb-3 border-b border-slate-100 dark:border-slate-800">
              <div>
                <h2 className="text-base font-bold text-slate-900 dark:text-white tracking-tight">
                  Dock Handling & Damage Risk Trends (Past 7 Days)
                </h2>
                <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                  Daily breakdown of safe placement, cautionary handling, and high-risk flags
                </p>
              </div>
              <button
                onClick={() => navigate('/analytics')}
                className="text-xs font-bold text-purple-600 dark:text-purple-400 hover:underline flex items-center gap-1 self-start sm:self-auto"
              >
                Deep Analytics Report <ArrowUpRight className="w-3.5 h-3.5" />
              </button>
            </div>
            <RiskChart data={trends} />
          </div>

          {/* Grid Row: Frequent Issues & Severity Breakdown Donut */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Top Handling Behaviors Bar Chart */}
            <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200/80 dark:border-slate-800 shadow-xs hover:shadow-md transition-all p-6 flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between mb-3 pb-2 border-b border-slate-100 dark:border-slate-800">
                  <h3 className="text-sm font-bold text-slate-900 dark:text-white">Frequent Handling Issues</h3>
                  <span className="text-[11px] font-mono text-slate-400 dark:text-slate-500">10 categories tracked</span>
                </div>
                <div className="h-52 w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={behaviours.slice(0, 5)} layout="vertical" margin={{ left: 10, right: 10, top: 5, bottom: 5 }}>
                      <XAxis type="number" hide />
                      <YAxis
                        type="category"
                        dataKey="behaviour"
                        tick={{ fontSize: 10, fill: '#64748b' }}
                        width={110}
                        axisLine={false}
                        tickLine={false}
                      />
                      <Tooltip
                        contentStyle={{
                          backgroundColor: '#0f172a',
                          borderColor: '#334155',
                          borderRadius: '12px',
                          fontSize: '12px',
                          color: '#fff',
                        }}
                      />
                      <Bar dataKey="count" radius={[0, 8, 8, 0]}>
                        {behaviours.slice(0, 5).map((entry, index) => (
                          <Cell
                            key={`cell-${index}`}
                            fill={index === 0 ? '#ef4444' : index === 1 ? '#f97316' : '#3b82f6'}
                          />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
              <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-2 font-medium">
                Shift watchout: <span className="text-slate-900 dark:text-white font-bold">{behaviours[0]?.behaviour || 'Product Drop'}</span> is the #1 flagged issue on the floor.
              </p>
            </div>

            {/* Severity Breakdown Donut */}
            <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200/80 dark:border-slate-800 shadow-xs hover:shadow-md transition-all p-6 flex flex-col justify-between">
              <div>
                <div className="flex justify-between items-start mb-2 pb-2 border-b border-slate-100 dark:border-slate-800">
                  <div>
                    <h3 className="text-sm font-bold text-slate-900 dark:text-white">Severity Breakdown</h3>
                    <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">Distribution by risk threshold</p>
                  </div>
                  <span className="text-xs font-mono font-bold text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/60 px-2 py-0.5 rounded-full border border-emerald-200 dark:border-emerald-800">
                    95.8% Safe
                  </span>
                </div>
                <div className="h-44 w-full flex items-center justify-center relative">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={pieData}
                        innerRadius={50}
                        outerRadius={75}
                        paddingAngle={4}
                        dataKey="value"
                      >
                        {pieData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} stroke="#ffffff" strokeWidth={3} />
                        ))}
                      </Pie>
                    </PieChart>
                  </ResponsiveContainer>
                  <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
                    <span className="text-xl font-black text-slate-900 dark:text-white">428</span>
                    <span className="text-[10px] uppercase font-bold text-slate-400 dark:text-slate-500 tracking-wider">Incidents</span>
                  </div>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-2 text-[11px] pt-2 border-t border-slate-100 dark:border-slate-800">
                {pieData.map((item) => (
                  <div key={item.name} className="flex items-center justify-between">
                    <span className="flex items-center gap-1.5 text-slate-600 dark:text-slate-400">
                      <span className="w-2 h-2 rounded-full" style={{ backgroundColor: item.color }} />
                      {item.name}:
                    </span>
                    <span className="font-mono font-bold text-slate-900 dark:text-white">{item.value}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Dock Bay Status Matrix */}
          <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200/80 dark:border-slate-800 shadow-xs hover:shadow-md transition-all p-6">
            <div className="flex items-center justify-between mb-4 pb-3 border-b border-slate-100 dark:border-slate-800">
              <div>
                <h3 className="text-sm font-bold text-slate-900 dark:text-white">Dock Bay Status Overview</h3>
                <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">Current traffic and safety flags across all 6 loading bays</p>
              </div>
              <button
                onClick={() => navigate('/live')}
                className="text-xs font-bold text-purple-600 dark:text-purple-400 hover:underline flex items-center gap-1"
              >
                View Live Grid <ArrowUpRight className="w-3.5 h-3.5" />
              </button>
            </div>
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
              {locations.map((bay, idx) => {
                const isCrit = bay.status === 'critical';
                const isWarn = bay.status === 'warning';
                return (
                  <div
                    key={bay.location || idx}
                    onClick={() => navigate('/video')}
                    className={`p-3.5 rounded-lg border transition-all cursor-pointer hover:scale-[1.02] flex flex-col justify-between h-28 ${
                      isCrit
                        ? 'bg-rose-50/70 dark:bg-rose-950/40 border-rose-200 dark:border-rose-900 hover:bg-rose-50'
                        : isWarn
                        ? 'bg-amber-50/70 dark:bg-amber-950/40 border-amber-200 dark:border-amber-900 hover:bg-amber-50'
                        : 'bg-slate-50/80 dark:bg-slate-800/60 border-slate-200 dark:border-slate-700 hover:bg-slate-100/70'
                    }`}
                  >
                    <div className="flex justify-between items-start">
                      <span className="text-xs font-bold text-slate-900 dark:text-white">{bay.location}</span>
                      <span
                        className={`w-2 h-2 rounded-full ${
                          isCrit ? 'bg-rose-500 animate-ping' : isWarn ? 'bg-amber-400' : 'bg-emerald-500'
                        }`}
                      />
                    </div>
                    <div>
                      <div className="text-lg font-black text-slate-900 dark:text-white font-mono">{bay.events_count}</div>
                      <div className="flex items-center justify-between text-[10px] text-slate-500 dark:text-slate-400 mt-0.5">
                        <span>Risk: {bay.risk_score}</span>
                        <span className={isCrit ? 'text-rose-600 dark:text-rose-400 font-bold' : 'text-slate-500'}>
                          {bay.high_risk_count} Urgent
                        </span>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Shift Safety Action Checklist */}
          <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200/80 dark:border-slate-800 shadow-xs hover:shadow-md transition-all p-6">
            <div className="flex items-center justify-between mb-3 pb-3 border-b border-slate-100 dark:border-slate-800">
              <div>
                <h3 className="text-sm font-bold text-slate-900 dark:text-white">Shift Safety Checklist</h3>
                <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">Supervisor sign-offs and dock safety follow-ups</p>
              </div>
              <span className="text-xs font-bold text-purple-600 dark:text-purple-400 bg-purple-50 dark:bg-purple-950/60 border border-purple-200 dark:border-purple-800 px-2.5 py-1 rounded-full">
                {tasks.filter((t) => !t.completed).length} Pending
              </span>
            </div>

            <div className="space-y-2.5">
              {tasks.map((task) => (
                <div
                  key={task.id}
                  onClick={() => toggleTask(task.id)}
                  className={`p-3 rounded-lg border transition-all flex items-center justify-between gap-3 cursor-pointer ${
                    task.completed
                      ? 'bg-slate-50/60 dark:bg-slate-800/40 border-slate-200/60 dark:border-slate-800 opacity-60'
                      : 'bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-700 hover:border-slate-300'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <input
                      type="checkbox"
                      checked={task.completed}
                      onChange={() => toggleTask(task.id)}
                      className="w-4 h-4 rounded text-purple-600 accent-purple-600 cursor-pointer"
                    />
                    <span
                      className={`text-xs font-medium ${
                        task.completed ? 'line-through text-slate-400 dark:text-slate-500' : 'text-slate-800 dark:text-slate-200'
                      }`}
                    >
                      {task.title}
                    </span>
                  </div>
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 shrink-0">
                    {task.tag}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right 4 Columns: Incident Timeline Feed & Supervisor Chat Card */}
        <div className="xl:col-span-4 space-y-6">
          {/* Live Recent Incident Feed */}
          <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200/80 dark:border-slate-800 shadow-xs hover:shadow-md transition-all p-6 flex flex-col">
            <div className="flex items-center justify-between mb-4 pb-3 border-b border-slate-100 dark:border-slate-800">
              <div>
                <h3 className="text-sm font-bold text-slate-900 dark:text-white">Recent Dock Flags</h3>
                <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">High priority events requiring review</p>
              </div>
              <button
                onClick={() => navigate('/incidents')}
                className="text-xs font-bold text-purple-600 dark:text-purple-400 hover:underline"
              >
                View All
              </button>
            </div>
            <div className="flex-1 overflow-y-auto max-h-[460px]">
              <EventTimeline
                events={events}
                onSelectEvent={() => {
                  navigate('/video');
                }}
              />
            </div>
          </div>

          {/* Supervisor Assistant Quick Access Card */}
          <div className="bg-gradient-to-br from-slate-900 via-purple-950 to-slate-900 text-white rounded-xl p-6 shadow-xl border border-slate-800">
            <div className="flex items-center gap-3 mb-3">
              <div className="w-10 h-10 rounded-xl bg-purple-600 flex items-center justify-center text-white shadow-md shadow-purple-500/30">
                <ShieldCheck className="w-5 h-5" />
              </div>
              <div>
                <h4 className="text-sm font-bold text-white">Shift Supervisor Assistant</h4>
                <p className="text-xs text-purple-300">Dock logs & team coaching</p>
              </div>
            </div>
            <p className="text-xs text-slate-300 leading-relaxed mb-4">
              Ask about today's dock activity, review why a specific event was flagged, or pull talking points for the shift safety huddle.
            </p>
            <button
              onClick={() => navigate('/assistant')}
              className="w-full py-2.5 rounded-lg bg-purple-600 hover:bg-purple-500 text-white text-xs font-bold transition-all shadow-md shadow-purple-600/30 active:scale-95 flex items-center justify-center gap-2"
            >
              Open Shift Chat <ArrowUpRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
