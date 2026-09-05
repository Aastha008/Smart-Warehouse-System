# Project: AI Warehouse Intelligence

## Architecture
AI Warehouse Intelligence is an end-to-end edge-to-cloud computer vision and temporal behavior intelligence system for warehouse loading/unloading operations.

- **CV Ingestion & Tracking Layer (`backend/vision/`)**: Multi-format video ingestion, YOLOv8 entity detection with CPU/GPU/fallback support, ByteTrack/BoT-SORT persistent object tracking with velocity and trajectory estimation.
- **Temporal Behaviour Understanding Engine (`backend/behaviour/`)**: Stateful temporal pattern analyzers evaluating frame history windows across 10 warehouse handling behaviors configured via YAML.
- **Risk Scoring & Incident Engine (`backend/risk/`, `backend/database/`)**: Multi-factor scoring (base + additive modifiers * confidence), severity levels (LOW, MEDIUM, HIGH, CRITICAL), prevention-focused explainability, SQLite/PostgreSQL persistence.
- **FastAPI REST Service (`backend/api/`, `backend/services/`, `backend/assistant/`)**: Async video analysis jobs, event filtering APIs, dashboard metrics, and grounded conversational AI supervisor with database tools.
- **Frontend Dashboard & Video Player (`frontend/`)**: React 18 + TypeScript + Tailwind CSS v4 web application with synchronized bounding box video replay, timeline navigation, KPI metrics, live monitoring, and AI assistant chat.
- **Demo & Testing Infrastructure (`scripts/`, `demo/`, `tests/`)**: Synthetic video generators, database seeders, unit tests, and E2E integration test harnesses.

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 1 | Multi-format Video Ingestion | Support MP4, AVI, RTSP/Webcam with configurable FPS and frame skipping | M1 | ORIGINAL_REQUEST §R1 |
| 2 | Warehouse Entity Detection | YOLO detection of person, carton, package, pallet, trolley, forklift, vehicle | M1 | ORIGINAL_REQUEST §R1 |
| 3 | Persistent Object Tracking | Multi-object tracking with persistent IDs, trajectory, velocity, acceleration | M1 | ORIGINAL_REQUEST §R1 |
| 4 | 10 Temporal Behaviour Detectors | Detect product drop, dragging, throwing, rough handling, stacking issues, zone violations, pallet placement, sequence, equipment | M1 | ORIGINAL_REQUEST §R2 |
| 5 | Externalized YAML Configurations | Configurable rules in detection.yaml, behaviour.yaml, zones.yaml, warehouse_rules.yaml | M1 | ORIGINAL_REQUEST §R2 |
| 6 | Multi-factor Risk Scoring | LOW, MEDIUM, HIGH, CRITICAL scoring based on height, velocity, equipment, location, recurrence | M2 | ORIGINAL_REQUEST §R3 |
| 7 | Damage-prevention Explainability | Non-accusatory, prevention-focused incident explanations & actionable recommendations | M2 | ORIGINAL_REQUEST §R3 |
| 8 | Structured Incident Storage | SQLite/PostgreSQL schema with async SQLAlchemy for events, video jobs, alerts | M2 | ORIGINAL_REQUEST §R3 |
| 9 | FastAPI Backend Services | REST endpoints for /video, /events, /dashboard, /alerts, /assistant | M2 | ORIGINAL_REQUEST §R4 |
| 10 | Grounded AI Supervisor | Conversational assistant grounded on database tools without hallucinations | M2 | ORIGINAL_REQUEST §R6 |
| 11 | Synchronized Video Player & Replay | HTML5 video player with bounding box overlays, timeline markers, click-to-seek | M3 | ORIGINAL_REQUEST §R5 |
| 12 | Enterprise KPI Dashboard & Analytics | Recharts visualizations, risk distribution, trends, bay heatmaps | M3 | ORIGINAL_REQUEST §R5 |
| 13 | Incident Log & Detail Modal | Filterable incident tables, CSV export, evidence parameter inspection dialog | M3 | ORIGINAL_REQUEST §R5 |
| 14 | Real-time Alerts & Notifications | Web Audio chimes, browser HTML5 notifications, and severity banners | M3 | ORIGINAL_REQUEST §R6 |
| 15 | Demo & Synthetic Scenarios | Synthetic warehouse video generator and demo seed script | M4 | ORIGINAL_REQUEST §R7 |
| 16 | Comprehensive Test Suite | Pytest unit, behaviour, API, and E2E integration tests | M4/M5 | ORIGINAL_REQUEST §R7 |
| 17 | Complete Documentation Suite | 12 documentation files, Model Card, Responsible AI, and demo presentation | M4 | ORIGINAL_REQUEST §R7 |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| M1 | CV Pipeline & Temporal Behaviour Engine | Guarded torch import, class mappings, tracker compatibility, all 10 behavior detectors (pallet, sequence, equipment, zone fixes), behavior engine config wiring | Survey | PLANNED |
| M2 | FastAPI Backend & Grounded AI Supervisor | Events query routing, AI assistant key alignment (`high_risk`), database seeding integration | M1 | PLANNED |
| M3 | React Web Dashboard & Video Player Replay | Native HTML5 video player with bounding box canvas overlays & click-to-seek, Analytics page, detail modal, CSV export, audio/browser alerts, API client adapter | M2 | PLANNED |
| M4 | Demo Scripts, Integration Tests & Docs | Synthetic video generator, demo runner, database seeder, E2E integration tests, and documentation synchronization | M1, M2, M3 | PLANNED |
| M5 | E2E Verification & Forensic Hardening | Full pytest suite pass, adversarial coverage verification (Tiers 1-5), forensic integrity audit | M1, M2, M3, M4 | PLANNED |

## Interface Contracts
### CV Pipeline ↔ Behaviour Engine
- Input: `tracked_objects: List[TrackedObject]`, `frame_idx: int`, `frame_shape: Tuple[int, int]`
- Output: `List[BehaviourEvent]` with `event_type: str`, `confidence: float`, `bounding_box: Tuple[int, int, int, int]`, `evidence: Dict[str, Any]`

### Behaviour Engine ↔ Risk Engine
- Input: `BehaviourEvent`, `context: Dict[str, Any]`
- Output: `RiskAssessment` with `risk_score: float` (0-100), `risk_level: RiskLevel` (LOW, MEDIUM, HIGH, CRITICAL), `explanation: str`, `recommendation: str`

### Backend REST ↔ React Frontend
- Endpoints:
  - `GET /api/events` (filters: `risk_level`, `event_type`, `location`) -> `List[EventResponse]`
  - `GET /api/events/{id}` -> `EventResponse`
  - `GET /api/dashboard/summary` -> `DashboardSummary`
  - `GET /api/dashboard/trends` -> `TrendsResponse`
  - `GET /api/alerts/recent` -> `List[AlertResponse]`
  - `POST /api/assistant/query` -> `AssistantResponse`
  - `POST /api/video/analyze` -> `JobResponse`
  - `GET /api/video/status/{job_id}` -> `JobStatusResponse`

## Code Layout
- `backend/vision/`: `detector.py`, `tracker.py`, `annotator.py`, `pipeline.py`
- `backend/behaviour/`: `base_detector.py`, `drop_detector.py`, `drag_detector.py`, `throw_detector.py`, `rough_detector.py`, `stack_detector.py`, `unstable_stack_detector.py`, `zone_detector.py`, `pallet_detector.py`, `loading_sequence_detector.py`, `equipment_detector.py`, `engine.py`
- `backend/risk/`: `risk_engine.py`, `risk_explanation.py`
- `backend/database/`: `models.py`, `session.py`
- `backend/api/`: `events.py`, `video.py`, `dashboard.py`, `alerts.py`, `assistant.py`
- `backend/services/`: `event_service.py`, `video_service.py`, `dashboard_service.py`
- `backend/assistant/`: `assistant.py`
- `frontend/src/`: `components/` (`VideoPlayer.tsx`, `RiskChart.tsx`, `Navbar.tsx`, etc.), `pages/` (`Dashboard.tsx`, `VideoAnalysis.tsx`, `LiveMonitoring.tsx`, `Incidents.tsx`, `Analytics.tsx`, `Settings.tsx`, `AIAssistant.tsx`), `services/api.ts`, `types/index.ts`
- `scripts/`: `generate_synthetic_video.py`, `seed_demo_data.py`
- `demo/`: `demo_runner.py`
- `tests/`: `unit/`, `behaviour/`, `api/`, `integration/`
- `docs/`: `ARCHITECTURE.md`, `SETUP.md`, `MODEL_CARD.md`, `DATASET.md`, `API.md`, `DEMO.md`, `PRESENTATION.md`, `RESPONSIBLE_AI.md`
