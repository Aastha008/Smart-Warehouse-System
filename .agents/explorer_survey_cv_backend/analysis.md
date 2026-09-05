# Comprehensive CV & Backend Survey & Analysis Report

**Project**: AI Warehouse Intelligence  
**Scope**: Computer Vision Pipeline (R1), Temporal Behaviour Engine (R2), Risk Engine & Data Storage (R3), and FastAPI Backend Service (R4)  
**Date**: 2026-09-02  
**Author**: `teamwork_preview_explorer_survey_cv_backend`  

---

## Executive Summary

This investigation performed a comprehensive, read-only architectural and code-level audit of the Computer Vision, Behavior Understanding, Risk Management, and FastAPI Backend subsystems of the AI Warehouse Intelligence application.

| Subsystem | Requirement | Implementation Status | Functional Quality | Key Findings & Deficiencies |
|---|---|---|---|---|
| **CV Pipeline & Tracking** | R1 | **Substantially Implemented** | Moderate | Top-level `import torch` in `detector.py` breaks environments without PyTorch; tracker uses Euclidean matching instead of full ByteTrack/BoT-SORT; class mapping in `detector.py` is hardcoded and ignores `configs/detection.yaml`; `Annotator` missing `"CRITICAL"` color mapping. |
| **Temporal Behaviour Engine** | R2 | **Partially Implemented (7/10 active, 3 stubs)** | Moderate | 7 behavior detectors implemented, but 3 (`pallet_detector`, `loading_sequence_detector`, `equipment_detector`) return empty stubs `[]`; `zone_detector` tests person position rather than package bounding box against zone boundaries; `BehaviourEngine` is initialized without passing YAML config; detectors lack `behaviour_type` attribute expected by tests. |
| **Risk Scoring & Incidents** | R3 | **Fully Implemented** | High | Multi-factor risk engine (base score + modifiers * confidence) with LOW, MEDIUM, HIGH, CRITICAL classification; strict distinction between observed behavior, potential risk, and confirmed damage; rich explanation generator; async SQLAlchemy schema (`events`, `video_jobs`, `alert_logs`) active in SQLite (`warehouse.db`) and PostgreSQL-ready. |
| **FastAPI Backend & APIs** | R4 | **Fully Implemented** | High | Complete REST service covering `/api/events`, `/api/video`, `/api/dashboard`, `/api/alerts`, and `/api/assistant`; background async processing with fallback mock generator; 18 integration tests passing; minor bug where `list_events` endpoint does not pass `event_type` and `location` query parameters to `EventService`. |

---

## 1. R1: Video Ingestion, YOLO Entity Detection & Object Tracking

### 1.1 Architecture & Components

```
Video Stream / File (.mp4, .avi, etc.)
  │
  ▼
[VideoPipeline] (backend/vision/pipeline.py)
  ├── 1. Frame Sampling (skip_frames = 2)
  ├── 2. [WarehouseDetector] (backend/vision/detector.py) -> List[Detection]
  ├── 3. [ObjectTracker] (backend/vision/tracker.py) -> List[TrackedObject]
  ├── 4. [MotionAnalyzer] (backend/vision/motion.py) -> Dict[id, MotionFeatures]
  ├── 5. [BehaviourEngine] (backend/behaviour/behaviour_engine.py) -> List[BehaviourEvent]
  ├── 6. [RiskEngine] (backend/risk/risk_engine.py) -> List[RiskAssessment]
  └── 7. [Annotator] (backend/vision/annotator.py) -> Annotated Frame
```

### 1.2 Component-by-Component Findings

#### A. Video Ingestion (`backend/vision/pipeline.py`)
- **Mechanism**: Reads frames using OpenCV `cv2.VideoCapture(video_path)`. Supports frame skipping via `if frame_idx % self.skip_frames == 0:` (lines 63-64).
- **Output Aggregation**: Collects all detected incidents into `AnalysisResult` dataclass with `total_frames` and `events`.
- **Deficiencies**:
  1. `process_video(video_path, output_path=None)` defines an `output_path` parameter, but never initializes a `cv2.VideoWriter` or writes annotated frames to disk when `output_path` is specified.

#### B. YOLO Entity Detection (`backend/vision/detector.py` & `configs/detection.yaml`)
- **Mechanism**: Loads YOLO model via `ultralytics.YOLO(model_path)`. Performs inference with configurable `conf_threshold` and `iou_threshold`.
- **Required Classes (R1 & `configs/detection.yaml`)**: `person`, `carton`, `package`, `pallet`, `trolley`, `forklift`, `vehicle`.
- **Critical Code Bugs & Discrepancies**:
  1. **Unguarded `import torch`** (`backend/vision/detector.py:3`):
     ```python
     # Line 3:
     import torch
     ...
     try:
         from ultralytics import YOLO
     except ImportError:
         class YOLO: ...
     ```
     `import torch` is executed at the top level without exception handling. When running in environments where PyTorch is not pre-installed or during lightweight CI, importing `detector.py` raises `ModuleNotFoundError: No module named 'torch'`. Because `tracker.py` and `base_detector.py` import `detector.py`, this breaks imports across the entire vision and behaviour modules.
     *Remediation*: Wrap `import torch` in `try ... except ImportError: torch = None` and check `torch is not None and torch.cuda.is_available()`.
  2. **Hardcoded Class Mapping Disconnect** (`backend/vision/detector.py:35-45`):
     `detector.py` defines a hardcoded dictionary:
     ```python
     self.class_mapping = {
         0: "person",
         2: "vehicle",
         7: "vehicle",
         39: "bottle",
         41: "cup",
         63: "laptop",
         67: "cell phone",
     }
     ```
     and ignores `self.config.get("class_mapping")` from `configs/detection.yaml` (which maps COCO class IDs 18/24 to `carton`, 25/26/28/56/73 to `package`, 67 to `pallet`, etc.). Any unrecognized class falls back to `"package"`.

#### C. Object Tracking (`backend/vision/tracker.py`)
- **Mechanism**: Implements `ObjectTracker` with Euclidean distance association (`_compute_distance`), velocity computation `(vx, vy)`, acceleration computation `(ax, ay)`, and trajectory history tracking up to 50 points per object.
- **Track Lifecycle**: Tracks missing frames (`missing_frames >= max_missing_frames` eviction).
- **Discrepancies**:
  1. **Attribute Naming**: `TrackedObject` defines `object_id: int`, whereas `tests/unit/test_vision.py:95` asserts `tracks1[0].track_id == tracks2[0].track_id`. Providing a property or alias `track_id` -> `object_id` ensures compatibility.
  2. **ByteTrack/BoT-SORT**: R1 mentions ByteTrack or BoT-SORT; the current tracker is a lightweight custom centroid tracker.

#### D. Motion Analysis (`backend/vision/motion.py`)
- **Features Extracted**: `avg_velocity`, `max_velocity`, `is_dropping`, `is_jerky`, `horizontal_movement`, `vertical_movement`, `total_displacement`.
- **Discrepancies**: `tests/unit/test_vision.py:120` expects a method `analyzer.compute_velocity(trajectory)`, but `MotionAnalyzer` only provides `analyze(tracks)`.

#### E. Annotator (`backend/vision/annotator.py`)
- **Features**: Draws bounding boxes, object ID/class labels, trajectory trail lines (`cv2.polylines`), and colored risk alert boxes.
- **Deficiencies**: `self.colors` only contains `"LOW": (0, 255, 0)`, `"MEDIUM": (0, 165, 255)`, `"HIGH": (0, 0, 255)`. When `risk_level == "CRITICAL"`, it falls back to white `(255, 255, 255)`. It should map `"CRITICAL"` to `(0, 0, 200)` or dedicated critical indicator.

---

## 2. R2: Temporal Behaviour Understanding Engine

### 2.1 Behavior Detector Implementation Matrix

All 10 required handling behaviors were surveyed against `backend/behaviour/` and `configs/behaviour.yaml`:

| # | Behavior Name | Detector File | Status | Detection Logic & Evidence Captured | Deficiencies / Findings |
|---|---|---|---|---|---|
| 1 | `product_drop` | `backend/behaviour/drop_detector.py` | **Implemented** | Trajectory vertical displacement: `end_y - start_y > drop_threshold (50px)`. Evidence: `drop_height_px`, `velocity`. | Checks hardcoded class list `["package", "bottle", "laptop", "cell phone"]`. |
| 2 | `product_dragging` | `backend/behaviour/drag_detector.py` | **Implemented** | Horizontal displacement with minimal vertical lift: `dx > drag_x_threshold (40px)` and `dy < drag_y_threshold (10px)` over 10 frames. Evidence: `dx`, `dy`. | Only checks `class_name == "package"`. |
| 3 | `product_throwing` | `backend/behaviour/throw_detector.py` | **Implemented** | Velocity magnitude `v_mag > throw_velocity (30px/f)` with upward velocity `vy < 0`. Evidence: `velocity_magnitude`. | Simple velocity threshold over 5-frame window. |
| 4 | `rough_handling` | `backend/behaviour/rough_handling_detector.py` | **Implemented** | Acceleration magnitude `accel_mag > jerk_threshold (15px/f^2)`. Evidence: `acceleration`. | Simple single-frame jerk check. |
| 5 | `improper_stacking` | `backend/behaviour/stacking_detector.py` | **Implemented** | Pairwise package spatial check: top item vertically aligned above bottom item with width ratio `p1_w > p2_w * 1.2` (heavy/large on top of light/small). Evidence: `top_width`, `bottom_width`. | Functional spatial check. |
| 6 | `unstable_stacking` | `backend/behaviour/unstable_stack_detector.py` | **Implemented** | Aspect ratio check `height / width > 3.0` (tall thin stack). Evidence: `aspect_ratio`. | Simplified proxy for stack tilt/oscillation. |
| 7 | `product_outside_zone` | `backend/behaviour/zone_detector.py` | **Flawed Logic** | Checks if `person` x-coordinate `> frame_width * 0.9`. | **Bug**: Checks `person` instead of `package`/`carton`/`pallet`, and does not load zone polygons/rectangles from `configs/zones.yaml`. |
| 8 | `incorrect_pallet_position` | `backend/behaviour/pallet_detector.py` | **Stub (Empty)** | `def analyze(...): return []` | Empty placeholder returning no events. |
| 9 | `unsafe_loading_sequence` | `backend/behaviour/loading_sequence_detector.py` | **Stub (Empty)** | `def analyze(...): return []` | Empty placeholder returning no events. |
| 10 | `improper_handling_equipment` | `backend/behaviour/equipment_detector.py` | **Stub (Empty)** | `def analyze(...): return []` | Empty placeholder returning no events. |

### 2.2 Architectural & Integration Findings in Behavior Subsystem
1. **Config Propagation**: In `backend/vision/pipeline.py:30`, `self.behaviour = BehaviourEngine()` passes no arguments (`config=None`). As a result, `BehaviourEngine` passes an empty `{}` to each detector, causing all `self.config.get(key, default)` calls to fall back to hardcoded defaults instead of values in `configs/behaviour.yaml`.
2. **Missing `behaviour_type` attribute**: `tests/behaviour/test_behaviour.py:128` asserts `[d.behaviour_type for d in engine.detectors]`. None of the detector classes define `behaviour_type: str`.
3. **State Machine / Track States**: `tests/behaviour/test_behaviour.py:19` checks `hasattr(detector, 'state_machines') or hasattr(detector, 'track_states')`. The detectors currently calculate metrics purely on the trajectory list of `TrackedObject` without persistent state dictionaries.

---

## 3. R3: Risk Scoring & Incident Management Engine

### 3.1 Risk Scoring Formula & Levels

`backend/risk/risk_engine.py` implements the multi-factor risk scoring engine configured via `configs/risk.yaml`:

- **Score Range**: 0 to 100
- **Formula**:
  $$\text{Raw Score} = \text{Base Score}(\text{event\_type}) + \sum \text{Modifiers}$$
  $$\text{Final Score} = \text{clamp}\Big(\big\lfloor \text{Raw Score} \times \text{clamp}(\text{confidence}, 0.5, 1.0) \big\rfloor, 0, 100\Big)$$
- **Base Scores**:
  - `product_throwing`: 85
  - `unstable_stacking`: 75
  - `product_drop`: 70
  - `unsafe_loading_sequence`: 70
  - `rough_handling`: 65
  - `improper_stacking`: 60
  - `incorrect_pallet_position`: 55
  - `product_dragging`: 50
  - `improper_handling_equipment`: 45
  - `product_outside_zone`: 40
- **Modifiers**:
  - `drop_height_px`: `>150px` (+20), `>80px` (+10)
  - `velocity`: `>6.0` (+15), `>3.0` (+5)
  - `product_type`: `fragile` (+15), `heavy` (+10), `lightweight` (-5)
  - `repeat_offence`: `second` (+10), `third_plus` (+20)
  - `location`: `loading_bay` (+5), `transit_zone` (+3)
- **4 Risk Levels**:
  - `LOW`: 0 – 30 (Action: `log`, Color: `#22c55e`, Icon: 🟢)
  - `MEDIUM`: 31 – 60 (Action: `notify`, Color: `#f59e0b`, Icon: 🟡)
  - `HIGH`: 61 – 85 (Action: `alert`, Color: `#f97316`, Icon: 🟠)
  - `CRITICAL`: 86 – 100 (Action: `intervene`, Color: `#ef4444`, Icon: 🔴)

### 3.2 Observed Behaviour vs Potential Risk vs Confirmed Damage
`backend/risk/risk_explanation.py` implements strict compliance with damage prevention semantics:
- Never asserts unverified product destruction.
- Uses explainable, grounded language: *"Potential damage-causing event"*, *"Product moved downward rapidly and became stationary"*, *"Requires inspection to assess impact"*.
- Contains dedicated explanation generators (`_explain_drop`, `_explain_drag`, `_explain_throw`, `_explain_rough`, `_explain_stacking`, `_explain_unstable`, `_explain_zone`, `_explain_pallet`, `_explain_loading`, `_explain_equipment`) and actionable recommendations linked to `configs/warehouse_rules.yaml`.

### 3.3 Database Storage & Schema (`backend/database/`)
- **Connection**: `backend/database/connection.py` uses SQLAlchemy Async Engine (`create_async_engine`) defaulting to `sqlite+aiosqlite:///./warehouse.db`. Easily switched to PostgreSQL via `DATABASE_URL=postgresql+asyncpg://...`.
- **Tables**:
  1. `events`:
     - `event_id` (String PK, UUID)
     - `timestamp` (DateTime)
     - `camera_id` (String)
     - `location` (String)
     - `event_type` (String)
     - `risk_level` (String: LOW, MEDIUM, HIGH, CRITICAL)
     - `risk_score` (Float)
     - `confidence` (Float)
     - `object_ids` (JSON)
     - `video_path` (String)
     - `video_start`, `video_end` (Float)
     - `evidence` (JSON)
     - `explanation` (String)
     - `recommendation` (String)
     - `created_at` (DateTime)
  2. `video_jobs`:
     - `job_id` (String PK)
     - `video_path`, `status`, `progress`, `total_frames`, `processed_frames`, `events_count`, `created_at`, `completed_at`, `error_message`
  3. `alert_logs`:
     - `id` (String PK), `event_id` (FK to events), `alert_type`, `sent_at`, `acknowledged` (Boolean)
- **Live Database Inspection**: Confirmed `warehouse.db` exists and has all 3 tables created cleanly.

---

## 4. R4: FastAPI Backend & Services Architecture

### 4.1 FastAPI Application (`backend/main.py`)
- **Lifespan Context Manager**: Automates table creation on startup and ensures directories exist (`uploads/`, `data/uploads/`, `data/processed/`, `data/frames/`).
- **CORS Configuration**: Wildcard CORS enabled for cross-origin frontend communication.
- **Static Video Server**: Mounts `/static` route to serve uploaded videos directly to video players.
- **Root Health Check**: `GET /` returns `{"message": "AI Warehouse Intelligence API is running", "version": "1.0.0"}`.
- **Route Alias**: `GET /api/statistics` delegates directly to `EventService.get_statistics`.

### 4.2 Endpoint Survey & Validation

| Router Prefix | Method | Path | Request Schema | Response Schema | Status & Notes |
|---|---|---|---|---|---|
| `/api/events` | GET | `/api/events` | Query: `risk_level`, `event_type`, `location` | `List[EventResponse]` | **Functional** (Bug: router omits passing `event_type` and `location` to `EventService.get_events`) |
| `/api/events` | GET | `/api/events/high-risk` | None | `List[EventResponse]` | **Functional** (Filters HIGH & CRITICAL) |
| `/api/events` | GET | `/api/events/today` | None | `List[EventResponse]` | **Functional** (Filters today's UTC midnight) |
| `/api/events` | GET | `/api/events/by-location/{location}` | Path: `location` | `List[EventResponse]` | **Functional** |
| `/api/events` | GET | `/api/events/statistics` | None | `EventStats` | **Functional** (Aggregates counts, behavior breakdowns, location stats) |
| `/api/events` | GET | `/api/events/{event_id}` | Path: `event_id` | `EventResponse` | **Functional** (Returns 404 if not found) |
| `/api/video` | POST | `/api/video/upload` | Form `UploadFile` | `VideoUploadResponse` | **Functional** (Validates .mp4, .avi, .mov, .mkv, .webm, saves to uploads, creates VideoJob) |
| `/api/video` | POST | `/api/video/analyze` | Body `AnalysisRequest` | JSON status | **Functional** (Enqueues `BackgroundTasks` runner `analyze_video_background`) |
| `/api/video` | GET | `/api/video/status/{job_id}` | Path: `job_id` | `VideoJobStatus` | **Functional** (Returns progress, frames, event count) |
| `/api/video` | GET | `/api/video/list` | None | List of job dictionaries | **Functional** (Sorted by `created_at` desc) |
| `/api/dashboard` | GET | `/api/dashboard/summary` | None | `DashboardSummary` | **Functional** (KPIs: today count, high risk, critical, active alerts) |
| `/api/dashboard` | GET | `/api/dashboard/trends` | None | `List[RiskTrend]` | **Functional** (7-day daily risk counts) |
| `/api/dashboard` | GET | `/api/dashboard/locations` | None | `List[LocationStats]` | **Functional** (Location counts + high risk counts with defaults) |
| `/api/dashboard` | GET | `/api/dashboard/behaviours` | None | `List[BehaviourStats]` | **Functional** (Group by event type with formatted titles) |
| `/api/alerts` | GET | `/api/alerts/recent` | None | `List[AlertLog]` | **Functional** |
| `/api/alerts` | POST | `/api/alerts/{alert_id}/acknowledge` | Path: `alert_id` | `{"message": "Acknowledged"}` | **Functional** (Updates acknowledged flag) |
| `/api/assistant` | POST | `/api/assistant/query` | Body `AssistantQuery` | `AssistantResponse` | **Functional** (Grounded retrieval over events & stats, rule-based fallback + optional OpenAI LLM) |

### 4.3 Background Processing & Graceful Fallback
- `analyze_video_background` in `backend/services/video_service.py`:
  - Attempts to run the complete vision pipeline (`VideoPipeline.process_video`).
  - If heavy ML packages (`torch`, `ultralytics`, `cv2`) are unavailable in a lightweight deployment, it catches `ImportError` and executes `_mock_analysis`.
  - `_mock_analysis` simulates incremental progress (25% -> 60% -> 100%), produces realistic events with bounding box timings, explanations, and evidence payloads, and persists them to `warehouse.db`.
  - This ensures that the frontend dashboard, incident tables, video player timeline markers, and AI Assistant remain fully testable in any environment.

---

## 5. Test Suite Verification & Analysis

### 5.1 Test Execution Results
Running `pytest` on the test suite produced the following results:

1. **`tests/api/test_api.py`**: **18 / 18 PASSED** (100% pass rate).
   - Validates Events API, High-Risk filtering, Video list, Job status 404, Dashboard summary, Trends, Locations, Behaviours, Assistant queries (today, empty query), Alert queries, CORS headers, 404 handler, and Invalid upload handling.
2. **`tests/test_api_quick.py`**: **Collection Error**.
   - Contains a standalone test function definition `def test(name, r, expected=200):` that pytest confuses for a pytest test requiring a fixture named `name`.
   - *Fix*: Rename `tests/test_api_quick.py` to `scripts/test_api_quick.py` or rename the helper to `def check_status(...)`.
3. **`tests/behaviour/test_behaviour.py` & `tests/unit/test_vision.py`**: **Skipped**.
   - Root cause: Top-level `import torch` in `backend/vision/detector.py` raised `ModuleNotFoundError`, which triggered `try ... except ImportError: pytest.skip(...)` in all test fixtures.
   - Secondary discrepancies: `test_vision.py` expects `track.track_id` (current is `track.object_id`), `analyzer.compute_velocity(trajectory)` (current is `analyze(tracks)`), and `test_behaviour.py` expects `detector.behaviour_type`.

---

## 6. Actionable Recommendations for Implementation Phase

To bring R1–R4 to 100% test pass rate and production readiness:

1. **Fix `detector.py` imports**:
   - Guard `import torch` with `try ... except ImportError`.
   - Read `class_mapping` from `configs/detection.yaml` instead of hardcoding.
2. **Complete 3 Stub Behavior Detectors**:
   - Implement `backend/behaviour/pallet_detector.py` (`incorrect_pallet_position`: check product bounding box extending beyond pallet bounding box).
   - Implement `backend/behaviour/loading_sequence_detector.py` (`unsafe_loading_sequence`: check multiple objects moving simultaneously in close proximity).
   - Implement `backend/behaviour/equipment_detector.py` (`improper_handling_equipment`: check large product moving without forklift/trolley within proximity threshold).
3. **Fix `zone_detector.py`**:
   - Load polygon/rectangle coordinates from `configs/zones.yaml` and test if product (`package`, `carton`, `pallet`) center or bbox lies outside `designated_area`.
4. **Propagate Config into `BehaviourEngine`**:
   - In `backend/vision/pipeline.py`, load `configs/behaviour.yaml` and pass it when instantiating `self.behaviour = BehaviourEngine(behaviour_config)`.
   - Add `self.behaviour_type` and `track_states = {}` attributes on all detector classes.
5. **Fix Minor Backend Routing & Naming Discrepancies**:
   - In `backend/api/events.py:17`, pass `event_type=event_type, location=location` to `EventService.get_events`.
   - Add `@property def track_id(self): return self.object_id` on `TrackedObject`.
   - Add `compute_velocity(trajectory)` helper on `MotionAnalyzer`.
   - Add `"CRITICAL": (0, 0, 200)` color in `backend/vision/annotator.py`.
   - Move or rename `tests/test_api_quick.py` so pytest runs cleanly across all test suites.
