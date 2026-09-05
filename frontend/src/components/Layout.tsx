import React, { useState, useEffect } from 'react';
import { NavLink, Outlet, useNavigate, useLocation } from 'react-router-dom';
import {
  LayoutDashboard,
  Video,
  Activity,
  AlertTriangle,
  BarChart2,
  MessageSquare,
  Settings,
  Bell,
  Volume2,
  VolumeX,
  ShieldCheck,
  Zap,
  Search,
  ChevronRight,
  HelpCircle,
  ShieldAlert,
  FileText,
  Mail,
  MoreHorizontal
} from 'lucide-react';
import { getAlerts, audioAlerts, acknowledgeAlert, acknowledgeAllAlerts } from '../services/api';
import { AlertData } from '../types';
import ThemeToggle from './ThemeToggle';
import AlertsDrawer from './AlertsDrawer';

const mainNavItems = [
  { path: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/video', label: 'Video Replay', icon: Video },
  { path: '/live', label: 'Bay Cameras', icon: Activity },
  { path: '/incidents', label: 'Handling Flags', icon: AlertTriangle },
  { path: '/assistant', label: 'Supervisor AI', icon: MessageSquare },
];

const secondaryNavItems = [
  { path: '/analytics', label: 'Shift Trends', icon: BarChart2 },
  { path: '/settings', label: 'Safety Rules', icon: Settings },
];

export default function Layout() {
  const [alerts, setAlerts] = useState<AlertData[]>([]);
  const [soundEnabled, setSoundEnabled] = useState<boolean>(true);
  const [showAlertDropdown, setShowAlertDropdown] = useState<boolean>(false);
  const [isAlertsDrawerOpen, setIsAlertsDrawerOpen] = useState<boolean>(false);
  const [searchQuery, setSearchQuery] = useState<string>('');
  const location = useLocation();
  const navigate = useNavigate();

  useEffect(() => {
    getAlerts()
      .then((res) => setAlerts(Array.isArray(res) ? res : []))
      .catch(() => setAlerts([]));

    const handleOpenDrawer = () => setIsAlertsDrawerOpen(true);
    window.addEventListener('open-alerts-drawer', handleOpenDrawer);
    return () => window.removeEventListener('open-alerts-drawer', handleOpenDrawer);
  }, [location.pathname]);

  const handleAcknowledgeAlert = async (id: string) => {
    setAlerts((prev) =>
      prev.map((a) => (a.id === id ? { ...a, acknowledged: true } : a))
    );
    await acknowledgeAlert(id);
  };

  const handleAcknowledgeAllAlerts = async () => {
    setAlerts((prev) => prev.map((a) => ({ ...a, acknowledged: true })));
    await acknowledgeAllAlerts();
  };

  const toggleSound = () => {
    const next = !soundEnabled;
    setSoundEnabled(next);
    audioAlerts.setSoundEnabled(next);
    if (next) {
      audioAlerts.playChime('LOW');
    }
  };

  const safeAlerts = Array.isArray(alerts) ? alerts : [];
  const unackAlerts = safeAlerts.filter((a) => a && !a.acknowledged);

  return (
    <div className="min-h-screen bg-[#EEF2F6] dark:bg-slate-950 text-slate-800 dark:text-slate-100 font-sans antialiased p-2 sm:p-4 lg:p-6 flex items-center justify-center transition-colors duration-200">
      {/* Outer Floating Island Card Canvas */}
      <div className="w-full max-w-[1720px] min-h-[940px] bg-white dark:bg-slate-900 rounded-[36px] shadow-[0_24px_70px_-15px_rgba(15,23,42,0.12)] dark:shadow-[0_24px_70px_-15px_rgba(0,0,0,0.5)] border border-slate-200/60 dark:border-slate-800 overflow-hidden flex flex-col md:flex-row relative transition-colors duration-200">
        {/* Left Integrated Sidebar */}
        <aside className="w-64 bg-white dark:bg-slate-900 border-r border-slate-100 dark:border-slate-800/80 flex flex-col justify-between shrink-0 p-5 z-30 transition-colors duration-200">
          <div>
            {/* Brand Logo & Name */}
            <div className="h-12 flex items-center px-2 gap-3 mb-6">
              <div className="w-9 h-9 rounded-2xl bg-gradient-to-tr from-[#5136B0] to-[#884FC1] flex items-center justify-center text-white shadow-md shadow-purple-500/25">
                <Zap className="w-5 h-5 fill-current" />
              </div>
              <div>
                <span className="font-black text-base tracking-tight text-slate-900 dark:text-white block leading-tight">
                  DockGuard
                </span>
                <span className="text-[10px] font-bold text-purple-600 dark:text-purple-400 uppercase tracking-wider block">
                  Warehouse AI
                </span>
              </div>
            </div>

            {/* Main Navigation Section */}
            <div className="px-2 pb-2 text-[11px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-wider">
              Main Navigation
            </div>
            <nav className="flex flex-col gap-1 mb-6">
              {mainNavItems.map((item) => (
                <NavLink
                  key={item.path}
                  to={item.path}
                  className={({ isActive }) =>
                    `flex items-center justify-between px-3.5 py-2.5 rounded-2xl text-xs font-semibold transition-all duration-150 ${
                      isActive
                        ? 'bg-purple-50 dark:bg-purple-950/60 text-purple-700 dark:text-purple-300 font-bold shadow-xs'
                        : 'text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800/60 hover:text-slate-900 dark:hover:text-white'
                    }`
                  }
                >
                  <div className="flex items-center gap-3">
                    <item.icon className="w-4 h-4 text-slate-400 dark:text-slate-500 group-hover:text-slate-600" />
                    <span>{item.label}</span>
                  </div>
                  <ChevronRight className="w-3.5 h-3.5 text-slate-300 dark:text-slate-600" />
                </NavLink>
              ))}
            </nav>

            {/* Settings & Schedules Section */}
            <div className="px-2 pb-2 text-[11px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-wider">
              Settings & Reports
            </div>
            <nav className="flex flex-col gap-1">
              {secondaryNavItems.map((item) => (
                <NavLink
                  key={item.path}
                  to={item.path}
                  className={({ isActive }) =>
                    `flex items-center justify-between px-3.5 py-2.5 rounded-2xl text-xs font-semibold transition-all duration-150 ${
                      isActive
                        ? 'bg-purple-50 dark:bg-purple-950/60 text-purple-700 dark:text-purple-300 font-bold shadow-xs'
                        : 'text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800/60 hover:text-slate-900 dark:hover:text-white'
                    }`
                  }
                >
                  <div className="flex items-center gap-3">
                    <item.icon className="w-4 h-4 text-slate-400 dark:text-slate-500" />
                    <span>{item.label}</span>
                  </div>
                  <ChevronRight className="w-3.5 h-3.5 text-slate-300 dark:text-slate-600" />
                </NavLink>
              ))}
            </nav>
          </div>

          {/* Bottom Warm Amber Help & SOP Card */}
          <div className="relative mt-auto bg-gradient-to-b from-[#F9C35A] to-[#F5AE38] rounded-2xl p-4 text-center text-slate-900 pt-6 shadow-sm">
            <div className="absolute -top-3.5 left-1/2 -translate-x-1/2 w-8 h-8 rounded-full bg-white text-[#EA580C] shadow-md flex items-center justify-center font-black text-sm border-2 border-[#F9C35A]">
              ?
            </div>
            <h4 className="text-xs font-bold text-slate-950 mb-0.5">Floor Safety SOP</h4>
            <p className="text-[10px] text-amber-950/80 leading-snug mb-3">
              Floor supervisors standard operating procedures, fork protocols & drop limits.
            </p>
            <button
              onClick={() => navigate('/settings')}
              className="w-full bg-white hover:bg-slate-50 text-slate-900 py-1.5 px-3 rounded-xl text-xs font-bold shadow-xs transition-colors"
            >
              View Safety Rules
            </button>
          </div>
        </aside>

        {/* Right Stage Workspace */}
        <div className="flex-1 flex flex-col min-w-0 bg-white dark:bg-slate-900 overflow-y-auto transition-colors duration-200">
          {/* The Signature Purple Gradient Canopy Header */}
          <header className="bg-gradient-to-r from-[#443896] via-[#6348B1] to-[#884FC1] dark:from-[#2a1d63] dark:via-[#422985] dark:to-[#5e2e8e] text-white px-8 pt-7 pb-28 shrink-0 relative transition-colors duration-300">
            {/* Ambient Background Glow Circles */}
            <div className="absolute -top-24 -right-24 w-96 h-96 bg-white/5 rounded-full blur-2xl pointer-events-none" />
            <div className="absolute top-1/2 left-1/3 w-64 h-64 bg-purple-400/10 rounded-full blur-xl pointer-events-none" />

            <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-4 relative z-10">
              {/* Left Search Bar (Translucent Glass Pill) */}
              <div className="relative w-72 sm:w-80">
                <Search className="w-3.5 h-3.5 text-white/70 absolute left-3.5 top-1/2 -translate-y-1/2" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search cargo, bays, events..."
                  className="w-full pl-9 pr-4 py-2 bg-white/15 backdrop-blur-md border border-white/20 text-white placeholder:text-white/65 rounded-xl text-xs focus:outline-none focus:bg-white/25 focus:border-white/40 transition-all shadow-inner"
                />
              </div>

              {/* Center / Right Utility Links & Operator Profile */}
              <div className="flex items-center gap-5 w-full lg:w-auto justify-between lg:justify-end">
                {/* Center Icons */}
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => navigate('/video')}
                    className="w-8 h-8 rounded-xl bg-white/10 hover:bg-white/20 backdrop-blur-sm border border-white/15 flex items-center justify-center text-white text-xs transition-colors"
                    title="Video Clips"
                  >
                    <FileText className="w-3.5 h-3.5" />
                  </button>

                  {/* Dark Mode / Light Mode / System Default Toggle */}
                  <ThemeToggle />

                  {/* Audio Chime Toggle */}
                  <button
                    onClick={toggleSound}
                    className="w-8 h-8 rounded-xl bg-white/10 hover:bg-white/20 backdrop-blur-sm border border-white/15 flex items-center justify-center text-white text-xs transition-colors"
                    title={soundEnabled ? 'Web Audio Alerts Enabled' : 'Audio Alerts Muted'}
                  >
                    {soundEnabled ? <Volume2 className="w-3.5 h-3.5" /> : <VolumeX className="w-3.5 h-3.5" />}
                  </button>

                    {/* Notification Bell Dropdown */}
                    <div className="relative">
                      <button
                        onClick={() => setShowAlertDropdown((prev) => !prev)}
                        className="w-8 h-8 rounded-xl bg-white/10 hover:bg-white/20 backdrop-blur-sm border border-white/15 flex items-center justify-center text-white text-xs transition-colors relative"
                        title="Warehouse Safety Alerts"
                      >
                        <Bell className="w-3.5 h-3.5" />
                        {unackAlerts.length > 0 && (
                          <span className="absolute -top-1 -right-1 w-4 h-4 bg-rose-500 text-white rounded-full text-[9px] font-black flex items-center justify-center animate-bounce">
                            {unackAlerts.length}
                          </span>
                        )}
                      </button>

                      {showAlertDropdown && (
                        <div className="absolute right-0 mt-2 w-88 bg-slate-900 border border-slate-700 rounded-2xl shadow-2xl p-4 z-50 text-xs text-slate-100 animate-in fade-in zoom-in-95 duration-150">
                          <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                            <div className="flex items-center gap-2">
                              <span className="font-bold text-white">Active Alerts ({unackAlerts.length})</span>
                              {unackAlerts.length > 0 && (
                                <span className="w-2 h-2 rounded-full bg-rose-500 animate-ping" />
                              )}
                            </div>
                            <button
                              onClick={() => {
                                setShowAlertDropdown(false);
                                setIsAlertsDrawerOpen(true);
                              }}
                              className="text-purple-400 hover:text-purple-300 font-bold hover:underline text-[11px] flex items-center gap-0.5 cursor-pointer"
                            >
                              View All ({safeAlerts.length}) →
                            </button>
                          </div>

                          <div className="divide-y divide-slate-800/80 max-h-72 overflow-y-auto py-2 pr-1 space-y-1">
                            {safeAlerts.length === 0 ? (
                              <div className="py-6 text-center text-slate-500 text-xs">No active alerts</div>
                            ) : (
                              safeAlerts.map((alt) => {
                                const isAck = alt.acknowledged;
                                return (
                                  <div
                                    key={alt.id}
                                    onClick={() => {
                                      setShowAlertDropdown(false);
                                      setIsAlertsDrawerOpen(true);
                                    }}
                                    className={`py-2 px-2.5 rounded-xl cursor-pointer transition-colors space-y-1 ${
                                      isAck
                                        ? 'bg-slate-900/40 opacity-60 hover:opacity-100 hover:bg-slate-800'
                                        : 'hover:bg-slate-800/90 bg-slate-800/30'
                                    }`}
                                  >
                                    <div className="flex justify-between items-center gap-1">
                                      <div className="flex items-center gap-1.5 font-bold text-slate-200">
                                        <span>{alt.location || 'Loading Bay'}</span>
                                        {alt.camera_id && (
                                          <span className="text-[10px] text-slate-400 font-normal">
                                            ({alt.camera_id})
                                          </span>
                                        )}
                                      </div>
                                      <span
                                        className={`px-1.5 py-0.5 rounded text-[9px] font-black ${
                                          alt.risk_level === 'CRITICAL'
                                            ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
                                            : 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                                        }`}
                                      >
                                        {alt.risk_level}
                                      </span>
                                    </div>
                                    <p className="text-slate-400 text-[11px] leading-snug line-clamp-2">
                                      {alt.message}
                                    </p>
                                  </div>
                                );
                              })
                            )}
                          </div>

                          <div className="pt-3 border-t border-slate-800">
                            <button
                              onClick={() => {
                                setShowAlertDropdown(false);
                                setIsAlertsDrawerOpen(true);
                              }}
                              className="w-full py-2.5 rounded-xl bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white font-bold text-center text-xs transition-all flex items-center justify-center gap-2 shadow-lg shadow-purple-600/30 active:scale-95 cursor-pointer"
                            >
                              <ShieldAlert className="w-4 h-4" />
                              <span>Open Full Alerts Center ({unackAlerts.length})</span>
                            </button>
                          </div>
                        </div>
                      )}
                    </div>
                </div>

                <div className="hidden sm:flex items-center gap-4 text-xs font-semibold">
                  <NavLink to="/live" className="text-white/80 hover:text-white transition-colors">
                    Live Bays
                  </NavLink>
                  <NavLink to="/incidents" className="text-white/80 hover:text-white transition-colors">
                    Incident Log
                  </NavLink>
                </div>

                <div className="flex items-center gap-2.5 pl-2">
                  <span className="text-xs font-bold text-white">Hi, Shift Lead</span>
                  <div className="w-8 h-8 rounded-full ring-2 ring-[#FFD043] p-0.5 bg-purple-900 overflow-hidden shrink-0 shadow-sm">
                    <div className="w-full h-full rounded-full bg-gradient-to-tr from-amber-400 to-rose-500 flex items-center justify-center text-white text-[10px] font-black">
                      SL
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </header>

          <main className="px-6 lg:px-10 pb-10 relative z-10">
            <Outlet />
          </main>
        </div>

        <AlertsDrawer
          isOpen={isAlertsDrawerOpen}
          onClose={() => setIsAlertsDrawerOpen(false)}
          alerts={safeAlerts}
          onAcknowledge={handleAcknowledgeAlert}
          onAcknowledgeAll={handleAcknowledgeAllAlerts}
        />
      </div>
    </div>
  );
}
