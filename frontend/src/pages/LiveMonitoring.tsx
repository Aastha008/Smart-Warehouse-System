import React, { useState, useEffect, useRef } from 'react';
import {
  Camera,
  Maximize2,
  AlertCircle,
  ShieldAlert,
  Volume2,
  VolumeX,
  Radio,
  Filter,
  Layers,
  X,
  Activity,
  CheckCircle2,
  Clock
} from 'lucide-react';
import { getLocations, getAlerts, audioAlerts } from '../services/api';
import { LocationStats, AlertData, CameraFeed } from '../types';
import RiskBadge from '../components/RiskBadge';

const defaultFeeds: CameraFeed[] = [
  { id: 'cam_01', name: 'Cam 01 - Dock 1', location: 'Loading Bay 1', status: 'warning', fps: 24.8, resolution: '1080p', active_objects: 5, last_incident: 'Unstable stack detected (18m ago)' },
  { id: 'cam_02', name: 'Cam 02 - Dock 2', location: 'Loading Bay 2', status: 'warning', fps: 24.5, resolution: '1080p', active_objects: 4, last_incident: 'Parcel dragging (42m ago)' },
  { id: 'cam_03', name: 'Cam 03 - Dock 3', location: 'Loading Bay 3', status: 'alert', fps: 25.0, resolution: '1080p', active_objects: 7, last_incident: 'Critical drop 1.45m (4m ago)' },
  { id: 'cam_04', name: 'Cam 04 - Dock 4', location: 'Loading Bay 4', status: 'active', fps: 24.9, resolution: '1080p', active_objects: 3, last_incident: 'Safe operations' },
  { id: 'cam_05', name: 'Cam 05 - Dock 5', location: 'Loading Bay 5', status: 'alert', fps: 24.8, resolution: '1080p', active_objects: 6, last_incident: 'Parcel throw across bench' },
  { id: 'cam_06', name: 'Cam 06 - Dock 6', location: 'Loading Bay 6', status: 'active', fps: 25.1, resolution: '1080p', active_objects: 2, last_incident: 'Normal loading' },
];

export default function LiveMonitoring() {
  const [feeds, setFeeds] = useState<CameraFeed[]>(defaultFeeds);
  const [alerts, setAlerts] = useState<AlertData[]>([]);
  const [filterStatus, setFilterStatus] = useState<string>('ALL');
  const [expandedFeed, setExpandedFeed] = useState<CameraFeed | null>(null);

  useEffect(() => {
    getAlerts().then(setAlerts);
  }, []);

  const filteredFeeds = feeds.filter((f) => {
    if (filterStatus === 'ALL') return true;
    if (filterStatus === 'ALERTS') return f.status === 'alert' || f.status === 'warning';
    return true;
  });

  return (
    <div className="space-y-6 max-w-7xl mx-auto flex flex-col min-h-[calc(100vh-8rem)]">
      {/* Top Header & Alert Banner */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 pb-4 border-b border-slate-800">
        <div>
          <div className="flex items-center gap-2.5">
            <h1 className="text-xl font-bold text-white tracking-tight">Live Dock Bay Cameras</h1>
            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-black bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-ping" />
              6 BAYS LIVE
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-0.5">
            Real-time dock views across Loading Bays 1 through 6 with automated alerts for drops, tilts, and lane obstructions.
          </p>
        </div>

        {/* Filter Controls */}
        <div className="flex items-center gap-2">
          <button
            onClick={() => setFilterStatus('ALL')}
            className={`px-3.5 py-1.5 rounded-full text-xs font-bold transition-all border ${
              filterStatus === 'ALL'
                ? 'bg-slate-900 text-white border-slate-900 shadow-sm'
                : 'bg-white text-slate-600 border-slate-200 hover:bg-slate-50 hover:text-slate-900'
            }`}
          >
            All Feeds (6)
          </button>
          <button
            onClick={() => setFilterStatus('ALERTS')}
            className={`px-3.5 py-1.5 rounded-full text-xs font-bold transition-all border ${
              filterStatus === 'ALERTS'
                ? 'bg-rose-600 text-white border-rose-600 shadow-sm'
                : 'bg-white text-slate-600 border-slate-200 hover:bg-slate-50 hover:text-slate-900'
            }`}
          >
            Attention Needed (4)
          </button>
        </div>
      </div>

      {/* Quick Alerts Banner */}
      {alerts.length > 0 && (
        <div className="bg-white border border-rose-200 rounded-2xl p-4 shadow-xs flex items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-rose-50 border border-rose-200 flex items-center justify-center text-rose-600 shrink-0 animate-pulse">
              <ShieldAlert className="w-5 h-5" />
            </div>
            <div className="text-xs">
              <span className="font-bold text-slate-900">Active Alert Flag: </span>
              <span className="text-slate-600">{alerts[0].message}</span>
            </div>
          </div>
          <button
            onClick={() => audioAlerts.playChime('CRITICAL')}
            className="px-3.5 py-1.5 rounded-full bg-rose-600 hover:bg-rose-700 text-white text-xs font-bold shrink-0 transition-colors shadow-xs"
          >
            Play Alert Sound
          </button>
        </div>
      )}

      {/* Main Grid View */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5 flex-1">
        {filteredFeeds.map((feed, idx) => (
          <LiveCameraCard
            key={feed.id}
            feed={feed}
            index={idx}
            onMaximize={() => setExpandedFeed(feed)}
          />
        ))}
      </div>

      {/* Fullscreen Expanded Camera Modal */}
      {expandedFeed && (
        <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-md flex items-center justify-center p-4">
          <div className="bg-white rounded-3xl border border-slate-200 w-full max-w-4xl shadow-2xl overflow-hidden flex flex-col">
            <div className="p-4 px-6 border-b border-slate-100 flex items-center justify-between bg-slate-900 text-white">
              <div className="flex items-center gap-2">
                <Camera className="w-5 h-5 text-blue-400" />
                <span className="font-bold text-white text-sm">{expandedFeed.name}</span>
                <span className="text-xs text-slate-300">({expandedFeed.location})</span>
              </div>
              <button
                onClick={() => setExpandedFeed(null)}
                className="p-1 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800 transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="p-4 flex-1 bg-slate-950">
              <div className="aspect-video w-full rounded-2xl overflow-hidden relative bg-black">
                <SimulatedLiveCanvas feed={expandedFeed} isExpanded />
              </div>
            </div>

            <div className="p-4 px-6 border-t border-slate-100 bg-slate-50 grid grid-cols-3 gap-4 text-xs">
              <div>
                <span className="text-slate-500 font-bold block">Status:</span>
                <span className="font-semibold text-emerald-600 uppercase">{expandedFeed.status}</span>
              </div>
              <div>
                <span className="text-slate-500 font-bold block">Objects Detected:</span>
                <span className="font-mono text-slate-800 font-semibold">{expandedFeed.active_objects} tracked entities</span>
              </div>
              <div>
                <span className="text-slate-500 font-bold block">Stream Framerate:</span>
                <span className="font-mono text-slate-800 font-semibold">{expandedFeed.fps} FPS</span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// Sub-Component: Live Camera Card Component with Reference Design Card Styling
function LiveCameraCard({
  feed,
  index,
  onMaximize,
}: {
  feed: CameraFeed;
  index: number;
  onMaximize: () => void;
}) {
  const isAlert = feed.status === 'alert';
  const isWarn = feed.status === 'warning';

  return (
    <div
      className={`bg-white rounded-3xl border shadow-xs hover:shadow-md transition-all flex flex-col overflow-hidden group ${
        isAlert
          ? 'border-rose-300 ring-1 ring-rose-200'
          : isWarn
          ? 'border-amber-300'
          : 'border-slate-200/90'
      }`}
    >
      {/* Stream Video / Canvas Rendering */}
      <div className="relative aspect-video bg-black overflow-hidden">
        <SimulatedLiveCanvas feed={feed} />

        {/* Top OSD Bar */}
        <div className="absolute top-2.5 left-2.5 right-2.5 flex items-center justify-between pointer-events-none z-10">
          <div className="flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-black/70 backdrop-blur text-white text-[10px] font-mono font-bold">
            <span className="w-1.5 h-1.5 rounded-full bg-rose-500 animate-pulse" />
            LIVE • {feed.fps} FPS
          </div>

          <span
            className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase backdrop-blur ${
              isAlert
                ? 'bg-rose-600 text-white'
                : isWarn
                ? 'bg-amber-600 text-white'
                : 'bg-emerald-600 text-white'
            }`}
          >
            {feed.status}
          </span>
        </div>

        {/* Hover Action Buttons */}
        <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-2 z-20">
          <button
            onClick={onMaximize}
            className="px-3.5 py-2 rounded-full bg-slate-900 text-white hover:bg-blue-600 transition-colors shadow-lg flex items-center gap-1.5 text-xs font-bold"
          >
            <Maximize2 className="w-3.5 h-3.5" />
            <span>Enlarge Feed</span>
          </button>
        </div>
      </div>

      {/* Stream Information Card Footer */}
      <div className="p-4 bg-white border-t border-slate-100 flex items-center justify-between text-xs">
        <div>
          <div className="flex items-center gap-1.5">
            <Camera className="w-3.5 h-3.5 text-blue-600" />
            <span className="font-bold text-slate-900 text-xs">{feed.name}</span>
          </div>
          <p className="text-[11px] text-slate-500 mt-0.5 truncate max-w-[200px]">
            {feed.last_incident}
          </p>
        </div>
        <div className="text-right font-mono text-[11px] text-slate-500">
          <div className="font-semibold text-slate-800">{feed.active_objects} tracked</div>
          <div className="text-[10px] text-slate-400">{feed.resolution}</div>
        </div>
      </div>
    </div>
  );
}

// Canvas Simulated Animated Live Feed with Bounding Boxes
function SimulatedLiveCanvas({ feed, isExpanded = false }: { feed: CameraFeed; isExpanded?: boolean }) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let frameId: number;
    let time = 0;

    const render = () => {
      time += 0.02;
      const width = (canvas.width = canvas.clientWidth || (isExpanded ? 800 : 400));
      const height = (canvas.height = canvas.clientHeight || (isExpanded ? 450 : 225));

      // Dark warehouse background
      ctx.fillStyle = '#090d16';
      ctx.fillRect(0, 0, width, height);

      // Floor perspective
      ctx.strokeStyle = 'rgba(51, 65, 85, 0.3)';
      ctx.lineWidth = 1;
      const horizon = height * 0.4;
      for (let y = horizon; y < height; y += (height - horizon) / 6) {
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(width, y);
        ctx.stroke();
      }

      // Demarcated bay zone
      ctx.strokeStyle = 'rgba(234, 179, 8, 0.4)';
      ctx.lineWidth = 1.5;
      ctx.strokeRect(width * 0.2, height * 0.5, width * 0.6, height * 0.4);

      // Draw simulated worker
      const wx = width * (0.35 + Math.sin(time + feed.fps) * 0.1);
      const wy = height * 0.45;
      const ww = width * 0.1;
      const wh = height * 0.4;

      // Worker Box
      ctx.strokeStyle = feed.status === 'alert' ? '#ef4444' : '#10b981';
      ctx.lineWidth = 2;
      ctx.strokeRect(wx, wy, ww, wh);

      ctx.fillStyle = feed.status === 'alert' ? '#dc2626' : '#059669';
      ctx.fillRect(wx, Math.max(0, wy - 16), ww + 20, 16);
      ctx.fillStyle = '#ffffff';
      ctx.font = 'bold 9px sans-serif';
      ctx.fillText(feed.status === 'alert' ? '[W-08] Anomaly' : '[W-04] Worker 96%', wx + 4, Math.max(12, wy - 4));

      // Draw simulated forklift or pallet
      const fx = width * 0.65;
      const fy = height * 0.48;
      const fw = width * 0.22;
      const fh = height * 0.38;

      ctx.strokeStyle = '#38bdf8';
      ctx.strokeRect(fx, fy, fw, fh);
      ctx.fillStyle = '#0284c7';
      ctx.fillRect(fx, Math.max(0, fy - 16), fw * 0.7, 16);
      ctx.fillStyle = '#ffffff';
      ctx.fillText('[P-12] Pallet Load', fx + 4, Math.max(12, fy - 4));

      frameId = requestAnimationFrame(render);
    };

    frameId = requestAnimationFrame(render);
    return () => cancelAnimationFrame(frameId);
  }, [feed, isExpanded]);

  return <canvas ref={canvasRef} className="w-full h-full object-cover" />;
}
