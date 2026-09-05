# Original User Request

## Initial Request — 2026-09-02T12:45:32Z

AI Warehouse Intelligence is a production-grade, AI-powered video intelligence and damage-prevention assistant for warehouse loading and unloading operations. The system monitors video feeds, performs multi-object detection and tracking, analyzes temporal behaviors across 10+ risk categories, computes composite risk scores, alerts supervisors in real time, and exposes a conversational AI supervisor grounded on warehouse event telemetry.

Working directory: C:/Users/hp/.gemini/antigravity/scratch/ai-warehouse-intelligence
Integrity mode: development

## Requirements

### R1. Video Ingestion & Computer Vision Pipeline
- Ingest warehouse video streams/files (MP4, AVI, RTSP/Webcam compatible) with configurable FPS and frame skipping.
- Detect key warehouse entities: `person`, `carton`, `package`, `pallet`, `trolley`, `forklift`, `vehicle` using modern YOLO detection (with CPU/GPU support and transfer learning / pretrained weights).
- Track objects across frames with persistent IDs, velocity, acceleration, and bounding box trajectories using ByteTrack or BoT-SORT.

### R2. Temporal Behaviour Understanding Engine
- Implement a stateful temporal event engine supporting at least 10 warehouse handling behaviors:
  1. `product_drop`
  2. `product_dragging`
  3. `product_throwing`
  4. `rough_handling`
  5. `improper_stacking`
  6. `unstable_stacking`
  7. `product_outside_zone`
  8. `incorrect_pallet_position`
  9. `unsafe_loading_sequence`
  10. `improper_handling_equipment`
- Configurable thresholds via YAML (`configs/detection.yaml`, `configs/behaviour.yaml`, `configs/zones.yaml`, `configs/warehouse_rules.yaml`).
- Generate structured behavior events with bounding boxes, timestamps, confidence, velocity/height evidence, and context.

### R3. Risk Scoring & Incident Management Engine
- Multi-factor risk engine classifying events into `LOW`, `MEDIUM`, `HIGH`, `CRITICAL` based on behavior type, drop height, velocity, equipment, location, and repeated patterns (`configs/risk.yaml`).
- Distinguish between *Observed Behaviour*, *Potential Risk*, and *Confirmed Damage* (focusing on damage prevention).
- Structured incident storage in SQLite/PostgreSQL with query APIs for filtering by severity, loading bay, shift, and time window.

### R4. FastAPI Backend & Video Processing Service
- FastAPI REST service providing:
  - Video upload, async background analysis, and job status (`/video/upload`, `/video/analyze`, `/video/status/{job_id}`)
  - Incident queries (`/events`, `/events/{id}`, `/events/high-risk`, `/events/today`, `/events/by-location`, `/statistics`)
  - Analytics and dashboard metrics (`/dashboard/summary`, `/dashboard/trends`, `/dashboard/locations`)
  - AI Assistant query endpoint (`/assistant/query`)
- Robust error handling for corrupted videos, missing models, and database fallbacks.

### R5. Interactive Web Dashboard & Video UI
- React + TypeScript + Tailwind CSS web application featuring:
  - Enterprise Dashboard: KPI summary cards, risk distribution charts, top risky behaviors, high-risk bays heatmap, live recent incident feed.
  - Video Analysis & Incident Replay: Synchronized video player with bounding box overlays, timeline markers, and jump-to-incident timestamp navigation on click.
  - Live Monitoring, Incident Log & Details, Analytics, Settings, and AI Supervisor Chat.

### R6. Grounded AI Supervisor Assistant & Real-time Alerts
- RAG / Tool-calling AI supervisor answering operator questions grounded strictly on warehouse telemetry (events, statistics, locations, rules) without fabricating events.
- Real-time browser notifications, audio alerts, and structured intervention recommendations for HIGH and CRITICAL severity events.

### R7. Responsible AI, Testing & Comprehensive Documentation
- Privacy-conscious design (process/behavior focus, no unauthorized facial recognition, configurable data retention, explainable alerts).
- Automated test suite covering vision pipeline, tracking, behavior detectors, risk engine, backend APIs, and end-to-end integration.
- Full documentation suite: `README.md`, `ARCHITECTURE.md`, `SETUP.md`, `MODEL_CARD.md`, `DATASET.md`, `API.md`, `DEMO.md`, `PROJECT_STATUS.md`, `CHALLENGE_COMPLIANCE.md`, `FINAL_REPORT.md`, and demo presentation slides.

## Acceptance Criteria

### Vision & Tracking
- [ ] YOLO detector successfully identifies warehouse objects (person, carton/package, pallet, equipment) on sample video frames.
- [ ] Object tracker maintains stable IDs and computes trajectory, velocity, and center coordinates across consecutive frames.

### Behaviour & Risk Intelligence
- [ ] All 10 behavior detectors trigger on their respective temporal patterns with structured JSON outputs and evidence payloads.
- [ ] Risk scoring engine correctly assigns `LOW`, `MEDIUM`, `HIGH`, and `CRITICAL` based on configurable YAML rules and evidence metrics.
- [ ] Explanations clearly articulate *why* an event was flagged as risky without claiming unverified actual damage.

### Backend & API
- [ ] FastAPI backend starts cleanly and passes all endpoint tests (`/video/*`, `/events/*`, `/dashboard/*`, `/assistant/*`).
- [ ] Video analysis jobs execute asynchronously in the background and persist incidents into the database.

### Frontend Dashboard & Video Player
- [ ] React UI renders dashboard KPIs, charts, incident lists, and incident detail views without errors.
- [ ] Video player visualizes bounding boxes, behavior tags, and jumps directly to the exact incident timestamp when clicked.

### AI Assistant & Alerts
- [ ] AI Assistant answers queries using database tools (`get_events`, `get_statistics`, `get_high_risk_events`, `get_location_stats`) and refuses out-of-domain / ungrounded queries.
- [ ] Alerts display clear prevention recommendations for high/critical incidents.

### Quality, Verification & Deliverables
- [ ] Test suite runs and passes (`pytest tests/`).
- [ ] Demo video generation script / synthetic scenario runner produces verified demo results.
- [ ] All required documentation files and `CHALLENGE_COMPLIANCE.md` are complete and accurate.
