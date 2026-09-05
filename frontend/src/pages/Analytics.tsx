import React, { useEffect, useState } from 'react';
import {
  BarChart,
  Bar,
  AreaChart,
  Area,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
  ComposedChart,
  Cell
} from 'recharts';
import {
  BarChart2,
  TrendingUp,
  Clock,
  Layers,
  Calendar,
  ShieldAlert,
  Download,
  Filter,
  Activity
} from 'lucide-react';
import { getTrends, getBehaviours, getLocations } from '../services/api';
import { RiskTrend, BehaviourStats, LocationStats } from '../types';

// Shift distribution data
const shiftData = [
  { shift: 'Morning (06:00 - 14:00)', low: 88, medium: 52, high: 22, critical: 3, total: 165 },
  { shift: 'Afternoon (14:00 - 22:00)', low: 96, medium: 64, high: 28, critical: 4, total: 192 },
  { shift: 'Night (22:00 - 06:00)', low: 40, medium: 26, high: 4, critical: 1, total: 71 },
];

// Hourly 24h distribution
const hourlyData = [
  { hour: '00:00', count: 4 }, { hour: '02:00', count: 6 }, { hour: '04:00', count: 5 },
  { hour: '06:00', count: 18 }, { hour: '08:00', count: 32 }, { hour: '10:00', count: 46 },
  { hour: '12:00', count: 38 }, { hour: '14:00', count: 52 }, { hour: '16:00', count: 48 },
  { hour: '18:00', count: 35 }, { hour: '20:00', count: 24 }, { hour: '22:00', count: 12 },
];

// Risk score histogram
const histogramData = [
  { bracket: '0 - 20 (Minimal)', count: 95, color: '#10b981' },
  { bracket: '21 - 40 (Low)', count: 129, color: '#34d399' },
  { bracket: '41 - 60 (Medium)', count: 142, color: '#f59e0b' },
  { bracket: '61 - 80 (High)', count: 54, color: '#f97316' },
  { bracket: '81 - 100 (Critical)', count: 8, color: '#ef4444' },
];

export default function Analytics() {
  const [trends, setTrends] = useState<RiskTrend[]>([]);
  const [behaviours, setBehaviours] = useState<BehaviourStats[]>([]);
  const [locations, setLocations] = useState<LocationStats[]>([]);
  const [timeRange, setTimeRange] = useState<string>('30d');
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    Promise.all([getTrends(), getBehaviours(), getLocations()]).then(([t, b, l]) => {
      setTrends(t);
      setBehaviours(b);
      setLocations(l);
      setLoading(false);
    });
  }, []);

  // Compute Pareto data (frequency + cumulative %)
  const totalBehaviourEvents = behaviours.reduce((acc, curr) => acc + curr.count, 0) || 428;
  let runningSum = 0;
  const paretoData = behaviours.map((b) => {
    runningSum += b.count;
    const cumPct = Math.round((runningSum / totalBehaviourEvents) * 100);
    return {
      behaviour: b.behaviour,
      count: b.count,
      cumulativePct: cumPct,
    };
  });

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] text-slate-400 gap-3">
        <Activity className="w-8 h-8 text-blue-500 animate-spin" />
        <p className="text-sm font-semibold tracking-wide">Synthesizing deep trend analytics...</p>
      </div>
    );
  }

  return (
    <div className="space-y-8 w-full">
      {/* Top Header & Range Controls */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 pb-4 border-b border-slate-200 dark:border-slate-800">
        <div>
          <h1 className="text-xl font-bold text-slate-900 dark:text-white tracking-tight">Shift Safety Trends & Reports</h1>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            Tracking handling issues across shifts, peak dock hours, and safety improvements across all bays.
          </p>
        </div>

        {/* Time Range Selector */}
        <div className="flex items-center gap-2">
          {['7d', '30d', '90d'].map((range) => (
            <button
              key={range}
              onClick={() => setTimeRange(range)}
              className={`px-3.5 py-1.5 rounded-lg text-xs font-bold transition-all border ${
                timeRange === range
                  ? 'bg-slate-900 text-white border-slate-900 shadow-sm'
                  : 'bg-white dark:bg-slate-800 text-slate-600 dark:text-slate-300 border-slate-200 dark:border-slate-700 hover:bg-slate-50'
              }`}
            >
              {range === '7d' ? 'Past 7 Days' : range === '30d' ? 'Past 30 Days' : 'Quarter to Date'}
            </button>
          ))}
        </div>
      </div>

      {/* Grid Row 1: Shift Distribution & Pareto Chart */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* 1. Incident Distribution by Shift */}
        <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200/90 dark:border-slate-800 shadow-xs hover:shadow-md transition-all p-6">
          <div className="flex items-center justify-between mb-4 pb-3 border-b border-slate-100">
            <div>
              <h2 className="text-sm font-bold text-slate-900">Handling Issues by Work Shift</h2>
              <p className="text-xs text-slate-500">Comparing flags across Morning, Afternoon, and Night crews</p>
            </div>
            <span className="text-xs font-mono text-blue-600 font-bold bg-blue-50 px-2 py-0.5 rounded-full border border-blue-200">3 Shifts</span>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={shiftData} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                <XAxis dataKey="shift" tick={{ fontSize: 11, fill: '#64748b' }} axisLine={{ stroke: '#e2e8f0' }} tickLine={false} />
                <YAxis tick={{ fontSize: 11, fill: '#64748b' }} axisLine={false} tickLine={false} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#0f172a',
                    borderColor: '#334155',
                    borderRadius: '12px',
                    fontSize: '12px',
                    color: '#fff',
                  }}
                />
                <Legend iconType="circle" wrapperStyle={{ fontSize: '11px', paddingTop: '8px' }} />
                <Bar dataKey="critical" name="Critical" fill="#ef4444" stackId="a" />
                <Bar dataKey="high" name="High Risk" fill="#f97316" stackId="a" />
                <Bar dataKey="medium" name="Medium Risk" fill="#f59e0b" stackId="a" />
                <Bar dataKey="low" name="Low Risk" fill="#10b981" stackId="a" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <p className="text-[11px] text-slate-500 mt-3 font-medium">
            Insight: <strong className="text-slate-900">Afternoon Shift (14:00 - 22:00)</strong> accounts for 45% of total events and the highest critical incident concentration.
          </p>
        </div>

        {/* 2. Pareto Chart of Warehouse Behavior Types (80/20 Rule) */}
        <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200/90 dark:border-slate-800 shadow-xs hover:shadow-md transition-all p-6">
          <div className="flex items-center justify-between mb-4 pb-3 border-b border-slate-100 dark:border-slate-800">
            <div>
              <h2 className="text-sm font-bold text-slate-900 dark:text-white">Pareto Analysis of Violations</h2>
              <p className="text-xs text-slate-500 dark:text-slate-400">80/20 Rule: Key drivers behind handling flags</p>
            </div>
            <span className="text-xs font-mono text-amber-700 font-bold bg-amber-50 dark:bg-amber-950/60 px-2 py-0.5 rounded-md border border-amber-200 dark:border-amber-800">Pareto (80%)</span>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <ComposedChart data={paretoData.slice(0, 6)} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                <XAxis dataKey="behaviour" tick={{ fontSize: 9, fill: '#64748b' }} axisLine={{ stroke: '#e2e8f0' }} tickLine={false} />
                <YAxis yAxisId="left" tick={{ fontSize: 11, fill: '#64748b' }} axisLine={false} tickLine={false} />
                <YAxis yAxisId="right" orientation="right" unit="%" domain={[0, 100]} tick={{ fontSize: 11, fill: '#d97706' }} axisLine={false} tickLine={false} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#0f172a',
                    borderColor: '#334155',
                    borderRadius: '8px',
                    fontSize: '12px',
                    color: '#fff',
                  }}
                />
                <Legend verticalAlign="top" align="right" wrapperStyle={{ fontSize: '11px', paddingBottom: '8px' }} />
                <Bar yAxisId="left" dataKey="count" name="Event Count" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                <Line yAxisId="right" type="monotone" dataKey="cumulativePct" name="Cumulative %" stroke="#d97706" strokeWidth={2.5} dot={{ r: 4 }} />
              </ComposedChart>
            </ResponsiveContainer>
          </div>
          <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-3 font-medium">
            Insight: The top 3 behaviors (<strong className="text-slate-900 dark:text-white">Product Drop, Dragging, Unstable Stacking</strong>) account for 55% of all safety violations.
          </p>
        </div>
      </div>

      {/* Grid Row 2: Risk Score Histogram & 24-Hour Time Distribution */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* 3. Risk Score Histogram */}
        <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200/90 dark:border-slate-800 shadow-xs hover:shadow-md transition-all p-6">
          <div className="flex items-center justify-between mb-4 pb-3 border-b border-slate-100 dark:border-slate-800">
            <div>
              <h2 className="text-sm font-bold text-slate-900 dark:text-white">Risk Score Distribution Histogram</h2>
              <p className="text-xs text-slate-500 dark:text-slate-400">Events grouped by composite multi-factor risk score (0-100)</p>
            </div>
            <span className="text-xs font-mono text-emerald-700 font-bold bg-emerald-50 dark:bg-emerald-950/60 px-2 py-0.5 rounded-md border border-emerald-200 dark:border-emerald-800">428 Events</span>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={histogramData} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                <XAxis dataKey="bracket" tick={{ fontSize: 10, fill: '#64748b' }} axisLine={{ stroke: '#e2e8f0' }} tickLine={false} />
                <YAxis tick={{ fontSize: 11, fill: '#64748b' }} axisLine={false} tickLine={false} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#0f172a',
                    borderColor: '#334155',
                    borderRadius: '8px',
                    fontSize: '12px',
                    color: '#fff',
                  }}
                />
                <Bar dataKey="count" name="Events Count" radius={[4, 4, 0, 0]}>
                  {histogramData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
          <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-3 font-medium">
            Distribution: 65% of recorded behaviors remain in the <strong className="text-emerald-600 font-bold">Low-to-Medium</strong> bracket (0-50).
          </p>
        </div>

        {/* 4. 24-Hour Time-of-Day Curve */}
        <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200/90 dark:border-slate-800 shadow-xs hover:shadow-md transition-all p-6">
          <div className="flex items-center justify-between mb-4 pb-3 border-b border-slate-100">
            <div>
              <h2 className="text-sm font-bold text-slate-900">24-Hour Hourly Diurnal Pattern</h2>
              <p className="text-xs text-slate-500">Hourly incident velocity highlighting shift changeover spikes</p>
            </div>
            <span className="text-xs font-mono text-indigo-700 font-bold bg-indigo-50 px-2 py-0.5 rounded-full border border-indigo-200">24 Hours</span>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={hourlyData} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorHourly" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#6366f1" stopOpacity={0.8} />
                    <stop offset="95%" stopColor="#6366f1" stopOpacity={0.05} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                <XAxis dataKey="hour" tick={{ fontSize: 10, fill: '#64748b' }} axisLine={{ stroke: '#e2e8f0' }} tickLine={false} />
                <YAxis tick={{ fontSize: 11, fill: '#64748b' }} axisLine={false} tickLine={false} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#0f172a',
                    borderColor: '#334155',
                    borderRadius: '12px',
                    fontSize: '12px',
                    color: '#fff',
                  }}
                />
                <Area type="monotone" dataKey="count" name="Hourly Events" stroke="#6366f1" strokeWidth={2.5} fill="url(#colorHourly)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
          <p className="text-[11px] text-slate-500 mt-3 font-medium">
            Peak anomaly window occurs between <strong className="text-indigo-600 font-bold">14:00 - 16:00</strong> during cross-dock outbound dispatch rush.
          </p>
        </div>
      </div>
    </div>
  );
}
