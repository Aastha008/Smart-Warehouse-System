import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getEvents, getAlerts } from '../services/api';
import { Event, RiskLevel } from '../types';
import RiskBadge from '../components/RiskBadge';
import {
  Search,
  Filter,
  Download,
  Eye,
  Video,
  X,
  ShieldCheck,
  Info,
  Calendar,
  MapPin,
  ChevronLeft,
  ChevronRight,
  Check,
  Bell,
  ShieldAlert
} from 'lucide-react';
import { format } from 'date-fns';

const BEHAVIOUR_TYPES = [
  { value: 'ALL', label: 'All Behaviors' },
  { value: 'product_drop', label: 'Product Drop' },
  { value: 'product_dragging', label: 'Product Dragging' },
  { value: 'product_throwing', label: 'Product Throwing' },
  { value: 'rough_handling', label: 'Rough Handling' },
  { value: 'improper_stacking', label: 'Improper Stacking' },
  { value: 'unstable_stacking', label: 'Unstable Stacking' },
  { value: 'product_outside_zone', label: 'Product Outside Zone' },
  { value: 'incorrect_pallet_position', label: 'Incorrect Pallet Position' },
  { value: 'unsafe_loading_sequence', label: 'Unsafe Loading Sequence' },
  { value: 'improper_handling_equipment', label: 'Improper Equipment' },
];

const LOCATIONS = [
  'ALL',
  'Loading Bay 1',
  'Loading Bay 2',
  'Loading Bay 3',
  'Loading Bay 4',
  'Loading Bay 5',
  'Loading Bay 6',
];

export default function Incidents() {
  const [events, setEvents] = useState<Event[]>([]);
  const [filteredEvents, setFilteredEvents] = useState<Event[]>([]);
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [severityFilter, setSeverityFilter] = useState<string>('ALL');
  const [typeFilter, setTypeFilter] = useState<string>('ALL');
  const [locationFilter, setLocationFilter] = useState<string>('ALL');
  const [selectedIncident, setSelectedIncident] = useState<Event | null>(null);
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [unackAlertsCount, setUnackAlertsCount] = useState<number>(0);
  const itemsPerPage = 8;

  const navigate = useNavigate();

  useEffect(() => {
    getEvents().then((data) => {
      setEvents(data);
      setFilteredEvents(data);
    });
    getAlerts().then((res) => {
      if (Array.isArray(res)) {
        setUnackAlertsCount(res.filter((a) => !a.acknowledged).length);
      }
    });
  }, []);

  // Filter logic
  useEffect(() => {
    let res = [...events];

    if (severityFilter !== 'ALL') {
      res = res.filter((e) => e.riskLevel === severityFilter);
    }
    if (typeFilter !== 'ALL') {
      res = res.filter((e) => e.type === typeFilter || e.event_type === typeFilter);
    }
    if (locationFilter !== 'ALL') {
      res = res.filter((e) => e.location.toLowerCase().includes(locationFilter.toLowerCase()));
    }
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      res = res.filter(
        (e) =>
          e.id.toLowerCase().includes(q) ||
          e.type.toLowerCase().includes(q) ||
          e.location.toLowerCase().includes(q) ||
          (e.description && e.description.toLowerCase().includes(q))
      );
    }

    setFilteredEvents(res);
    setCurrentPage(1);
  }, [events, severityFilter, typeFilter, locationFilter, searchQuery]);

  // Export CSV handler
  const handleExportCSV = () => {
    if (filteredEvents.length === 0) return;

    const headers = [
      'Incident ID',
      'Timestamp',
      'Event Type',
      'Risk Level',
      'Risk Score',
      'Confidence',
      'Location',
      'Camera ID',
      'Description',
      'Explanation',
      'Recommendation',
      'Evidence Payload',
    ];

    const rows = filteredEvents.map((e) => [
      `"${e.id || e.event_id || ''}"`,
      `"${e.timestamp || ''}"`,
      `"${(e.type || e.event_type || '').replace(/_/g, ' ')}"`,
      `"${e.riskLevel || 'LOW'}"`,
      `"${e.risk_score ?? ''}"`,
      `"${e.confidence ? (e.confidence * 100).toFixed(0) + '%' : ''}"`,
      `"${e.location || ''}"`,
      `"${e.camera_id || ''}"`,
      `"${(e.description || '').replace(/"/g, '""')}"`,
      `"${(e.explanation || '').replace(/"/g, '""')}"`,
      `"${(e.recommendation || '').replace(/"/g, '""')}"`,
      `"${JSON.stringify(e.evidence || {}).replace(/"/g, '""')}"`,
    ]);

    const csvContent = [headers.join(','), ...rows.map((r) => r.join(','))].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', `warehouse_incidents_${format(new Date(), 'yyyy-MM-dd_HHmm')}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // Pagination slice
  const totalPages = Math.ceil(filteredEvents.length / itemsPerPage) || 1;
  const paginatedEvents = filteredEvents.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  );

  const selectedEvidence = (typeof selectedIncident?.evidence === 'object'
    ? selectedIncident.evidence
    : {}) as Record<string, any>;

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Top Header & Export Actions */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 pb-4 border-b border-slate-200">
        <div>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight">Dock Handling Incident Log</h1>
          <p className="text-xs text-slate-500 mt-1">
            Review recorded handling events across bays, inspect camera timestamps, and track follow-up coaching.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={handleExportCSV}
            className="px-4 py-2 bg-slate-900 hover:bg-slate-800 rounded-full text-xs font-bold text-white shadow-sm flex items-center gap-2 transition-all active:scale-95"
          >
            <Download className="w-4 h-4" /> Export CSV ({filteredEvents.length})
          </button>
        </div>
      </div>

      {/* Active Alerts Banner */}
      {unackAlertsCount > 0 && (
        <div className="bg-gradient-to-r from-rose-500/10 via-amber-500/10 to-purple-500/10 border border-rose-200 dark:border-rose-900/60 rounded-3xl p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3 shadow-xs">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-2xl bg-rose-500 text-white flex items-center justify-center shadow-md shadow-rose-500/20 shrink-0">
              <ShieldAlert className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-xs font-black text-rose-600 dark:text-rose-400 uppercase tracking-wide">
                  Active Safety Attention Required
                </span>
                <span className="px-2 py-0.5 rounded-full text-[10px] font-black bg-rose-500 text-white animate-pulse">
                  {unackAlertsCount} ACTIVE ALERTS
                </span>
              </div>
              <p className="text-xs text-slate-700 dark:text-slate-300 font-medium mt-0.5">
                {unackAlertsCount} critical handling alerts currently require supervisor review and acknowledgment.
              </p>
            </div>
          </div>
          <button
            onClick={() => window.dispatchEvent(new CustomEvent('open-alerts-drawer'))}
            className="px-4 py-2 rounded-2xl bg-gradient-to-r from-rose-600 to-purple-600 hover:from-rose-500 hover:to-purple-500 text-white font-bold text-xs shadow-md shadow-rose-600/25 active:scale-95 transition-all flex items-center justify-center gap-2 shrink-0 cursor-pointer"
          >
            <Bell className="w-3.5 h-3.5" />
            <span>Open Alerts Center ({unackAlertsCount})</span>
          </button>
        </div>
      )}

      {/* Filter Toolbar */}
      <div className="bg-white border border-slate-200/90 rounded-3xl p-4 shadow-xs grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
        {/* Search Input */}
        <div className="relative">
          <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search ID, type, location..."
            className="w-full pl-10 pr-4 py-2 bg-slate-50 border border-slate-200 rounded-2xl text-xs text-slate-800 placeholder-slate-400 focus:outline-none focus:border-blue-500 focus:bg-white transition-all"
          />
        </div>

        {/* Severity Filter */}
        <div>
          <select
            value={severityFilter}
            onChange={(e) => setSeverityFilter(e.target.value)}
            className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-2xl text-xs text-slate-800 focus:outline-none focus:border-blue-500 focus:bg-white transition-all"
          >
            <option value="ALL">All Severities</option>
            <option value="CRITICAL">Critical Severity</option>
            <option value="HIGH">High Risk</option>
            <option value="MEDIUM">Medium Risk</option>
            <option value="LOW">Low Risk</option>
          </select>
        </div>

        {/* Behavior Type Filter */}
        <div>
          <select
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
            className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-2xl text-xs text-slate-800 focus:outline-none focus:border-blue-500 focus:bg-white transition-all"
          >
            {BEHAVIOUR_TYPES.map((b) => (
              <option key={b.value} value={b.value}>
                {b.label}
              </option>
            ))}
          </select>
        </div>

        {/* Location Filter */}
        <div>
          <select
            value={locationFilter}
            onChange={(e) => setLocationFilter(e.target.value)}
            className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-2xl text-xs text-slate-800 focus:outline-none focus:border-blue-500 focus:bg-white transition-all"
          >
            {LOCATIONS.map((loc) => (
              <option key={loc} value={loc}>
                {loc === 'ALL' ? 'All Loading Bays' : loc}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Incidents Table */}
      <div className="bg-white border border-slate-200/90 rounded-3xl shadow-xs overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-700">
            <thead className="bg-slate-50/90 border-b border-slate-200 text-slate-500 font-bold uppercase tracking-wider text-[10px]">
              <tr>
                <th className="px-6 py-3.5">Incident ID</th>
                <th className="px-6 py-3.5">Timestamp</th>
                <th className="px-6 py-3.5">Behavior Category</th>
                <th className="px-6 py-3.5">Location</th>
                <th className="px-6 py-3.5">Severity</th>
                <th className="px-6 py-3.5">Confidence</th>
                <th className="px-6 py-3.5 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {paginatedEvents.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-6 py-12 text-center text-slate-400">
                    No matching incidents found.
                  </td>
                </tr>
              ) : (
                paginatedEvents.map((evt) => (
                  <tr
                    key={evt.id}
                    onClick={() => setSelectedIncident(evt)}
                    className="hover:bg-slate-800/50 transition-colors cursor-pointer"
                  >
                    <td className="px-6 py-4 font-mono text-blue-600 font-semibold">
                      #{evt.id?.substring(0, 8)}
                    </td>
                    <td className="px-6 py-4 font-mono text-slate-500">
                      {evt.timestamp
                        ? format(new Date(evt.timestamp), 'MMM dd, HH:mm:ss')
                        : 'Today'}
                    </td>
                    <td className="px-6 py-4 font-bold text-slate-900">
                      {(evt.type || evt.event_type || '').replace(/_/g, ' ').toUpperCase()}
                    </td>
                    <td className="px-6 py-4 flex items-center gap-1.5 text-slate-600">
                      <MapPin className="w-3.5 h-3.5 text-slate-400" />
                      {evt.location}
                    </td>
                    <td className="px-6 py-4">
                      <RiskBadge level={evt.riskLevel} />
                    </td>
                    <td className="px-6 py-4 font-mono text-slate-600">
                      {Math.round((evt.confidence || 0.85) * 100)}%
                    </td>
                    <td className="px-6 py-4 text-right">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          setSelectedIncident(evt);
                        }}
                        className="px-3 py-1 rounded-full bg-slate-100 hover:bg-slate-200 text-slate-800 text-xs font-bold inline-flex items-center gap-1 transition-colors border border-slate-200"
                      >
                        <Eye className="w-3.5 h-3.5 text-blue-600" /> Details
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination Bar */}
        <div className="p-4 border-t border-slate-100 bg-slate-50/80 text-xs text-slate-500 flex items-center justify-between">
          <span>
            Showing {Math.min(filteredEvents.length, (currentPage - 1) * itemsPerPage + 1)} to{' '}
            {Math.min(filteredEvents.length, currentPage * itemsPerPage)} of {filteredEvents.length} incidents
          </span>
          <div className="flex items-center gap-1.5">
            <button
              onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
              disabled={currentPage === 1}
              className="p-1.5 rounded-full border border-slate-200 bg-white text-slate-700 hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed shadow-2xs"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <span className="px-3 py-1 font-mono font-bold text-slate-900 text-xs">
              {currentPage} / {totalPages}
            </span>
            <button
              onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
              disabled={currentPage === totalPages}
              className="p-1.5 rounded-full border border-slate-200 bg-white text-slate-700 hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed shadow-2xs"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Incident Detail Inspection Modal */}
      {selectedIncident && (
        <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-md flex items-center justify-center p-4">
          <div className="bg-white border border-slate-200 rounded-3xl w-full max-w-2xl shadow-2xl overflow-hidden flex flex-col animate-in fade-in zoom-in-95 duration-150">
            {/* Modal Header */}
            <div className="p-6 border-b border-slate-800 flex items-center justify-between bg-slate-900 text-white">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-blue-600/20 border border-blue-500/40 flex items-center justify-center text-blue-400">
                  <ShieldCheck className="w-5 h-5" />
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <h3 className="text-base font-bold text-white">
                      {(selectedIncident.type || selectedIncident.event_type || '').replace(/_/g, ' ').toUpperCase()}
                    </h3>
                    <RiskBadge level={selectedIncident.riskLevel} />
                  </div>
                  <p className="text-xs text-slate-400 font-mono mt-0.5">
                    Incident #{selectedIncident.id} • {selectedIncident.location}
                  </p>
                </div>
              </div>
              <button
                onClick={() => setSelectedIncident(null)}
                className="p-1.5 text-slate-400 hover:text-white rounded-xl hover:bg-slate-800 transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Modal Body */}
            <div className="p-6 space-y-5 overflow-y-auto max-h-[70vh]">
              {/* Evidence Metrics Dictionary */}
              <div>
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-2.5 flex items-center gap-1.5">
                  <Info className="w-3.5 h-3.5 text-blue-600" />
                  Extracted Kinetic Evidence Payload
                </h4>
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                  {selectedEvidence.drop_height_m !== undefined && (
                    <div className="bg-slate-50 p-3 rounded-2xl border border-slate-200">
                      <span className="text-[10px] text-slate-500 uppercase font-bold block">Drop Height</span>
                      <span className="text-sm font-black text-rose-600 font-mono">{selectedEvidence.drop_height_m} m</span>
                    </div>
                  )}
                  {selectedEvidence.impact_velocity_mps !== undefined && (
                    <div className="bg-slate-50 p-3 rounded-2xl border border-slate-200">
                      <span className="text-[10px] text-slate-500 uppercase font-bold block">Impact Velocity</span>
                      <span className="text-sm font-black text-orange-600 font-mono">{selectedEvidence.impact_velocity_mps} m/s</span>
                    </div>
                  )}
                  {selectedEvidence.tilt_angle_deg !== undefined && (
                    <div className="bg-slate-50 p-3 rounded-2xl border border-slate-200">
                      <span className="text-[10px] text-slate-500 uppercase font-bold block">Tilt Angle</span>
                      <span className="text-sm font-black text-amber-600 font-mono">{selectedEvidence.tilt_angle_deg}°</span>
                    </div>
                  )}
                  <div className="bg-slate-50 p-3 rounded-2xl border border-slate-200">
                    <span className="text-[10px] text-slate-500 uppercase font-bold block">Risk Score</span>
                    <span className="text-sm font-black text-slate-900 font-mono">{selectedIncident.risk_score ?? 82}/100</span>
                  </div>
                  <div className="bg-slate-50 p-3 rounded-2xl border border-slate-200">
                    <span className="text-[10px] text-slate-500 uppercase font-bold block">Confidence</span>
                    <span className="text-sm font-black text-emerald-600 font-mono">
                      {Math.round((selectedIncident.confidence || 0.85) * 100)}%
                    </span>
                  </div>
                  <div className="bg-slate-50 p-3 rounded-2xl border border-slate-200">
                    <span className="text-[10px] text-slate-500 uppercase font-bold block">Damage Status</span>
                    <span className="text-xs font-bold text-emerald-600">Potential Risk</span>
                  </div>
                </div>
              </div>

              {/* Observed Explanation */}
              <div className="bg-slate-50 p-4 rounded-2xl border border-slate-200 space-y-1">
                <span className="text-[11px] font-bold text-slate-600 uppercase tracking-wider block">
                  Observed Behavior Summary
                </span>
                <p className="text-xs text-slate-700 leading-relaxed">
                  {selectedIncident.explanation || selectedIncident.description}
                </p>
              </div>

              {/* Actionable Recommendation */}
              <div className="bg-blue-50/70 p-4 rounded-2xl border border-blue-200/80 space-y-1">
                <span className="text-[11px] font-bold text-blue-700 uppercase tracking-wider block">
                  Actionable Prevention Recommendation
                </span>
                <p className="text-xs text-slate-700 leading-relaxed">
                  {selectedIncident.recommendation ||
                    'Review safe handling procedures and provide appropriate transport dollies.'}
                </p>
              </div>
            </div>

            {/* Modal Footer */}
            <div className="p-4 px-6 border-t border-slate-100 bg-slate-50 flex items-center justify-between">
              <button
                onClick={() => setSelectedIncident(null)}
                className="px-4 py-2 rounded-full bg-white border border-slate-200 hover:bg-slate-100 text-slate-700 text-xs font-bold transition-colors"
              >
                Close
              </button>
              <button
                onClick={() => {
                  setSelectedIncident(null);
                  navigate('/video');
                }}
                className="px-4 py-2 rounded-full bg-slate-900 hover:bg-slate-800 text-white text-xs font-bold shadow-sm flex items-center gap-2 transition-all active:scale-95"
              >
                <Video className="w-4 h-4" /> Replay in Video Player
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
