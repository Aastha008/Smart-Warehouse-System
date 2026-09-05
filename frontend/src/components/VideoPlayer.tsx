import React, { useRef, useEffect, useState, useCallback } from 'react';
import {
  Play,
  Pause,
  RotateCcw,
  RotateCw,
  Volume2,
  VolumeX,
  Maximize2,
  Repeat,
  Eye,
  EyeOff,
  ChevronLeft,
  ChevronRight,
  AlertTriangle,
  Clock
} from 'lucide-react';
import { Event, FrameAnnotation, RiskLevel, BoundingBox } from '../types';
import RiskBadge from './RiskBadge';

interface VideoPlayerProps {
  url?: string;
  duration?: number;
  events?: Event[];
  annotations?: FrameAnnotation[];
  seekTime?: number | null;
  onTimeUpdate?: (time: number) => void;
  onEventSelected?: (event: Event) => void;
  className?: string;
}

export default function VideoPlayer({
  url,
  duration = 180,
  events = [],
  annotations = [],
  seekTime = null,
  onTimeUpdate,
  onEventSelected,
  className = '',
}: VideoPlayerProps) {
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const containerRef = useRef<HTMLDivElement | null>(null);
  const animationFrameRef = useRef<number | null>(null);

  const [isPlaying, setIsPlaying] = useState<boolean>(false);
  const [currentTime, setCurrentTime] = useState<number>(0);
  const [videoDuration, setVideoDuration] = useState<number>(duration);
  const [playbackRate, setPlaybackRate] = useState<number>(1);
  const [isLooping, setIsLooping] = useState<boolean>(true);
  const [isMuted, setIsMuted] = useState<boolean>(false);
  const [volume, setVolume] = useState<number>(0.8);
  const [showOverlays, setShowOverlays] = useState<boolean>(true);
  const [activeEvent, setActiveEvent] = useState<Event | null>(null);
  const [hoveredMarker, setHoveredMarker] = useState<Event | null>(null);
  const [hoverPosition, setHoverPosition] = useState<{ x: number; y: number } | null>(null);

  // Simulated synthetic playback ticker if no real video URL
  const isSynthetic = !url || url.startsWith('synthetic');

  // Sync duration whenever duration prop changes
  useEffect(() => {
    setVideoDuration(duration);
  }, [duration]);

  // Handle external seek request
  useEffect(() => {
    if (seekTime !== null && seekTime !== undefined) {
      seekTo(seekTime);
    }
  }, [seekTime]);

  const seekTo = (timeInSeconds: number) => {
    const clamped = Math.max(0, Math.min(videoDuration, timeInSeconds));
    setCurrentTime(clamped);
    if (videoRef.current && !isSynthetic) {
      videoRef.current.currentTime = clamped;
    }
    if (onTimeUpdate) {
      onTimeUpdate(clamped);
    }
  };

  // Toggle play/pause
  const togglePlay = () => {
    if (videoRef.current && !isSynthetic) {
      if (videoRef.current.paused) {
        videoRef.current.play().then(() => setIsPlaying(true)).catch(() => setIsPlaying(true));
      } else {
        videoRef.current.pause();
        setIsPlaying(false);
      }
    } else {
      setIsPlaying((prev) => !prev);
    }
  };

  // Speed change
  const handleSpeedChange = (rate: number) => {
    setPlaybackRate(rate);
    if (videoRef.current) {
      videoRef.current.playbackRate = rate;
    }
  };

  // Format seconds to mm:ss
  const formatTime = (secs: number): string => {
    const m = Math.floor(secs / 60);
    const s = Math.floor(secs % 60);
    return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  };

  // Synthetic clock animation loop (only when in synthetic simulation mode)
  useEffect(() => {
    if (!isSynthetic) return; // Real video element handles its own time updates!

    if (!isPlaying) {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
      return;
    }

    let lastTimestamp = performance.now();

    const step = (now: number) => {
      const delta = (now - lastTimestamp) / 1000;
      lastTimestamp = now;

      setCurrentTime((prev) => {
        let next = prev + delta * playbackRate;
        if (next >= videoDuration) {
          if (isLooping) {
            next = 0;
          } else {
            setIsPlaying(false);
            next = videoDuration;
          }
        }
        if (onTimeUpdate) {
          onTimeUpdate(next);
        }
        return next;
      });

      animationFrameRef.current = requestAnimationFrame(step);
    };

    animationFrameRef.current = requestAnimationFrame(step);

    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, [isSynthetic, isPlaying, playbackRate, videoDuration, isLooping, onTimeUpdate]);

  // Determine active event at current timestamp
  useEffect(() => {
    const current = events.find((e) => {
      const start = e.video_start ?? 0;
      const end = e.video_end ?? start + 5;
      return currentTime >= start && currentTime <= end;
    });
    setActiveEvent(current || null);
  }, [currentTime, events]);

  // Canvas overlay rendering for Bounding Boxes and synthetic warehouse visualization
  const renderCanvas = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const width = canvas.width;
    const height = canvas.height;

    // Clear canvas
    ctx.clearRect(0, 0, width, height);

    // If synthetic mode (no real video playing), render high-tech warehouse CCTV backdrop
    if (isSynthetic) {
      // Dark warehouse background with perspective floor grid
      const grad = ctx.createLinearGradient(0, 0, 0, height);
      grad.addColorStop(0, '#0f172a');
      grad.addColorStop(0.4, '#1e293b');
      grad.addColorStop(1, '#090d16');
      ctx.fillStyle = grad;
      ctx.fillRect(0, 0, width, height);

      // Perspective floor lines (loading dock floor)
      ctx.strokeStyle = 'rgba(51, 65, 85, 0.4)';
      ctx.lineWidth = 1;
      const horizon = height * 0.38;

      // Horizontal lines
      for (let y = horizon; y < height; y += (height - horizon) / 8) {
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(width, y);
        ctx.stroke();
      }

      // Vanishing lines
      const vanishX = width * 0.5;
      for (let x = -width * 0.5; x <= width * 1.5; x += width * 0.2) {
        ctx.beginPath();
        ctx.moveTo(vanishX, horizon);
        ctx.lineTo(x, height);
        ctx.stroke();
      }

      // Demarcated Yellow Safety Zone
      ctx.fillStyle = 'rgba(234, 179, 8, 0.08)';
      ctx.strokeStyle = 'rgba(234, 179, 8, 0.6)';
      ctx.lineWidth = 2;
      ctx.setLineDash([8, 4]);
      ctx.beginPath();
      ctx.moveTo(width * 0.25, height * 0.55);
      ctx.lineTo(width * 0.75, height * 0.55);
      ctx.lineTo(width * 0.88, height * 0.92);
      ctx.lineTo(width * 0.12, height * 0.92);
      ctx.closePath();
      ctx.fill();
      ctx.stroke();
      ctx.setLineDash([]);

      // Zone Label
      ctx.fillStyle = 'rgba(234, 179, 8, 0.8)';
      ctx.font = '10px monospace';
      ctx.fillText('DEMARCATED STAGING ZONE — BAY 3', width * 0.26, height * 0.58);

      // Synthetic dynamic objects (worker, forklift, cartons)
      const t = currentTime;

      // 1. Worker Object
      const workerX = width * (0.35 + Math.sin(t * 0.5) * 0.08);
      const workerY = height * (0.45 + Math.cos(t * 0.5) * 0.03);
      const workerW = width * 0.09;
      const workerH = height * 0.38;

      // Draw stylized worker figure
      ctx.fillStyle = '#f97316'; // Hi-vis vest
      ctx.fillRect(workerX + workerW * 0.25, workerY + workerH * 0.25, workerW * 0.5, workerH * 0.4);
      // Hard hat
      ctx.fillStyle = '#eab308';
      ctx.beginPath();
      ctx.arc(workerX + workerW * 0.5, workerY + workerH * 0.15, workerW * 0.2, 0, Math.PI * 2);
      ctx.fill();
      // Legs
      ctx.fillStyle = '#334155';
      ctx.fillRect(workerX + workerW * 0.3, workerY + workerH * 0.65, workerW * 0.16, workerH * 0.35);
      ctx.fillRect(workerX + workerW * 0.54, workerY + workerH * 0.65, workerW * 0.16, workerH * 0.35);

      // 2. Forklift Object
      const flX = width * 0.08;
      const flY = height * 0.42;
      const flW = width * 0.22;
      const flH = height * 0.42;

      ctx.fillStyle = '#eab308'; // yellow body
      ctx.fillRect(flX, flY + flH * 0.3, flW * 0.7, flH * 0.5);
      ctx.fillStyle = '#1e293b'; // mast & cage
      ctx.fillRect(flX + flW * 0.65, flY, flW * 0.08, flH * 0.9);
      ctx.fillRect(flX + flW * 0.72, flY + flH * 0.6, flW * 0.22, flH * 0.08); // forks

      // 3. Staged Pallet Stack
      const palX = width * 0.68;
      const palY = height * 0.52;
      const palW = width * 0.22;
      const palH = height * 0.36;

      ctx.fillStyle = '#854d0e'; // wooden pallet
      ctx.fillRect(palX, palY + palH * 0.82, palW, palH * 0.15);
      // Corrugated cartons
      ctx.fillStyle = '#b45309';
      ctx.fillRect(palX + palW * 0.05, palY + palH * 0.42, palW * 0.42, palH * 0.4);
      ctx.fillRect(palX + palW * 0.52, palY + palH * 0.42, palW * 0.42, palH * 0.4);

      // Dropping / Handled Carton dynamic behavior
      let cartonX = workerX + workerW * 0.6;
      let cartonY = workerY + workerH * 0.35;
      let isDropFrame = false;

      // If active drop scenario between 14s and 18s
      if (t >= 14 && t <= 18) {
        isDropFrame = true;
        const dropProgress = Math.min(1, (t - 14) / 1.5);
        cartonY = workerY + workerH * 0.35 + (height * 0.85 - (workerY + workerH * 0.35)) * (dropProgress * dropProgress);
      }

      ctx.fillStyle = isDropFrame ? '#ef4444' : '#d97706';
      ctx.fillRect(cartonX, cartonY, width * 0.08, height * 0.12);
      ctx.strokeStyle = '#78350f';
      ctx.strokeRect(cartonX, cartonY, width * 0.08, height * 0.12);
    }

    // Overlay Bounding Boxes if enabled
    if (showOverlays) {
      // Find matching frame annotation or build dynamic real-time boxes
      let currentBoxes: BoundingBox[] = [];

      const foundAnn = annotations.find(
        (a) => Math.abs(a.timestamp - currentTime) < 2.0
      );

      const isRollingDrop =
        Boolean(
          url &&
            (url.toLowerCase().includes('rolling') ||
              url.toLowerCase().includes('dropping') ||
              url.toLowerCase().includes('carton'))
        ) ||
        events.some(
          (e) =>
            e.type === 'product_drop' ||
            (e.description &&
              (e.description.toLowerCase().includes('rolling') ||
                e.description.toLowerCase().includes('drop')))
        );

      const isKdPackets =
        !isRollingDrop &&
        (Boolean(
          url &&
            (url.toLowerCase().includes('kd') ||
              url.toLowerCase().includes('packet') ||
              url.toLowerCase().includes('heavy'))
        ) ||
          videoDuration > 25 ||
          events.some(
            (e) =>
              e.type === 'incorrect_stacking' ||
              (e.description && e.description.includes('KD'))
          ));

      if (foundAnn && foundAnn.boxes.length > 0) {
        currentBoxes = foundAnn.boxes;
      } else {
        const t = currentTime;

        if (isRollingDrop) {
          const p = Math.min(1, Math.max(0, (t - 1.5) / 2.5));
          if (t <= 5.5) {
            currentBoxes = [
              {
                id: 'trk-roll-carton-drop',
                label: 'Carton [CRITICAL: Pallet Drop & Impact]',
                track_id: 'C-301',
                bbox: [
                  0.40 - 0.02 * p,
                  0.26 + 0.06 * p,
                  0.58 - 0.02 * p,
                  0.55 + 0.03 * p,
                ] as [number, number, number, number],
                score: 0.98,
                risk_level: 'CRITICAL',
              },
              {
                id: 'trk-roll-worker-push',
                label: 'Operator [Toppling & Dropping Freight]',
                track_id: 'W-01',
                bbox: [0.40, 0.12, 0.54, 0.36] as [number, number, number, number],
                score: 0.97,
                risk_level: 'HIGH',
              },
              {
                id: 'trk-roll-worker-blue',
                label: 'Operator [Light Blue Shirt]',
                track_id: 'W-02',
                bbox: [0.54, 0.22, 0.69, 0.72] as [number, number, number, number],
                score: 0.95,
                risk_level: 'MEDIUM',
              },
              {
                id: 'trk-roll-supervisor',
                label: 'Supervisor [Black Uniform]',
                track_id: 'W-03',
                bbox: [0.58, 0.10, 0.72, 0.44] as [number, number, number, number],
                score: 0.94,
                risk_level: 'LOW',
              },
              {
                id: 'trk-roll-pallet',
                label: 'Base Pallet [Wood]',
                track_id: 'P-105',
                bbox: [0.32, 0.48, 0.64, 0.76] as [number, number, number, number],
                score: 0.96,
                risk_level: 'LOW',
              },
              {
                id: 'trk-roll-staged',
                label: 'Godrej Interio Staged Carton',
                track_id: 'C-302',
                bbox: [0.46, 0.42, 0.62, 0.74] as [number, number, number, number],
                score: 0.94,
                risk_level: 'LOW',
              },
            ];
          } else {
            currentBoxes = [
              {
                id: 'trk-roll-carton-ground',
                label: 'Carton [HIGH: Rolled on Dock Floor]',
                track_id: 'C-301',
                bbox: [0.36, 0.48, 0.54, 0.74] as [number, number, number, number],
                score: 0.96,
                risk_level: 'HIGH',
              },
              {
                id: 'trk-roll-worker-blue2',
                label: 'Operator [Light Blue Shirt]',
                track_id: 'W-02',
                bbox: [0.54, 0.35, 0.71, 0.88] as [number, number, number, number],
                score: 0.96,
                risk_level: 'MEDIUM',
              },
              {
                id: 'trk-roll-pallet-side',
                label: 'Wood Pallet',
                track_id: 'P-105',
                bbox: [0.32, 0.64, 0.58, 0.94] as [number, number, number, number],
                score: 0.94,
                risk_level: 'LOW',
              },
            ];
          }
        } else if (isKdPackets) {
          if (t >= 18.0 && t <= 27.5) {
            // Exact trajectory for 00:23 circled moment
            const p = Math.min(1, Math.max(0, (t - 18.0) / 9.0));
            currentBoxes = [
              {
                id: 'trk-kd-worker',
                label: 'Operator [Dragging KD Packet]',
                track_id: 'W-01',
                bbox: [0.12 - 0.02 * p, 0.06 + 0.02 * p, 0.32 - 0.02 * p, 0.44 + 0.02 * p] as [number, number, number, number],
                score: 0.98,
                risk_level: 'HIGH',
              },
              {
                id: 'trk-kd-packet',
                label: 'KD Packet [Threshold Dragging Hazard]',
                track_id: 'C-201',
                bbox: [0.15 - 0.03 * p, 0.15 + 0.03 * p, 0.42 - 0.03 * p, 0.38 + 0.02 * p] as [number, number, number, number],
                score: 0.97,
                risk_level: 'HIGH',
              },
              {
                id: 'trk-truck-dock',
                label: 'Vehicle Cargo Bed [Dock 09]',
                track_id: 'TR-01',
                bbox: [0.02, 0.04, 0.22, 0.70] as [number, number, number, number],
                score: 0.94,
                risk_level: 'LOW',
              },
              {
                id: 'trk-heavy-box',
                label: 'Heavy Box (Strapped)',
                track_id: 'C-105',
                bbox: [0.58, 0.18, 0.88, 0.54] as [number, number, number, number],
                score: 0.95,
                risk_level: 'LOW',
              },
              {
                id: 'trk-kd-pallet',
                label: 'KD Pallet Staging Area',
                track_id: 'P-104',
                bbox: [0.28, 0.12, 0.68, 0.46] as [number, number, number, number],
                score: 0.91,
                risk_level: 'LOW',
              },
            ];
          } else if (t < 11.0) {
            currentBoxes = [
              {
                id: 'trk-heavy-box',
                label: 'Heavy Box [OVERLOAD: Placed on Top of Packets]',
                track_id: 'C-105',
                bbox: [0.40, 0.18, 0.64, 0.46] as [number, number, number, number],
                score: 0.96,
                risk_level: 'CRITICAL',
              },
              {
                id: 'trk-kd-crush',
                label: 'KD Packets (Crush Hazard Underneath)',
                track_id: 'C-200',
                bbox: [0.22, 0.16, 0.62, 0.62] as [number, number, number, number],
                score: 0.94,
                risk_level: 'HIGH',
              },
              {
                id: 'trk-pallet',
                label: 'Pallet (Wood Base)',
                track_id: 'P-104',
                bbox: [0.20, 0.15, 0.65, 0.65] as [number, number, number, number],
                score: 0.92,
                risk_level: 'LOW',
              },
              {
                id: 'trk-worker-walk',
                label: 'Worker [Blue Shirt]',
                track_id: 'W-01',
                bbox: [0.58, 0.26, 0.75, 0.78] as [number, number, number, number],
                score: 0.96,
                risk_level: 'HIGH',
              },
            ];
          } else if (t >= 11.0 && t < 18.0) {
            currentBoxes = [
              {
                id: 'trk-worker-strap',
                label: 'Worker [Pulling Strap]',
                track_id: 'W-01',
                bbox: [0.72, 0.35, 0.94, 0.78] as [number, number, number, number],
                score: 0.97,
                risk_level: 'HIGH',
              },
              {
                id: 'trk-heavy-box',
                label: 'Heavy Box [Tension Strap Hazard]',
                track_id: 'C-105',
                bbox: [0.60, 0.28, 0.84, 0.64] as [number, number, number, number],
                score: 0.95,
                risk_level: 'HIGH',
              },
              {
                id: 'trk-kd-base',
                label: 'KD Packets [Base Pallet]',
                track_id: 'C-200',
                bbox: [0.35, 0.18, 0.75, 0.60] as [number, number, number, number],
                score: 0.93,
                risk_level: 'LOW',
              },
            ];
          } else {
            currentBoxes = [
              {
                id: 'trk-worker-stow',
                label: 'Operator [Stowing Freight]',
                track_id: 'W-01',
                bbox: [0.10, 0.08, 0.28, 0.46] as [number, number, number, number],
                score: 0.94,
                risk_level: 'MEDIUM',
              },
              {
                id: 'trk-heavy-box',
                label: 'Heavy Box (Strapped)',
                track_id: 'C-105',
                bbox: [0.58, 0.18, 0.88, 0.54] as [number, number, number, number],
                score: 0.95,
                risk_level: 'LOW',
              },
            ];
          }
        } else {
          const isDragging = activeEvent?.type === 'product_dragging' || (t >= 1 && t <= 12);
          const isRolling = activeEvent?.type === 'rough_handling' || (t >= 13 && t <= 22);
          const isDrop = activeEvent?.type === 'product_drop' || (t >= 14 && t <= 18);
          const isUnstable = activeEvent?.type === 'unstable_stacking' || (t >= 32 && t <= 38);

          if (isDragging) {
            // Continuous dynamic tracking matching real CCTV movement across 6 seconds
            const p = Math.min(1, Math.max(0, t / (videoDuration || 6.0)));
            const cartonX1 = 0.34 - 0.08 * p;
            const cartonY1 = 0.44 + 0.16 * p;
            const workerX1 = 0.50 - 0.12 * p;
            const workerY1 = 0.35 + 0.29 * p;

            currentBoxes = [
              {
                id: 'trk-drag-carton',
                label: 'Carton [Dragging on Wet Floor]',
                track_id: 'C-108',
                bbox: [cartonX1, cartonY1, cartonX1 + 0.14, cartonY1 + 0.20] as [number, number, number, number],
                score: 0.95,
                risk_level: 'HIGH',
              },
              {
                id: 'trk-drag-worker',
                label: 'Worker [Dragging Freight]',
                track_id: 'W-04',
                bbox: [workerX1, workerY1, workerX1 + 0.14, Math.min(0.99, workerY1 + 0.34)] as [number, number, number, number],
                score: 0.97,
                risk_level: 'HIGH',
              },
              {
                id: 'trk-truck-worker',
                label: 'Worker [Truck Bed]',
                track_id: 'W-02',
                bbox: [0.56, 0.28, 0.65, 0.50] as [number, number, number, number],
                score: 0.92,
                risk_level: 'LOW',
              },
              {
                id: 'trk-wet-zone',
                label: 'Wet Floor Hazard Zone',
                track_id: 'Z-02',
                bbox: [0.22, 0.60, 0.54, 0.92] as [number, number, number, number],
                score: 0.89,
                risk_level: 'MEDIUM',
              },
            ];
          } else if (isRolling) {
            const progress = Math.min(1, Math.max(0, (t - 13) / 8));
            currentBoxes = [
              {
                id: 'trk-roll-carton',
                label: 'Carton [Rotational Impact x3]',
                track_id: 'C-112',
                bbox: [0.36 + progress * 0.06, 0.48, 0.52 + progress * 0.06, 0.72] as [number, number, number, number],
                score: 0.93,
                risk_level: 'HIGH',
              },
              {
                id: 'trk-roll-worker',
                label: 'Worker [Rolling Freight]',
                track_id: 'W-04',
                bbox: [0.50 + progress * 0.05, 0.38, 0.64 + progress * 0.05, 0.82] as [number, number, number, number],
                score: 0.95,
                risk_level: 'HIGH',
              },
            ];
          } else {
            currentBoxes = [
              {
                id: 'trk-01',
                label: 'Worker',
                track_id: 'W-08',
                bbox: [0.34 + Math.sin(t * 0.5) * 0.08, 0.42, 0.46 + Math.sin(t * 0.5) * 0.08, 0.86] as [number, number, number, number],
                score: 0.97,
                risk_level: isDrop ? 'HIGH' : 'LOW',
              },
              {
                id: 'trk-02',
                label: isDrop ? 'Carton [CRITICAL: High Drop]' : 'Carton Package',
                track_id: 'C-412',
                bbox: (isDrop ? [0.42, 0.55, 0.56, 0.88] : [0.42, 0.48, 0.52, 0.65]) as [number, number, number, number],
                score: 0.94,
                risk_level: isDrop ? 'CRITICAL' : 'LOW',
              },
              {
                id: 'trk-03',
                label: isUnstable ? 'Pallet Stack [HIGH: 18° Tilt]' : 'Pallet Stack (Wood)',
                track_id: 'P-104',
                bbox: [0.65, 0.48, 0.92, 0.92] as [number, number, number, number],
                score: 0.92,
                risk_level: isUnstable ? 'HIGH' : 'LOW',
              },
              {
                id: 'trk-04',
                label: 'Forklift Counterbalance',
                track_id: 'FL-03',
                bbox: [0.06, 0.38, 0.32, 0.88] as [number, number, number, number],
                score: 0.98,
                risk_level: 'LOW',
              },
            ];
          }
        }
      }

      // Draw each bounding box
      currentBoxes.forEach((box) => {
        const [x1, y1, x2, y2] = box.bbox;
        const px = x1 < 1 ? x1 * width : x1;
        const py = y1 < 1 ? y1 * height : y1;
        const pw = (x2 < 1 ? x2 * width : x2) - px;
        const ph = (y2 < 1 ? y2 * height : y2) - py;

        const risk = box.risk_level || 'LOW';
        let strokeColor = '#10b981'; // Green
        let fillColor = 'rgba(16, 185, 129, 0.12)';
        let tagBg = '#059669';

        if (risk === 'CRITICAL') {
          strokeColor = '#ef4444';
          fillColor = 'rgba(239, 68, 68, 0.25)';
          tagBg = '#dc2626';
        } else if (risk === 'HIGH') {
          strokeColor = '#f97316';
          fillColor = 'rgba(249, 115, 22, 0.2)';
          tagBg = '#ea580c';
        } else if (risk === 'MEDIUM') {
          strokeColor = '#f59e0b';
          fillColor = 'rgba(245, 158, 11, 0.15)';
          tagBg = '#d97706';
        }

        // Box border and soft fill
        ctx.fillStyle = fillColor;
        ctx.fillRect(px, py, pw, ph);

        ctx.strokeStyle = strokeColor;
        ctx.lineWidth = 2.5;
        ctx.strokeRect(px, py, pw, ph);

        // Corner brackets for high-tech CV HUD look
        const cornerLen = Math.min(12, pw * 0.2, ph * 0.2);
        ctx.lineWidth = 4;
        // Top-left
        ctx.beginPath();
        ctx.moveTo(px, py + cornerLen);
        ctx.lineTo(px, py);
        ctx.lineTo(px + cornerLen, py);
        ctx.stroke();
        // Top-right
        ctx.beginPath();
        ctx.moveTo(px + pw - cornerLen, py);
        ctx.lineTo(px + pw, py);
        ctx.lineTo(px + pw, py + cornerLen);
        ctx.stroke();
        // Bottom-left
        ctx.beginPath();
        ctx.moveTo(px, py + ph - cornerLen);
        ctx.lineTo(px, py + ph);
        ctx.lineTo(px + cornerLen, py + ph);
        ctx.stroke();
        // Bottom-right
        ctx.beginPath();
        ctx.moveTo(px + pw - cornerLen, py + ph);
        ctx.lineTo(px + pw, py + ph);
        ctx.lineTo(px + pw, py + ph - cornerLen);
        ctx.stroke();

        // Label pill
        const labelText = `[${box.track_id || box.id}] ${box.label} (${Math.round(box.score * 100)}%)`;
        ctx.font = 'bold 11px sans-serif';
        const textWidth = ctx.measureText(labelText).width;

        ctx.fillStyle = tagBg;
        ctx.fillRect(px, Math.max(0, py - 20), textWidth + 12, 20);

        ctx.fillStyle = '#ffffff';
        ctx.fillText(labelText, px + 6, Math.max(14, py - 6));
      });

      // HUD OSD Overlay (Timecode, FPS, Camera ID)
      ctx.fillStyle = 'rgba(0, 0, 0, 0.65)';
      ctx.fillRect(12, 12, 280, 32);
      ctx.fillStyle = '#38bdf8';
      ctx.font = 'bold 12px monospace';
      const isDock09Osd =
        Boolean(
          url &&
            (url.toLowerCase().includes('kd') ||
              url.toLowerCase().includes('packet') ||
              url.toLowerCase().includes('heavy') ||
              url.toLowerCase().includes('rolling') ||
              url.toLowerCase().includes('dropping') ||
              url.toLowerCase().includes('carton') ||
              url.toLowerCase().includes('dock 09'))
        ) ||
        videoDuration > 25 ||
        events.some(
          (e) =>
            e.type === 'incorrect_stacking' ||
            e.type === 'product_drop' ||
            (e.location && e.location.includes('Dock 09')) ||
            (e.description && (e.description.includes('KD') || e.description.includes('dropping')))
        );
      ctx.fillText(
        isDock09Osd
          ? 'DOCK 09 INSIDE | 720p | 30.0 FPS | REC'
          : 'CAM 03 | 1080p | 24.8 FPS | REC',
        20,
        32
      );
    }
  }, [currentTime, duration, isSynthetic, showOverlays, annotations, activeEvent]);

  // Redraw canvas on time change
  useEffect(() => {
    renderCanvas();
  }, [renderCanvas]);

  // Resize canvas to match container aspect ratio
  useEffect(() => {
    const handleResize = () => {
      if (containerRef.current && canvasRef.current) {
        const { clientWidth, clientHeight } = containerRef.current;
        canvasRef.current.width = clientWidth || 800;
        canvasRef.current.height = clientHeight || 450;
        renderCanvas();
      }
    };

    handleResize();
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [renderCanvas]);

  // Jump to next/prev incident
  const jumpToIncident = (direction: 'prev' | 'next') => {
    if (events.length === 0) return;
    const sorted = [...events].sort((a, b) => (a.video_start ?? 0) - (b.video_start ?? 0));
    if (direction === 'next') {
      const nextEvt = sorted.find((e) => (e.video_start ?? 0) > currentTime + 0.5);
      if (nextEvt) {
        seekTo(nextEvt.video_start ?? 0);
        if (onEventSelected) onEventSelected(nextEvt);
      } else {
        seekTo(sorted[0].video_start ?? 0);
        if (onEventSelected) onEventSelected(sorted[0]);
      }
    } else {
      const prevs = sorted.filter((e) => (e.video_start ?? 0) < currentTime - 0.5);
      if (prevs.length > 0) {
        const prevEvt = prevs[prevs.length - 1];
        seekTo(prevEvt.video_start ?? 0);
        if (onEventSelected) onEventSelected(prevEvt);
      }
    }
  };

  return (
    <div
      ref={containerRef}
      className={`relative bg-slate-950 rounded-2xl overflow-hidden shadow-2xl border border-slate-800 flex flex-col group select-none ${className}`}
      style={{ aspectRatio: '16/9' }}
    >
      {/* HTML5 Video element if valid video URL provided */}
      {!isSynthetic && url && (
        <video
          ref={videoRef}
          src={url}
          className="absolute inset-0 w-full h-full object-contain"
          onTimeUpdate={() => {
            if (videoRef.current) {
              setCurrentTime(videoRef.current.currentTime);
              if (onTimeUpdate) onTimeUpdate(videoRef.current.currentTime);
            }
          }}
          onLoadedMetadata={() => {
            if (videoRef.current) {
              setVideoDuration(videoRef.current.duration || duration);
            }
          }}
          onEnded={() => {
            if (isLooping) {
              videoRef.current?.play();
            } else {
              setIsPlaying(false);
            }
          }}
        />
      )}

      {/* Synchronized HTML5 Canvas Overlay */}
      <canvas
        ref={canvasRef}
        className="absolute inset-0 w-full h-full pointer-events-none z-10"
      />

      {/* Active Incident Warning Banner Overlay */}
      {activeEvent && (
        <div className="absolute top-4 right-4 z-20 bg-red-950/90 border border-red-500/80 rounded-xl px-4 py-2.5 shadow-xl backdrop-blur-md flex items-center gap-3 animate-pulse">
          <AlertTriangle className="w-5 h-5 text-red-400 shrink-0" />
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-black uppercase text-red-300 tracking-wider">Active Incident</span>
              <RiskBadge level={activeEvent.riskLevel} />
            </div>
            <p className="text-xs font-semibold text-white mt-0.5">{activeEvent.type.replace(/_/g, ' ').toUpperCase()}</p>
          </div>
        </div>
      )}

      {/* Hover Marker Tooltip */}
      {hoveredMarker && hoverPosition && (
        <div
          className="absolute bottom-16 z-30 bg-slate-900/95 text-white border border-slate-700 rounded-lg p-2.5 text-xs shadow-2xl backdrop-blur pointer-events-none -translate-x-1/2"
          style={{ left: `${hoverPosition.x}px` }}
        >
          <div className="flex items-center gap-2 mb-1">
            <span className="font-mono text-slate-400">{formatTime(hoveredMarker.video_start ?? 0)}</span>
            <RiskBadge level={hoveredMarker.riskLevel} />
          </div>
          <p className="font-semibold text-slate-100">{hoveredMarker.type.replace(/_/g, ' ').toUpperCase()}</p>
          <p className="text-slate-400 text-[11px] truncate max-w-xs">{hoveredMarker.location}</p>
        </div>
      )}

      {/* Video Control Bar & Scrub Timeline */}
      <div className="absolute bottom-0 left-0 right-0 z-20 p-4 bg-gradient-to-t from-slate-950 via-slate-950/80 to-transparent opacity-90 group-hover:opacity-100 transition-opacity">
        {/* Timeline Scrub Bar with Markers */}
        <div
          className="relative w-full h-3 bg-slate-800/90 rounded-full mb-3 cursor-pointer group/timeline hover:h-4 transition-all flex items-center"
          onClick={(e) => {
            const rect = e.currentTarget.getBoundingClientRect();
            const pos = (e.clientX - rect.left) / rect.width;
            seekTo(pos * videoDuration);
          }}
        >
          {/* Played Progress Fill */}
          <div
            className="absolute left-0 top-0 bottom-0 bg-blue-500 rounded-full transition-all"
            style={{ width: `${(currentTime / (videoDuration || 1)) * 100}%` }}
          />

          {/* Scrub Thumb */}
          <div
            className="absolute top-1/2 -translate-y-1/2 w-4 h-4 bg-white rounded-full shadow-lg border-2 border-blue-600 scale-0 group-hover/timeline:scale-100 transition-transform"
            style={{ left: `calc(${(currentTime / (videoDuration || 1)) * 100}% - 8px)` }}
          />

          {/* Color-Coded Event Markers along Timeline */}
          {events.map((evt) => {
            const startSec = evt.video_start ?? 0;
            const pct = Math.min(100, Math.max(0, (startSec / (videoDuration || 1)) * 100));
            const isCrit = evt.riskLevel === 'CRITICAL';
            const isHigh = evt.riskLevel === 'HIGH';

            return (
              <div
                key={evt.id}
                className={`absolute top-1/2 -translate-y-1/2 w-3.5 h-3.5 rounded-full border-2 border-slate-900 cursor-pointer transition-transform hover:scale-150 z-10 ${
                  isCrit ? 'bg-red-500 shadow-red-500/50 shadow-md' : isHigh ? 'bg-orange-500 shadow-orange-500/50 shadow-md' : 'bg-amber-400'
                }`}
                style={{ left: `calc(${pct}% - 6px)` }}
                onClick={(e) => {
                  e.stopPropagation();
                  seekTo(startSec);
                  if (onEventSelected) onEventSelected(evt);
                }}
                onMouseEnter={(e) => {
                  const rect = containerRef.current?.getBoundingClientRect();
                  if (rect) {
                    setHoverPosition({ x: e.clientX - rect.left, y: e.clientY - rect.top });
                  }
                  setHoveredMarker(evt);
                }}
                onMouseLeave={() => setHoveredMarker(null)}
              />
            );
          })}
        </div>

        {/* Lower Controls Row */}
        <div className="flex items-center justify-between text-white text-xs">
          {/* Left: Playback Controls */}
          <div className="flex items-center gap-3">
            <button
              onClick={togglePlay}
              className="w-9 h-9 rounded-xl bg-blue-600 hover:bg-blue-500 text-white flex items-center justify-center transition-transform active:scale-95 shadow-lg shadow-blue-600/30"
              title={isPlaying ? 'Pause (Space)' : 'Play (Space)'}
            >
              {isPlaying ? <Pause className="w-5 h-5 fill-current" /> : <Play className="w-5 h-5 fill-current ml-0.5" />}
            </button>

            <button
              onClick={() => seekTo(currentTime - 5)}
              className="p-1.5 text-slate-300 hover:text-white rounded-lg hover:bg-slate-800/60 transition-colors"
              title="Rewind 5s"
            >
              <RotateCcw className="w-4 h-4" />
            </button>

            <button
              onClick={() => seekTo(currentTime + 5)}
              className="p-1.5 text-slate-300 hover:text-white rounded-lg hover:bg-slate-800/60 transition-colors"
              title="Forward 5s"
            >
              <RotateCw className="w-4 h-4" />
            </button>

            <div className="h-4 w-px bg-slate-800 mx-1" />

            {/* Jump to Incident */}
            <button
              onClick={() => jumpToIncident('prev')}
              className="p-1.5 text-slate-300 hover:text-amber-400 rounded-lg hover:bg-slate-800/60 transition-colors flex items-center gap-1"
              title="Previous Incident Marker"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>

            <button
              onClick={() => jumpToIncident('next')}
              className="p-1.5 text-slate-300 hover:text-amber-400 rounded-lg hover:bg-slate-800/60 transition-colors flex items-center gap-1"
              title="Next Incident Marker"
            >
              <ChevronRight className="w-4 h-4" />
            </button>

            {/* Time Stamp */}
            <div className="flex items-center gap-1.5 font-mono text-slate-300 text-xs ml-2 bg-slate-900/80 px-2.5 py-1 rounded-md border border-slate-800">
              <Clock className="w-3.5 h-3.5 text-blue-400" />
              <span>{formatTime(currentTime)}</span>
              <span className="text-slate-600">/</span>
              <span className="text-slate-500">{formatTime(videoDuration)}</span>
            </div>
          </div>

          {/* Right: Auxiliary Toggles & Speed */}
          <div className="flex items-center gap-3">
            {/* Speed Selector */}
            <div className="flex items-center bg-slate-900/80 rounded-lg p-0.5 border border-slate-800">
              {[0.5, 1, 1.5, 2].map((rate) => (
                <button
                  key={rate}
                  onClick={() => handleSpeedChange(rate)}
                  className={`px-2 py-1 rounded text-[11px] font-semibold transition-colors ${
                    playbackRate === rate ? 'bg-blue-600 text-white shadow' : 'text-slate-400 hover:text-white'
                  }`}
                >
                  {rate}x
                </button>
              ))}
            </div>

            {/* Loop Toggle */}
            <button
              onClick={() => setIsLooping((prev) => !prev)}
              className={`p-1.5 rounded-lg border transition-colors ${
                isLooping
                  ? 'border-blue-500/50 bg-blue-500/20 text-blue-400'
                  : 'border-slate-800 text-slate-400 hover:text-white'
              }`}
              title={isLooping ? 'Looping Enabled' : 'Looping Disabled'}
            >
              <Repeat className="w-4 h-4" />
            </button>

            {/* Overlay AI Bounding Box Toggle */}
            <button
              onClick={() => setShowOverlays((prev) => !prev)}
              className={`p-1.5 rounded-lg border transition-colors ${
                showOverlays
                  ? 'border-emerald-500/50 bg-emerald-500/20 text-emerald-400'
                  : 'border-slate-800 text-slate-400 hover:text-white'
              }`}
              title={showOverlays ? 'Hide AI Bounding Boxes' : 'Show AI Bounding Boxes'}
            >
              {showOverlays ? <Eye className="w-4 h-4" /> : <EyeOff className="w-4 h-4" />}
            </button>

            {/* Volume Toggle */}
            <button
              onClick={() => setIsMuted((prev) => !prev)}
              className="p-1.5 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800/60 transition-colors"
              title={isMuted ? 'Unmute' : 'Mute'}
            >
              {isMuted ? <VolumeX className="w-4 h-4" /> : <Volume2 className="w-4 h-4" />}
            </button>

            {/* Fullscreen Toggle */}
            <button
              onClick={() => {
                if (containerRef.current) {
                  if (document.fullscreenElement) {
                    document.exitFullscreen();
                  } else {
                    containerRef.current.requestFullscreen();
                  }
                }
              }}
              className="p-1.5 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800/60 transition-colors"
              title="Fullscreen"
            >
              <Maximize2 className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
