/**
 * TypeScript Interfaces and Types for AI Warehouse Intelligence
 */

export type RiskLevel = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';

export interface EvidenceData {
  drop_height_m?: number;
  impact_velocity_mps?: number;
  tilt_angle_deg?: number;
  duration_s?: number;
  distance_m?: number;
  equipment_type?: string;
  equipment_speed_kmh?: number;
  zone_name?: string;
  pallet_id?: string;
  pallet_overhang_cm?: number;
  stack_height_layers?: number;
  worker_id_anonymized?: string;
  trajectory_points?: number;
  [key: string]: any;
}

export interface Event {
  id: string;
  event_id?: string;
  timestamp: string;
  camera_id?: string;
  location: string;
  type: string;
  event_type?: string;
  riskLevel: RiskLevel;
  risk_level?: RiskLevel;
  risk_score?: number;
  confidence: number;
  object_ids?: (string | number)[];
  video_path?: string;
  videoUrl?: string;
  video_start?: number;
  video_end?: number;
  description: string;
  evidence?: EvidenceData | string;
  explanation?: string;
  recommendation?: string;
  created_at?: string;
}

export interface VideoJob {
  job_id: string;
  id?: string;
  video_path: string;
  filename?: string;
  status: 'pending' | 'processing' | 'completed' | 'failed' | 'uploaded';
  progress: number;
  total_frames?: number;
  processed_frames?: number;
  events_count?: number;
  error_message?: string;
  created_at?: string;
  completed_at?: string;
  results?: Event[];
}

export interface DashboardSummary {
  totalEvents: number;
  total_events?: number;
  highRisk: number;
  high_risk_count?: number;
  critical: number;
  critical_count?: number;
  eventsToday: number;
  total_events_today?: number;
  high_risk_events_today?: number;
  critical_events_today?: number;
  activeAlerts?: number;
  active_alerts?: number;
  activeCameras?: number;
  preventionRate?: number;
}

export interface RiskTrend {
  date: string;
  low: number;
  medium: number;
  high: number;
  critical: number;
  total?: number;
  risk_level?: string;
  count?: number;
}

export interface BehaviourStats {
  behaviour: string;
  type?: string;
  count: number;
  percentage?: number;
  risk_level?: RiskLevel;
}

export interface LocationStats {
  location: string;
  events_count: number;
  count?: number;
  high_risk_count: number;
  critical_count?: number;
  risk_score?: number;
  status?: 'normal' | 'warning' | 'critical';
}

export interface AlertData {
  id: string;
  alert_id?: string;
  event_id?: string;
  camera_id?: string;
  location?: string;
  risk_level: RiskLevel;
  event_type: string;
  message: string;
  timestamp: string;
  acknowledged: boolean;
  event?: Event;
}

export interface AssistantMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  response?: string;
  sources?: string[];
  data_used?: Record<string, any>;
  confidence?: string;
  timestamp?: string;
  tools_called?: string[];
}

export interface BoundingBox {
  id: number | string;
  label: string;
  bbox: [number, number, number, number]; // [x1, y1, x2, y2] normalized or pixel
  score: number;
  risk_level?: RiskLevel;
  track_id?: number | string;
  color?: string;
}

export interface FrameAnnotation {
  timestamp: number; // in seconds
  frame_idx: number;
  boxes: BoundingBox[];
  active_events?: string[];
}

export interface VideoScenario {
  id: string;
  title: string;
  description: string;
  location: string;
  camera_id: string;
  duration_seconds: number;
  video_url?: string;
  filename?: string;
  file_size_mb?: number;
  uploaded_at?: string;
  events: Event[];
  annotations: FrameAnnotation[];
}

export interface CameraFeed {
  id: string;
  name: string;
  location: string;
  status: 'active' | 'warning' | 'alert' | 'offline';
  fps: number;
  resolution: string;
  active_objects: number;
  stream_url?: string;
  last_incident?: string;
}

export interface SettingsConfig {
  ppe_detection_sensitivity: number;
  proximity_threshold_meters: number;
  drop_height_sensitivity: number;
  stacking_tilt_tolerance: number;
  temporal_window_frames: number;
  min_alert_severity: RiskLevel;
  sound_enabled: boolean;
  sound_volume: number;
  browser_notifications_enabled: boolean;
  face_blurring: boolean;
  worker_anonymization: boolean;
  data_retention_days: number;
}
