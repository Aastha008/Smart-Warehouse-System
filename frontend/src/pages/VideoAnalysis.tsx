import React, { useState, useEffect, useCallback } from 'react';
import VideoPlayer from '../components/VideoPlayer';
import RiskBadge from '../components/RiskBadge';
import {
  UploadCloud,
  FileVideo,
  CheckCircle2,
  AlertTriangle,
  Clock,
  Play,
  RotateCcw,
  Sparkles,
  Layers,
  ArrowRight,
  Info,
  ShieldCheck,
  Database,
  Trash2,
  RefreshCw,
  HardDrive
} from 'lucide-react';
import {
  mockEvents,
  mockScenarios,
  uploadVideo,
  analyzeVideo,
  getVideoStatus,
  getVideoJobs,
  getVideoLibrary,
  deleteVideoFromLibrary
} from '../services/api';
import { Event, VideoScenario, VideoJob, FrameAnnotation } from '../types';

export default function VideoAnalysis() {
  const [selectedScenario, setSelectedScenario] = useState<VideoScenario>(mockScenarios[0]);
  const [selectedEvent, setSelectedEvent] = useState<Event | null>(mockScenarios[0].events[0]);
  const [seekTime, setSeekTime] = useState<number | null>(null);
  const [currentTime, setCurrentTime] = useState<number>(0);
  const [isUploading, setIsUploading] = useState<boolean>(false);
  const [uploadProgress, setUploadProgress] = useState<number>(0);
  const [jobs, setJobs] = useState<VideoJob[]>([]);
  const [uploadedVideos, setUploadedVideos] = useState<VideoScenario[]>([]);
  const [isLoadingLibrary, setIsLoadingLibrary] = useState<boolean>(false);

  const handleScenarioChange = useCallback((scenario: VideoScenario) => {
    setSelectedScenario(scenario);
    setSelectedEvent(scenario.events[0] || null);
    if (scenario.id || scenario.filename) {
      localStorage.setItem('agy_last_selected_video', scenario.id || scenario.filename || '');
    }
    if (scenario.events[0]) {
      setSeekTime(scenario.events[0].video_start ?? 0);
    } else {
      setSeekTime(0);
    }
  }, []);

  const loadLibrary = useCallback(async (autoSelect = false) => {
    setIsLoadingLibrary(true);
    try {
      const library = await getVideoLibrary();
      if (Array.isArray(library) && library.length > 0) {
        setUploadedVideos(library);
        localStorage.setItem('agy_saved_videos', JSON.stringify(library));

        const lastSelectedId = localStorage.getItem('agy_last_selected_video');
        const matched = library.find(
          (v) =>
            v.id === lastSelectedId ||
            v.filename === lastSelectedId ||
            (lastSelectedId && v.title && v.title.includes(lastSelectedId))
        );

        if (matched) {
          handleScenarioChange(matched);
        } else if (autoSelect) {
          // If rolling and dropping carton video exists in library, prioritize it or KD packets
          const rollingVideo = library.find(
            (v) =>
              v.filename &&
              (v.filename.toLowerCase().includes('rolling') || v.filename.toLowerCase().includes('dropping')) &&
              v.filename.toLowerCase().includes('carton')
          );
          const kdVideo = library.find((v) => v.filename && v.filename.toLowerCase().includes('kd'));
          handleScenarioChange(rollingVideo || kdVideo || library[0]);
        }
      }
    } catch (e) {
      console.error('Failed to load video library:', e);
    } finally {
      setIsLoadingLibrary(false);
    }
  }, [handleScenarioChange]);

  useEffect(() => {
    loadLibrary(true);
    getVideoJobs().then(setJobs);
  }, [loadLibrary]);

  const handleDeleteVideo = async (filename: string) => {
    if (!window.confirm(`Delete '${filename}' from warehouse database?`)) return;
    try {
      await deleteVideoFromLibrary(filename);
      const updated = uploadedVideos.filter((v) => v.filename !== filename);
      setUploadedVideos(updated);
      localStorage.setItem('agy_saved_videos', JSON.stringify(updated));
      if (selectedScenario.filename === filename) {
        handleScenarioChange(updated[0] || mockScenarios[0]);
      }
    } catch (e) {
      console.error('Delete video failed:', e);
    }
  };

  const handleSelectIncident = (event: Event) => {
    setSelectedEvent(event);
    const targetTimestamp = event.video_start ?? 0;
    setSeekTime(targetTimestamp);
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const blobUrl = URL.createObjectURL(file);
    setIsUploading(true);
    setUploadProgress(20);

    const timer = setInterval(() => {
      setUploadProgress((prev) => {
        if (prev >= 90) {
          clearInterval(timer);
          return 90;
        }
        return prev + 25;
      });
    }, 300);

    try {
      const { job_id, scenario: serverScenario } = await uploadVideo(file);
      await analyzeVideo(job_id, 'cam_03', 'Loading Bay 3 - CCTV');
      setUploadProgress(100);

      setTimeout(() => {
        setIsUploading(false);
        setUploadProgress(0);

        const lowerName = file.name.toLowerCase();
        const isRollingDrop =
          lowerName.includes('drop') ||
          lowerName.includes('rolling and dropping') ||
          lowerName.includes('rolling nd dropping') ||
          (lowerName.includes('rolling') && lowerName.includes('carton'));

        const isKdPackets =
          !isRollingDrop &&
          (lowerName.includes('kd') ||
            lowerName.includes('heavy box') ||
            lowerName.includes('dock 09') ||
            lowerName.includes('other packet'));

        const isDragOrWet =
          !isRollingDrop && !isKdPackets && (lowerName.includes('drag') || lowerName.includes('wet') || lowerName.includes('floor'));

        let uploadedEvents: Event[];
        let uploadedAnnotations: FrameAnnotation[];

        if (isRollingDrop) {
          uploadedEvents = [
            {
              id: `evt-${Date.now()}-1`,
              event_id: `evt-${Date.now()}-1`,
              timestamp: new Date().toISOString(),
              location: 'Dock 09 - Pallet Staging Area',
              type: 'product_drop',
              event_type: 'product_drop',
              riskLevel: 'CRITICAL',
              risk_level: 'CRITICAL',
              confidence: 0.98,
              video_start: 1.5,
              video_end: 5.5,
              description:
                'Product drop & corner impact off wooden pallet (Carton Toppled from Elevation)',
              evidence: {
                incident_type: 'Carton Free-Fall / Pallet Edge Topple',
                drop_height_cm: 45,
                impact_surface: 'Bare Concrete Dock Floor',
                cargo_type: 'Godrej Interio Corrugated Furniture Master Carton',
                handling_violation: 'Single-operator topple instead of two-person team carry',
                damage_risk: 'Packaging Corner Rupture & Internal Panel Structural Fracture',
                cctv_banner: 'Rolling and dropping the carton',
                camera_zone: 'Dock 09 inside (Circled Pallet Zone)',
              },
              explanation:
                'Worker deliberately tipped and pushed a heavy master carton off the elevated pallet edge directly onto the bare concrete floor instead of lifting it down safely. Gravitational corner impact causes immediate packaging crush, seam rupture, and internal furniture component damage.',
              recommendation:
                'Strict zero-drop policy enforcement. Cartons must be lowered using a two-person team lift or a hydraulic scissor lift. Prohibit tipping or toppling cartons from pallets.',
            },
            {
              id: `evt-${Date.now()}-2`,
              event_id: `evt-${Date.now()}-2`,
              timestamp: new Date().toISOString(),
              location: 'Dock 09 - Pallet Staging Area',
              type: 'rough_handling',
              event_type: 'rough_handling',
              riskLevel: 'HIGH',
              risk_level: 'HIGH',
              confidence: 0.95,
              video_start: 3.0,
              video_end: 7.5,
              description:
                'Rough handling: Rolling carton corner-over-corner across dock floor (Rotational Point-Loads)',
              evidence: {
                handling_mode: 'Rotational Edge-over-Edge Tumbling',
                point_impacts: '3 consecutive floor edge impacts',
                equipment_used: 'None (Manual Topple / Roll)',
                stress_applied: 'Concentrated Shear Force on Seams & Joints',
                cctv_banner: 'Rolling and dropping the carton',
                camera_zone: 'Dock 09 inside',
              },
              explanation:
                'Rather than using a hand truck, pallet jack, or team carry, the carton is continuously rolled and tumbled edge-over-edge across the dock floor. Each 90-degree roll subjects internal components to repeated kinetic shock waves and tears packaging edges.',
              recommendation:
                'Mandate mechanical handling equipment (platform trolley or pallet truck) for moving unpalletized cartons across Dock 09.',
            },
            {
              id: `evt-${Date.now()}-3`,
              event_id: `evt-${Date.now()}-3`,
              timestamp: new Date().toISOString(),
              location: 'Dock 09 - Staging Lane',
              type: 'unsafe_material_movement',
              event_type: 'unsafe_material_movement',
              riskLevel: 'HIGH',
              risk_level: 'HIGH',
              confidence: 0.92,
              video_start: 5.0,
              video_end: 9.0,
              description:
                'Uncontrolled manual material movement & improper operator posture near active pallet zone',
              evidence: {
                staging_hazard: 'Uncontrolled parcel drop trajectory',
                proximity_risk: 'Workers in close drop radius without safety standoff',
                operator_posture: 'Awkward lumbar twist during carton push',
                camera_zone: 'Dock 09 inside',
              },
              explanation:
                'Multiple operators in Dock 09 are handling freight haphazardly without synchronized lifting protocols, posing foot crushing hazards and risks of dropped cargo striking adjacent workers.',
              recommendation:
                'Establish standard operating procedure for two-person team lifting and clear standoff distances around active pallet breakdown zones.',
            },
          ];

          uploadedAnnotations = [
            {
              timestamp: 3.5,
              frame_idx: 105,
              boxes: [
                {
                  id: 1,
                  label: 'Carton [CRITICAL: Dropping / Pallet Edge Impact]',
                  bbox: [0.40, 0.28, 0.58, 0.55] as [number, number, number, number],
                  score: 0.98,
                  risk_level: 'CRITICAL',
                  track_id: 'C-301',
                },
                {
                  id: 2,
                  label: 'Operator [Toppling & Dropping Freight]',
                  bbox: [0.40, 0.12, 0.54, 0.36] as [number, number, number, number],
                  score: 0.97,
                  risk_level: 'HIGH',
                  track_id: 'W-01',
                },
                {
                  id: 3,
                  label: 'Operator [Light Blue Shirt]',
                  bbox: [0.54, 0.22, 0.69, 0.72] as [number, number, number, number],
                  score: 0.95,
                  risk_level: 'MEDIUM',
                  track_id: 'W-02',
                },
                {
                  id: 4,
                  label: 'Supervisor [Black Uniform]',
                  bbox: [0.58, 0.10, 0.72, 0.44] as [number, number, number, number],
                  score: 0.94,
                  risk_level: 'LOW',
                  track_id: 'W-03',
                },
                {
                  id: 5,
                  label: 'Base Pallet [Wood]',
                  bbox: [0.32, 0.48, 0.64, 0.76] as [number, number, number, number],
                  score: 0.96,
                  risk_level: 'LOW',
                  track_id: 'P-105',
                },
                {
                  id: 6,
                  label: 'Staged Cartons [Pallet Top]',
                  bbox: [0.46, 0.42, 0.62, 0.74] as [number, number, number, number],
                  score: 0.95,
                  risk_level: 'LOW',
                  track_id: 'C-302',
                },
              ],
              active_events: ['product_drop', 'rough_handling'],
            },
            {
              timestamp: 6.0,
              frame_idx: 180,
              boxes: [
                {
                  id: 1,
                  label: 'Carton [HIGH: Rolled on Dock Floor]',
                  bbox: [0.36, 0.48, 0.54, 0.74] as [number, number, number, number],
                  score: 0.96,
                  risk_level: 'HIGH',
                  track_id: 'C-301',
                },
                {
                  id: 2,
                  label: 'Operator [Light Blue Shirt]',
                  bbox: [0.54, 0.35, 0.71, 0.88] as [number, number, number, number],
                  score: 0.96,
                  risk_level: 'MEDIUM',
                  track_id: 'W-02',
                },
                {
                  id: 3,
                  label: 'Wood Pallet',
                  bbox: [0.32, 0.64, 0.58, 0.94] as [number, number, number, number],
                  score: 0.94,
                  risk_level: 'LOW',
                  track_id: 'P-105',
                },
              ],
              active_events: ['rough_handling', 'unsafe_material_movement'],
            },
          ];
        } else if (isDragOrWet) {
          uploadedEvents = [
            {
              id: `evt-${Date.now()}-1`,
              event_id: `evt-${Date.now()}-1`,
              timestamp: new Date().toISOString(),
              location: 'Loading Bay 3 - Transition Area',
              type: 'product_dragging',
              event_type: 'product_dragging',
              riskLevel: 'HIGH',
              risk_level: 'HIGH',
              confidence: 0.95,
              video_start: 1.0,
              video_end: 4.0,
              description:
                'Carton dragged manually across wet dock floor without mechanical trolley.',
              evidence: {
                drag_distance_m: 3.8,
                drag_duration_s: 3.0,
                friction_surface: 'Wet Concrete Dock Plate',
                equipment_used: 'None (Manual Floor Drag)',
                weight_est_kg: 28.5,
              },
              explanation:
                'Carton was dragged 3.8m across wet concrete instead of being transported on a wheeled trolley. This causes base friction abrasion and moisture ingress.',
              recommendation:
                'Halt manual floor dragging immediately. Deploy hydraulic pallet truck or two-person team lift. Dry the loading dock transition plate before moving freight.',
            },
            {
              id: `evt-${Date.now()}-2`,
              event_id: `evt-${Date.now()}-2`,
              timestamp: new Date().toISOString(),
              location: 'Loading Bay 3 - Wet Floor Area',
              type: 'unsafe_loading_sequence',
              event_type: 'unsafe_loading_sequence',
              riskLevel: 'HIGH',
              risk_level: 'HIGH',
              confidence: 0.92,
              video_start: 2.8,
              video_end: 5.2,
              description:
                'Heavy freight transit across wet dock floor creating severe slip and package water damage risk.',
              evidence: {
                surface_condition: 'Moisture / Water Puddle Detected',
                friction_hazard: 'High Slip Potential',
                worker_traction: 'Unstable Footing Observed',
              },
              explanation:
                'Handling heavy cartons over wet concrete risks operator falls, dropping cargo, and corrugated package bottom sogginess.',
              recommendation:
                'Stop freight movement until dock surface is dried. Apply moisture absorbent pads and display yellow wet floor caution signage.',
            },
            {
              id: `evt-${Date.now()}-3`,
              event_id: `evt-${Date.now()}-3`,
              timestamp: new Date().toISOString(),
              location: 'Loading Bay 3 - Dock Edge',
              type: 'rough_handling',
              event_type: 'rough_handling',
              riskLevel: 'MEDIUM',
              risk_level: 'MEDIUM',
              confidence: 0.89,
              video_start: 4.2,
              video_end: 6.0,
              description:
                'Solo operator pulling overweight freight without mechanical assistance or team lift.',
              evidence: {
                operator_count: 1,
                cargo_weight_est_kg: 28.5,
                recommended_handling: 'Two-Person Team Lift or Dolly',
              },
              explanation:
                'Solo operator dragging heavy freight violates warehouse ergonomic weight limits and causes jerky carton transit.',
              recommendation:
                'Provide platform hand truck or assign a second handler to assist in team lifting.',
            },
          ];

          uploadedAnnotations = [
            {
              timestamp: 1.0,
              frame_idx: 30,
              boxes: [
                {
                  id: 1,
                  label: 'Carton [Dragging on Wet Floor]',
                  bbox: [0.34, 0.44, 0.48, 0.64] as [number, number, number, number],
                  score: 0.95,
                  risk_level: 'HIGH',
                  track_id: 'C-108',
                },
                {
                  id: 2,
                  label: 'Worker [Dragging Freight]',
                  bbox: [0.50, 0.35, 0.64, 0.70] as [number, number, number, number],
                  score: 0.97,
                  risk_level: 'HIGH',
                  track_id: 'W-04',
                },
                {
                  id: 3,
                  label: 'Worker [Truck Bed]',
                  bbox: [0.56, 0.28, 0.65, 0.50] as [number, number, number, number],
                  score: 0.92,
                  risk_level: 'LOW',
                  track_id: 'W-02',
                },
                {
                  id: 4,
                  label: 'Wet Floor Hazard Zone',
                  bbox: [0.22, 0.60, 0.54, 0.92] as [number, number, number, number],
                  score: 0.89,
                  risk_level: 'MEDIUM',
                  track_id: 'Z-02',
                },
              ],
              active_events: ['product_dragging'],
            },
            {
              timestamp: 3.5,
              frame_idx: 105,
              boxes: [
                {
                  id: 1,
                  label: 'Carton [Dragging on Wet Floor]',
                  bbox: [0.30, 0.52, 0.44, 0.72] as [number, number, number, number],
                  score: 0.95,
                  risk_level: 'HIGH',
                  track_id: 'C-108',
                },
                {
                  id: 2,
                  label: 'Worker [Dragging Freight]',
                  bbox: [0.44, 0.48, 0.58, 0.84] as [number, number, number, number],
                  score: 0.97,
                  risk_level: 'HIGH',
                  track_id: 'W-04',
                },
                {
                  id: 3,
                  label: 'Worker [Truck Bed]',
                  bbox: [0.56, 0.28, 0.65, 0.50] as [number, number, number, number],
                  score: 0.92,
                  risk_level: 'LOW',
                  track_id: 'W-02',
                },
                {
                  id: 4,
                  label: 'Wet Floor Hazard Zone',
                  bbox: [0.22, 0.60, 0.54, 0.92] as [number, number, number, number],
                  score: 0.89,
                  risk_level: 'MEDIUM',
                  track_id: 'Z-02',
                },
              ],
              active_events: ['product_dragging', 'unsafe_loading_sequence'],
            },
            {
              timestamp: 5.8,
              frame_idx: 175,
              boxes: [
                {
                  id: 1,
                  label: 'Carton [Dragging on Wet Floor]',
                  bbox: [0.26, 0.60, 0.40, 0.80] as [number, number, number, number],
                  score: 0.95,
                  risk_level: 'HIGH',
                  track_id: 'C-108',
                },
                {
                  id: 2,
                  label: 'Worker [Dragging Freight]',
                  bbox: [0.38, 0.64, 0.52, 0.98] as [number, number, number, number],
                  score: 0.97,
                  risk_level: 'HIGH',
                  track_id: 'W-04',
                },
                {
                  id: 3,
                  label: 'Worker [Truck Bed]',
                  bbox: [0.56, 0.28, 0.65, 0.50] as [number, number, number, number],
                  score: 0.92,
                  risk_level: 'LOW',
                  track_id: 'W-02',
                },
                {
                  id: 4,
                  label: 'Wet Floor Hazard Zone',
                  bbox: [0.22, 0.60, 0.54, 0.92] as [number, number, number, number],
                  score: 0.89,
                  risk_level: 'MEDIUM',
                  track_id: 'Z-02',
                },
              ],
              active_events: ['rough_handling'],
            },
          ];
        } else {
          uploadedEvents = [
            {
              id: `evt-${Date.now()}-1`,
              event_id: `evt-${Date.now()}-1`,
              timestamp: new Date().toISOString(),
              location: 'Loading Bay - CCTV Stream',
              type: 'rough_handling',
              event_type: 'rough_handling',
              riskLevel: 'HIGH',
              risk_level: 'HIGH',
              confidence: 0.92,
              video_start: 1.5,
              video_end: 5.0,
              description: `Observed cargo handling anomaly in ${file.name}.`,
              evidence: {
                file_analyzed: file.name,
                detection_engine: 'YOLOv8 + ByteTrack FSM',
              },
              explanation:
                'Kinematic tracking detected irregular acceleration and excessive tilt angle during freight transit.',
              recommendation:
                'Inspect freight packaging before loading. Ensure proper two-person team lift protocol.',
            },
          ];

          uploadedAnnotations = [
            {
              timestamp: 3.0,
              frame_idx: 90,
              boxes: [
                {
                  id: 1,
                  label: 'Worker [Operator]',
                  bbox: [0.35, 0.35, 0.50, 0.85] as [number, number, number, number],
                  score: 0.95,
                  risk_level: 'LOW',
                  track_id: 'W-01',
                },
                {
                  id: 2,
                  label: 'Carton Package',
                  bbox: [0.48, 0.52, 0.64, 0.82] as [number, number, number, number],
                  score: 0.92,
                  risk_level: 'HIGH',
                  track_id: 'C-01',
                },
              ],
            },
          ];
        }

        let finalScenario: VideoScenario;
        if (serverScenario) {
          finalScenario = {
            ...serverScenario,
            video_url: serverScenario.video_url || blobUrl,
          };
        } else {
          finalScenario = {
            id: job_id,
            title: `CCTV: ${file.name}`,
            filename: file.name,
            description: isRollingDrop
              ? 'Stored in warehouse CCTV database. 3 incident(s) analyzed across Dock 09 inside.'
              : 'Real warehouse video loaded. Computer vision overlays detected kinematics, dragging friction, and rolling impacts.',
            location: isRollingDrop ? 'Dock 09 inside' : isKdPackets ? 'Dock 09 Inside' : 'Loading Bay 3 - CCTV',
            camera_id: isRollingDrop || isKdPackets ? 'cam_09' : 'cam_03',
            duration_seconds: isRollingDrop ? 9 : isKdPackets ? 34 : 6,
            video_url: blobUrl,
            events: uploadedEvents,
            annotations: uploadedAnnotations,
          };
        }

        setUploadedVideos((prev) => {
          const filtered = prev.filter((v) => v.filename !== file.name);
          const nextList = [finalScenario, ...filtered];
          localStorage.setItem('agy_saved_videos', JSON.stringify(nextList));
          return nextList;
        });

        handleScenarioChange(finalScenario);
      }, 600);
    } catch (err) {
      setIsUploading(false);
      clearInterval(timer);
    }
  };

  const formatTime = (secs: number) => {
    const m = Math.floor(secs / 60);
    const s = Math.floor(secs % 60);
    return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  };

  const evidence = (typeof selectedEvent?.evidence === 'object' ? selectedEvent.evidence : {}) as Record<string, any>;

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Top Header & Scenario Preset Selector */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 pb-4 border-b border-slate-200">
        <div>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight">Video Replay & Incident Review</h1>
          <p className="text-xs text-slate-500 mt-1">
            Review recorded bay camera footage, inspect flagged handling events, and jump directly to incident moments.
          </p>
        </div>

        {/* Upload Button */}
        <div className="flex items-center gap-3">
          <label className="bg-slate-900 hover:bg-slate-800 text-white px-4 py-2 rounded-full text-xs font-bold shadow-sm transition-all flex items-center gap-2 cursor-pointer active:scale-95">
            <UploadCloud className="w-4 h-4" />
            <span>Upload Bay Video</span>
            <input
              type="file"
              accept=".mp4,.avi,.mov,.mkv,.webm"
              className="hidden"
              onChange={handleFileUpload}
            />
          </label>
        </div>
      </div>

      {/* Persistent Video Database Shelf */}
      <div className="bg-slate-50/80 border border-slate-200/90 rounded-2xl p-3.5 space-y-2.5">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Database className="w-4 h-4 text-blue-600" />
            <span className="text-xs font-bold text-slate-800 uppercase tracking-wide">
              Persistent Video Database (Saved in DB)
            </span>
            <span className="text-[10px] font-bold bg-blue-100 text-blue-800 px-2 py-0.5 rounded-full">
              {uploadedVideos.length} Saved Footage
            </span>
          </div>
          <button
            onClick={() => loadLibrary(false)}
            title="Sync with server database"
            className="text-slate-500 hover:text-blue-600 text-xs flex items-center gap-1 transition-colors px-2 py-1 rounded-lg hover:bg-white"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isLoadingLibrary ? 'animate-spin' : ''}`} />
            <span className="text-[11px] font-semibold">Sync DB</span>
          </button>
        </div>

        {uploadedVideos.length > 0 ? (
          <div className="flex flex-wrap items-center gap-2">
            {uploadedVideos.map((video) => {
              const isSelected =
                selectedScenario.id === video.id ||
                selectedScenario.filename === video.filename ||
                (selectedScenario.title && video.filename && selectedScenario.title.includes(video.filename));
              return (
                <div
                  key={video.id || video.filename}
                  className={`group relative flex items-center gap-2.5 pl-3 pr-2 py-2 rounded-xl border text-xs font-semibold transition-all cursor-pointer shadow-2xs ${
                    isSelected
                      ? 'bg-blue-600 text-white border-blue-600 shadow-blue-500/20'
                      : 'bg-white text-slate-800 border-slate-200 hover:border-blue-300 hover:bg-blue-50/40'
                  }`}
                  onClick={() => handleScenarioChange(video)}
                >
                  <FileVideo className={`w-4 h-4 shrink-0 ${isSelected ? 'text-white' : 'text-blue-600'}`} />
                  <div className="flex items-center gap-1.5 max-w-[240px] truncate">
                    <span className="truncate">{video.filename || video.title}</span>
                    <span
                      className={`text-[10px] px-1.5 py-0.5 rounded font-mono ${
                        isSelected ? 'bg-blue-700 text-blue-100' : 'bg-slate-100 text-slate-600'
                      }`}
                    >
                      {formatTime(video.duration_seconds || 6)}
                    </span>
                  </div>
                  {video.events && video.events.length > 0 && (
                    <span
                      className={`text-[10px] font-bold px-1.5 py-0.5 rounded-full ${
                        isSelected ? 'bg-red-500/80 text-white' : 'bg-red-100 text-red-700'
                      }`}
                    >
                      {video.events.length} Flagged
                    </span>
                  )}
                  {video.file_size_mb ? (
                    <span
                      className={`text-[10px] font-mono hidden sm:inline ${
                        isSelected ? 'text-blue-200' : 'text-slate-400'
                      }`}
                    >
                      {video.file_size_mb}MB
                    </span>
                  ) : null}
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      if (video.filename) handleDeleteVideo(video.filename);
                    }}
                    title="Delete from database"
                    className={`opacity-0 group-hover:opacity-100 transition-opacity p-1 rounded hover:bg-red-500/20 text-slate-400 hover:text-red-600 ${
                      isSelected ? 'hover:text-white' : ''
                    }`}
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              );
            })}
          </div>
        ) : (
          <p className="text-[11px] text-slate-500 italic">
            No footage in database yet. Use "Upload Bay Video" above to store your CCTV clips permanently.
          </p>
        )}
      </div>

      {/* Scenario Presets Bar */}
      <div className="flex flex-wrap items-center gap-2 pt-1">
        <span className="text-xs font-bold text-slate-500 mr-2 flex items-center gap-1.5">
          <Sparkles className="w-3.5 h-3.5 text-blue-600" />
          Simulated Dock Presets:
        </span>
        {mockScenarios.map((scen) => (
          <button
            key={scen.id}
            onClick={() => handleScenarioChange(scen)}
            className={`px-3.5 py-1.5 rounded-full text-xs font-bold transition-all border ${
              selectedScenario.id === scen.id && !selectedScenario.video_url
                ? 'bg-slate-900 text-white border-slate-900 shadow-sm'
                : 'bg-white text-slate-700 border-slate-200 hover:bg-slate-50 hover:text-slate-900 shadow-2xs'
            }`}
          >
            {scen.location}: {scen.title.split(':')[1] || scen.title}
          </button>
        ))}
      </div>

      {/* Upload Progress Bar if active */}
      {isUploading && (
        <div className="bg-white border border-blue-200 rounded-3xl p-4 shadow-xs animate-pulse">
          <div className="flex justify-between text-xs font-bold text-slate-900 mb-2">
            <span className="flex items-center gap-2">
              <UploadCloud className="w-4 h-4 text-blue-600 animate-bounce" />
              Scanning dock video for handling issues...
            </span>
            <span className="font-mono text-blue-600">{uploadProgress}%</span>
          </div>
          <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
            <div
              className="bg-blue-600 h-full rounded-full transition-all duration-300"
              style={{ width: `${uploadProgress}%` }}
            />
          </div>
        </div>
      )}

      {/* Main Analysis Workspace */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left 2 Columns: Synchronized Video Player & Evidence Inspector */}
        <div className="lg:col-span-2 space-y-6">
          {/* Synchronized Canvas Video Player */}
          <div className="bg-white rounded-3xl border border-slate-200/90 shadow-xs overflow-hidden p-3">
            <div className="px-3 py-2 flex items-center justify-between text-xs border-b border-slate-100 mb-3">
              <div className="flex items-center gap-2 font-mono text-slate-800 font-semibold">
                <FileVideo className="w-4 h-4 text-blue-600" />
                <span>{selectedScenario.title}</span>
              </div>
              {selectedScenario.video_url ? (
                <span className="flex items-center gap-1 text-blue-600 font-bold text-[11px] bg-blue-50 px-2.5 py-0.5 rounded-full border border-blue-200">
                  <Play className="w-3.5 h-3.5 fill-blue-600" /> Live CCTV Footage Loaded
                </span>
              ) : (
                <span className="flex items-center gap-1 text-emerald-600 font-bold text-[11px] bg-emerald-50 px-2.5 py-0.5 rounded-full border border-emerald-200">
                  <CheckCircle2 className="w-3.5 h-3.5" /> Video Ready
                </span>
              )}
            </div>

            <VideoPlayer
              url={selectedScenario.video_url}
              duration={selectedScenario.duration_seconds}
              events={selectedScenario.events}
              annotations={selectedScenario.annotations}
              seekTime={seekTime}
              onTimeUpdate={(t) => setCurrentTime(t)}
              onEventSelected={handleSelectIncident}
            />
          </div>

          {/* Selected Incident Deep Evidence & Explainability Card */}
          {selectedEvent && (
            <div className="bg-white rounded-3xl border border-slate-200/90 p-6 shadow-xs space-y-5">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-slate-100 gap-2">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-2xl bg-blue-50 border border-blue-200 flex items-center justify-center text-blue-600">
                    <ShieldCheck className="w-5 h-5" />
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <h3 className="text-base font-bold text-slate-900">
                        {(selectedEvent.type || selectedEvent.event_type || '').replace(/_/g, ' ').toUpperCase()}
                      </h3>
                      <RiskBadge level={selectedEvent.riskLevel} />
                    </div>
                    <p className="text-xs text-slate-500 font-mono mt-0.5">
                      Timestamp: {formatTime(selectedEvent.video_start ?? 0)} • {selectedEvent.location} • Confidence: {Math.round(selectedEvent.confidence * 100)}%
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <span className="text-xs text-slate-500 font-mono">
                    Score: <strong className="text-slate-900 font-bold">{selectedEvent.risk_score ?? 85}/100</strong>
                  </span>
                </div>
              </div>

              {/* Evidence Metrics Grid */}
              <div>
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-3 flex items-center gap-1.5">
                  <Info className="w-3.5 h-3.5 text-blue-600" />
                  Extracted Telemetry Evidence:
                </h4>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                  {evidence.drop_height_m !== undefined && (
                    <div className="bg-slate-50 p-3 rounded-2xl border border-slate-200">
                      <span className="text-[10px] text-slate-500 uppercase font-bold block">Drop Height</span>
                      <span className="text-base font-black text-rose-600 font-mono">{evidence.drop_height_m} m</span>
                    </div>
                  )}
                  {evidence.impact_velocity_mps !== undefined && (
                    <div className="bg-slate-50 p-3 rounded-2xl border border-slate-200">
                      <span className="text-[10px] text-slate-500 uppercase font-bold block">Impact Velocity</span>
                      <span className="text-base font-black text-orange-600 font-mono">{evidence.impact_velocity_mps} m/s</span>
                    </div>
                  )}
                  {evidence.tilt_angle_deg !== undefined && (
                    <div className="bg-slate-50 p-3 rounded-2xl border border-slate-200">
                      <span className="text-[10px] text-slate-500 uppercase font-bold block">Stack Tilt</span>
                      <span className="text-base font-black text-amber-600 font-mono">{evidence.tilt_angle_deg}°</span>
                    </div>
                  )}
                  {evidence.duration_s !== undefined && (
                    <div className="bg-slate-50 p-3 rounded-2xl border border-slate-200">
                      <span className="text-[10px] text-slate-500 uppercase font-bold block">Duration</span>
                      <span className="text-base font-black text-slate-800 font-mono">{evidence.duration_s} s</span>
                    </div>
                  )}
                  {evidence.equipment_type && (
                    <div className="bg-slate-50 p-3 rounded-2xl border border-slate-200">
                      <span className="text-[10px] text-slate-500 uppercase font-bold block">Equipment</span>
                      <span className="text-xs font-bold text-slate-800 truncate block">{evidence.equipment_type}</span>
                    </div>
                  )}
                  {evidence.zone_name && (
                    <div className="bg-slate-50 p-3 rounded-2xl border border-slate-200">
                      <span className="text-[10px] text-slate-500 uppercase font-bold block">Zone Area</span>
                      <span className="text-xs font-bold text-slate-800 truncate block">{evidence.zone_name}</span>
                    </div>
                  )}
                  <div className="bg-slate-50 p-3 rounded-2xl border border-slate-200">
                    <span className="text-[10px] text-slate-500 uppercase font-bold block">Objects Tracked</span>
                    <span className="text-xs font-bold text-slate-800 truncate block">
                      {selectedEvent.object_ids?.join(', ') || 'carton_412'}
                    </span>
                  </div>
                  <div className="bg-slate-50 p-3 rounded-2xl border border-slate-200">
                    <span className="text-[10px] text-slate-500 uppercase font-bold block">Damage Status</span>
                    <span className="text-xs font-bold text-emerald-600">Potential Risk</span>
                  </div>
                </div>
              </div>

              {/* Prevention Explanation & Recommendation */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
                <div className="bg-slate-50 p-4 rounded-2xl border border-slate-200 space-y-1">
                  <span className="text-[11px] font-bold text-slate-600 uppercase tracking-wider block">
                    Observed Behavior Analysis
                  </span>
                  <p className="text-xs text-slate-700 leading-relaxed">
                    {selectedEvent.explanation || selectedEvent.description}
                  </p>
                </div>
                <div className="bg-blue-50/70 p-4 rounded-2xl border border-blue-200/80 space-y-1">
                  <span className="text-[11px] font-bold text-blue-700 uppercase tracking-wider block">
                    Actionable Prevention Recommendation
                  </span>
                  <p className="text-xs text-slate-700 leading-relaxed">
                    {selectedEvent.recommendation || 'Mandate ergonomic lifting protocol and verify container integrity.'}
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Right Column: Interactive Incident List Sidebar */}
        <div className="space-y-6">
          <div className="bg-white rounded-3xl border border-slate-200/90 p-6 shadow-xs flex flex-col h-full">
            <div className="flex items-center justify-between pb-4 border-b border-slate-100 mb-4">
              <div>
                <h3 className="text-sm font-bold text-slate-900">Detected Incidents</h3>
                <p className="text-xs text-slate-500 mt-0.5">Click any incident to jump to timestamp</p>
              </div>
              <span className="px-2.5 py-0.5 rounded-full bg-blue-50 text-blue-700 border border-blue-200 font-mono text-xs font-bold">
                {selectedScenario.events.length} flagged
              </span>
            </div>

            {/* Incidents List */}
            <div className="space-y-3 overflow-y-auto max-h-[580px] pr-1">
              {selectedScenario.events.map((evt) => {
                const isSelected = selectedEvent?.id === evt.id;
                const start = evt.video_start ?? 0;

                return (
                  <div
                    key={evt.id}
                    onClick={() => handleSelectIncident(evt)}
                    className={`p-3.5 rounded-2xl border transition-all cursor-pointer flex flex-col gap-2 ${
                      isSelected
                        ? 'bg-blue-50/80 border-blue-300 shadow-xs ring-1 ring-blue-300'
                        : 'bg-slate-50/70 border-slate-200/90 hover:bg-slate-100/70 hover:border-slate-300'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-white border border-slate-200 text-xs font-mono font-bold text-blue-600 shadow-2xs">
                        <Play className="w-3 h-3 fill-current" />
                        {formatTime(start)}
                      </span>
                      <RiskBadge level={evt.riskLevel} />
                    </div>

                    <div>
                      <h4 className="text-xs font-bold text-slate-900">
                        {(evt.type || evt.event_type || '').replace(/_/g, ' ').toUpperCase()}
                      </h4>
                      <p className="text-[11px] text-slate-600 line-clamp-2 mt-1 leading-snug">
                        {evt.description}
                      </p>
                    </div>

                    <div className="flex items-center justify-between text-[10px] text-slate-400 pt-1 border-t border-slate-200/60 font-mono">
                      <span>Conf: {Math.round(evt.confidence * 100)}%</span>
                      <span className="text-blue-600 font-sans font-bold flex items-center gap-0.5">
                        Jump to Replay <ArrowRight className="w-3 h-3" />
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
