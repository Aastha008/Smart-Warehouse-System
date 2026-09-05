import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  X,
  Bell,
  AlertTriangle,
  CheckCircle2,
  Check,
  MapPin,
  Camera,
  Clock,
  Video,
  Search,
  Filter,
  ShieldAlert,
  ShieldCheck,
  Sparkles
} from 'lucide-react';
import { AlertData, RiskLevel } from '../types';
import RiskBadge from './RiskBadge';

interface AlertsDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  alerts: AlertData[];
  onAcknowledge: (id: string) => Promise<void>;
  onAcknowledgeAll: () => Promise<void>;
}

export default function AlertsDrawer({
  isOpen,
  onClose,
  alerts,
  onAcknowledge,
  onAcknowledgeAll,
}: AlertsDrawerProps) {
  const [filterTab, setFilterTab] = useState<'UNACK' | 'ALL' | 'CRITICAL' | 'HIGH'>('UNACK');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [isAckingAll, setIsAckingAll] = useState<boolean>(false);
  const [ackedIds, setAckedIds] = useState<Set<string>>(new Set());

  const navigate = useNavigate();

  if (!isOpen) return null;

  const safeAlerts = Array.isArray(alerts) ? alerts : [];

  // Effective status considering local optimistic ack
  const isAcked = (alt: AlertData) => alt.acknowledged || ackedIds.has(alt.id);

  const unackCount = safeAlerts.filter((a) => !isAcked(a)).length;
  const critCount = safeAlerts.filter((a) => a.risk_level === 'CRITICAL' && !isAcked(a)).length;
  const highCount = safeAlerts.filter((a) => a.risk_level === 'HIGH' && !isAcked(a)).length;

  const filteredAlerts = safeAlerts.filter((alt) => {
    const ackStatus = isAcked(alt);
    if (filterTab === 'UNACK' && ackStatus) return false;
    if (filterTab === 'CRITICAL' && (alt.risk_level !== 'CRITICAL' || ackStatus)) return false;
    if (filterTab === 'HIGH' && (alt.risk_level !== 'HIGH' || ackStatus)) return false;

    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      const matchLoc = alt.location?.toLowerCase().includes(q);
      const matchMsg = alt.message?.toLowerCase().includes(q);
      const matchType = alt.event_type?.toLowerCase().includes(q);
      const matchCam = alt.camera_id?.toLowerCase().includes(q);
      return matchLoc || matchMsg || matchType || matchCam;
    }

    return true;
  });

  const handleSingleAcknowledge = async (id: string) => {
    setAckedIds((prev) => new Set([...prev, id]));
    await onAcknowledge(id);
  };

  const handleAllAcknowledge = async () => {
    setIsAckingAll(true);
    try {
      const allIds = safeAlerts.map((a) => a.id);
      setAckedIds(new Set(allIds));
      await onAcknowledgeAll();
    } finally {
      setIsAckingAll(false);
    }
  };

  const formatRelativeTime = (isoString?: string) => {
    if (!isoString) return 'Recent';
    try {
      const date = new Date(isoString);
      const diffMs = Date.now() - date.getTime();
      const diffMins = Math.floor(diffMs / 60000);
      if (diffMins < 1) return 'Just now';
      if (diffMins < 60) return `${diffMins}m ago`;
      const diffHours = Math.floor(diffMins / 60);
      if (diffHours < 24) return `${diffHours}h ago`;
      return date.toLocaleDateString();
    } catch {
      return 'Recent';
    }
  };

  return (
    <div className="fixed inset-0 z-50 overflow-hidden">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-slate-900/60 dark:bg-black/80 backdrop-blur-xs transition-opacity animate-in fade-in duration-200"
        onClick={onClose}
      />

      {/* Drawer Container */}
      <div className="fixed inset-y-0 right-0 max-w-full flex pl-10">
        <div className="w-screen max-w-xl bg-white dark:bg-slate-900 shadow-2xl border-l border-slate-200 dark:border-slate-800 flex flex-col animate-in slide-in-from-right duration-300">
          {/* Header */}
          <div className="p-5 border-b border-slate-200 dark:border-slate-800 bg-slate-50/70 dark:bg-slate-900/90">
            <div className="flex items-center justify-between gap-4 mb-3">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-2xl bg-gradient-to-tr from-rose-500 to-amber-500 flex items-center justify-center text-white shadow-md shadow-rose-500/20">
                  <ShieldAlert className="w-5 h-5" />
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <h2 className="text-base font-black text-slate-900 dark:text-white tracking-tight">
                      Active Warehouse Alerts
                    </h2>
                    {unackCount > 0 && (
                      <span className="px-2 py-0.5 rounded-full text-[10px] font-black bg-rose-500 text-white animate-pulse">
                        {unackCount} ACTIVE
                      </span>
                    )}
                  </div>
                  <p className="text-xs text-slate-500 dark:text-slate-400">
                    Real-time field safety detections requiring supervisor acknowledgment
                  </p>
                </div>
              </div>

              <button
                onClick={onClose}
                className="w-8 h-8 rounded-xl bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-500 dark:text-slate-400 flex items-center justify-center transition-colors"
                title="Close Drawer"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Quick Actions & Tabs */}
            <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3 pt-2">
              {/* Filter Tabs */}
              <div className="flex items-center gap-1.5 p-1 bg-slate-200/60 dark:bg-slate-800/80 rounded-xl text-xs font-semibold overflow-x-auto">
                <button
                  onClick={() => setFilterTab('UNACK')}
                  className={`px-3 py-1.5 rounded-lg transition-all ${
                    filterTab === 'UNACK'
                      ? 'bg-white dark:bg-slate-700 text-purple-700 dark:text-purple-300 font-bold shadow-xs'
                      : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
                  }`}
                >
                  Unacknowledged ({unackCount})
                </button>
                <button
                  onClick={() => setFilterTab('CRITICAL')}
                  className={`px-2.5 py-1.5 rounded-lg transition-all ${
                    filterTab === 'CRITICAL'
                      ? 'bg-rose-500 text-white font-bold shadow-xs'
                      : 'text-slate-600 dark:text-slate-400 hover:text-rose-600'
                  }`}
                >
                  Critical ({critCount})
                </button>
                <button
                  onClick={() => setFilterTab('HIGH')}
                  className={`px-2.5 py-1.5 rounded-lg transition-all ${
                    filterTab === 'HIGH'
                      ? 'bg-amber-500 text-white font-bold shadow-xs'
                      : 'text-slate-600 dark:text-slate-400 hover:text-amber-600'
                  }`}
                >
                  High ({highCount})
                </button>
                <button
                  onClick={() => setFilterTab('ALL')}
                  className={`px-2.5 py-1.5 rounded-lg transition-all ${
                    filterTab === 'ALL'
                      ? 'bg-white dark:bg-slate-700 text-purple-700 dark:text-purple-300 font-bold shadow-xs'
                      : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
                  }`}
                >
                  All ({safeAlerts.length})
                </button>
              </div>

              {/* Acknowledge All Button */}
              {unackCount > 0 && (
                <button
                  onClick={handleAllAcknowledge}
                  disabled={isAckingAll}
                  className="px-3.5 py-1.5 rounded-xl bg-purple-600 hover:bg-purple-700 active:scale-95 text-white text-xs font-bold transition-all shadow-xs flex items-center justify-center gap-1.5 shrink-0"
                >
                  <Check className="w-3.5 h-3.5" />
                  <span>{isAckingAll ? 'Acknowledging...' : `Acknowledge All (${unackCount})`}</span>
                </button>
              )}
            </div>

            {/* Search Input */}
            <div className="mt-3 relative">
              <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search alerts by bay, event type, or keywords..."
                className="w-full pl-9 pr-4 py-2 rounded-xl text-xs bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-800 dark:text-slate-200 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-purple-500"
              />
            </div>
          </div>

          {/* Alert Cards List */}
          <div className="flex-1 overflow-y-auto p-5 space-y-3.5 divide-y-0">
            {filteredAlerts.length === 0 ? (
              <div className="h-full flex flex-col items-center justify-center text-center p-8 text-slate-400 dark:text-slate-500">
                <div className="w-16 h-16 rounded-full bg-emerald-50 dark:bg-emerald-950/40 text-emerald-500 flex items-center justify-center mb-3">
                  <ShieldCheck className="w-8 h-8" />
                </div>
                <h3 className="text-sm font-bold text-slate-800 dark:text-slate-200">
                  {filterTab === 'UNACK' && unackCount === 0
                    ? 'All Active Alerts Acknowledged!'
                    : 'No Matching Alerts Found'}
                </h3>
                <p className="text-xs text-slate-500 dark:text-slate-400 max-w-xs mt-1">
                  {filterTab === 'UNACK' && unackCount === 0
                    ? 'All warehouse safety violations have been reviewed by the shift supervisor.'
                    : 'Try changing your search query or filter tab to view other historical events.'}
                </p>
              </div>
            ) : (
              filteredAlerts.map((alt) => {
                const acked = isAcked(alt);
                const isCritical = alt.risk_level === 'CRITICAL';
                return (
                  <div
                    key={alt.id}
                    className={`rounded-2xl border p-4 transition-all duration-150 ${
                      acked
                        ? 'bg-slate-50/60 dark:bg-slate-800/40 border-slate-200/80 dark:border-slate-800 opacity-75'
                        : isCritical
                        ? 'bg-rose-50/40 dark:bg-rose-950/20 border-rose-200 dark:border-rose-900/60 shadow-xs ring-1 ring-rose-400/20'
                        : 'bg-amber-50/40 dark:bg-amber-950/20 border-amber-200 dark:border-amber-900/60 shadow-xs ring-1 ring-amber-400/20'
                    }`}
                  >
                    {/* Top Row: Meta badges */}
                    <div className="flex items-center justify-between gap-2 mb-2">
                      <div className="flex items-center gap-2 flex-wrap">
                        <RiskBadge level={alt.risk_level || 'HIGH'} />
                        <span className="inline-flex items-center gap-1 text-[11px] font-bold text-slate-700 dark:text-slate-300 bg-white dark:bg-slate-800 px-2 py-0.5 rounded-md border border-slate-200 dark:border-slate-700">
                          <MapPin className="w-3 h-3 text-purple-600 dark:text-purple-400 shrink-0" />
                          <span>{alt.location || 'Loading Bay'}</span>
                        </span>
                        {alt.camera_id && (
                          <span className="inline-flex items-center gap-1 text-[10px] font-semibold text-slate-500 dark:text-slate-400 bg-white dark:bg-slate-800 px-1.5 py-0.5 rounded border border-slate-200 dark:border-slate-700">
                            <Camera className="w-2.5 h-2.5" />
                            <span>{alt.camera_id}</span>
                          </span>
                        )}
                      </div>

                      <span className="text-[11px] text-slate-400 flex items-center gap-1 shrink-0 font-mono">
                        <Clock className="w-3 h-3" />
                        {formatRelativeTime(alt.timestamp)}
                      </span>
                    </div>

                    {/* Alert Message */}
                    <p className="text-xs font-semibold text-slate-900 dark:text-slate-100 leading-relaxed mb-3">
                      {alt.message}
                    </p>

                    {/* Action Footer */}
                    <div className="flex items-center justify-between gap-2 pt-2 border-t border-slate-100 dark:border-slate-800/80">
                      <button
                        onClick={() => {
                          onClose();
                          navigate('/video');
                        }}
                        className="inline-flex items-center gap-1.5 text-[11px] font-bold text-purple-600 dark:text-purple-400 hover:underline"
                      >
                        <Video className="w-3.5 h-3.5" />
                        <span>Inspect CCTV Footage</span>
                      </button>

                      {acked ? (
                        <span className="inline-flex items-center gap-1 text-[11px] font-bold text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/40 px-2 py-1 rounded-lg">
                          <CheckCircle2 className="w-3.5 h-3.5" />
                          <span>Acknowledged</span>
                        </span>
                      ) : (
                        <button
                          onClick={() => handleSingleAcknowledge(alt.id)}
                          className="inline-flex items-center gap-1 px-3 py-1 rounded-xl bg-slate-900 dark:bg-white text-white dark:text-slate-900 text-xs font-bold hover:bg-purple-700 dark:hover:bg-purple-100 transition-all active:scale-95 shadow-xs"
                        >
                          <Check className="w-3 h-3" />
                          <span>Acknowledge</span>
                        </button>
                      )}
                    </div>
                  </div>
                );
              })
            )}
          </div>

          {/* Footer */}
          <div className="p-4 border-t border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900 flex items-center justify-between text-xs text-slate-500">
            <span>
              Showing {filteredAlerts.length} of {safeAlerts.length} alerts
            </span>
            <button
              onClick={() => {
                onClose();
                navigate('/incidents');
              }}
              className="font-bold text-purple-600 dark:text-purple-400 hover:underline"
            >
              Go to Full Incident Table →
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
