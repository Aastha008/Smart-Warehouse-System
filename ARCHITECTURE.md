# System Architecture & Design Specification

## 1. Architectural Overview

AI Warehouse Intelligence is a real-time, edge-to-cloud computer vision and temporal behavior intelligence platform engineered for warehouse loading, unloading, and staging operations. The architecture decouples low-latency video decoding and object tracking from stateful temporal pattern recognition, multi-factor risk modeling, and conversational AI telemetry grounding.

```
+---------------------------------------------------------------------------------------------------+
|                                  WAREHOUSE VIDEO INGESTION LAYER                                  |
|   RTSP Streams / Webcams / Uploaded MP4 & AVI Video Files (640x480 to 1920x1080 @ 15-30 FPS)       |
+---------------------------------------------------------------------------------------------------+
                                                  |
                                                  v
+---------------------------------------------------------------------------------------------------+
|                               COMPUTER VISION & TRACKING SUBSYSTEM                                 |
|  * Frame Extraction & Configurable Frame Skipping (OpenCV / FFmpeg Hardware Decoding)             |
|  * WarehouseDetector: YOLOv8 Object Detection (Classes: person, package, carton, pallet, forklift)|
|  * ObjectTracker: ByteTrack / Kalman Filtering (Persistent IDs, 2D Trajectory, Velocity, Accel)   |
+---------------------------------------------------------------------------------------------------+
                                                  |
                                                  v
+---------------------------------------------------------------------------------------------------+
|                             TEMPORAL BEHAVIOUR UNDERSTANDING ENGINE                                |
|  * Stateful sliding-window temporal analyzers evaluated across consecutive frames                 |
|  * 10 Core Warehouse Handling Detectors (Drop, Drag, Throw, Rough, Stacking, Unstable, Zones, etc.)|
|  * Structured BehaviourEvent: {event_type, object_id, timestamp, frame_idx, confidence, evidence} |
+---------------------------------------------------------------------------------------------------+
                                                  |
                                                  v
+---------------------------------------------------------------------------------------------------+
|                                MULTI-FACTOR RISK SCORING ENGINE                                    |
|  * Formula: Risk Score = (Base Score + Sum(Modifiers)) * Confidence                               |
|  * Classification: LOW (0-30), MEDIUM (31-60), HIGH (61-85), CRITICAL (86-100)                    |
|  * Damage-Prevention Explainability & Non-accusatory Actionable Corrective Recommendations        |
+---------------------------------------------------------------------------------------------------+
                                                  |
                                                  v
+---------------------------------------------------------------------------------------------------+
|                                FASTAPI REST & PERSISTENCE SERVICES                                |
|  * SQLAlchemy ORM (SQLite / PostgreSQL) for Events, VideoJobs, AlertLogs, Cameras, Metrics        |
|  * Asynchronous Background Job Processing (/api/video/upload, /api/video/analyze)                 |
|  * Query Endpoints: /api/events, /api/events/high-risk, /api/dashboard/summary, /api/alerts       |
+---------------------------------------------------------------------------------------------------+
                   |                                                              |
                   v                                                              v
+--------------------------------------+      +-----------------------------------------------------+
|        GROUNDED AI SUPERVISOR        |      |             REACT WEB DASHBOARD & UI                |
|  * Telemetry Grounding Tools         |      |  * Synchronized HTML5 Video Player + BBox Overlays  |
|  * Strict Domain Guardrails          |      |  * Timeline Markers & Click-to-Seek Incident Replay |
|  * Natural Language Operations Chat  |      |  * KPI Cards, Risk Distribution, Bay Heatmap Charts |
|  * /api/assistant/query              |      |  * Audio Chimes & Browser HTML5 Notifications       |
+--------------------------------------+      +-----------------------------------------------------+
```

---

## 2. Mathematical Risk Scoring Formula

The Risk Engine evaluates every detected `BehaviourEvent` using a deterministic multi-factor model configured via YAML (`configs/risk.yaml`):

$$\text{Raw Score} = \text{BaseScore}(\text{behavior\_type}) + \sum_{i=1}^{k} \text{Modifier}_i$$

$$\text{Composite Risk Score} = \text{clamp}\Big(\text{Raw Score} \times \text{Confidence}, 0.0, 100.0\Big)$$

### Modifiers Table:
| Factor | Condition | Modifier Value |
|---|---|:---:|
| Drop Height | $\text{Height} \ge 1.5\text{ m}$ ($>140\text{ px}$) | $+25.0$ |
| Drop Height | $0.8\text{ m} \le \text{Height} < 1.5\text{ m}$ | $+15.0$ |
| Impact Velocity | $\text{Velocity} \ge 5.0\text{ m/s}$ ($>6.0\text{ px/f}$) | $+20.0$ |
| Product Fragility | `fragile_electronics` or `glassware` | $+20.0$ |
| Stacking Overhang | $\text{Overhang} > 20\%$ | $+15.0$ |
| Stack Tilt Angle | $\text{Tilt} > 15^\circ$ | $+20.0$ |
| Repeat Violation | Same object / zone within 5 minutes | $+15.0$ |
| Location Modifier | Loading Bay Dock Edge | $+10.0$ |

### Severity Thresholds:
- **`LOW`** ($0.0 \le \text{Score} \le 30.0$): Informational log; zero operational disruption.
- **`MEDIUM`** ($30.1 \le \text{Score} \le 60.0$): Operational advisory on supervisor dashboard.
- **`HIGH`** ($60.1 \le \text{Score} \le 85.0$): Supervisor visual/audio alert requiring bay check.
- **`CRITICAL`** ($85.1 \le \text{Score} \le 100.0$): Immediate intervention required; potential cargo loss or severe safety hazard.

---

## 3. Stateful Temporal Behaviour State Machines

Each behavior detector in `backend/behaviour/` implements an explicit finite state machine (FSM) evaluated across a sliding frame buffer ($N=30$ frames):

### 1. `ProductDropDetector`
$$\text{IDLE} \xrightarrow{\text{Person holding carton}} \text{HELD} \xrightarrow{\text{Downward } v_y > v_{\text{thresh}}} \text{FALLING} \xrightarrow{v_y \to 0, y \approx y_{\text{floor}}} \text{IMPACT} \xrightarrow{\text{Stationary}} \text{TRIGGER(product\_drop)}$$

### 2. `ProductThrowDetector`
$$\text{IDLE} \xrightarrow{\text{Carton in hand}} \text{HELD} \xrightarrow{|v_x| > 5.0, v_y < 0} \text{RELEASED} \xrightarrow{\text{Parabolic Trajectory}} \text{AIRBORNE} \xrightarrow{\Delta x > 100\text{px}} \text{TRIGGER(product\_throwing)}$$

### 3. `ProductDragDetector`
$$\text{IDLE} \xrightarrow{y \approx y_{\text{floor}}} \text{FLOOR\_CONTACT} \xrightarrow{|v_x| > 2.0, \Delta y \approx 0 \text{ for } t > 1.5\text{s}} \text{DRAGGING} \xrightarrow{} \text{TRIGGER(product\_dragging)}$$

### 4. `RoughHandlingDetector`
$$\text{IDLE} \xrightarrow{\text{In motion}} \text{TRACKING} \xrightarrow{\left|\frac{dv}{dt}\right| > a_{\text{max}} \text{ or jerk} > j_{\text{max}}} \text{JERK\_SPIKE} \xrightarrow{} \text{TRIGGER(rough\_handling)}$$

### 5. `StackingDetector` & `UnstableStackDetector`
- Evaluates vertical bounding box overlap $(\text{IoU}_x > 0.6)$ and compares box dimensions / weight tiers (heavy-on-light).
- Measures centroid alignment angle $\theta = \arctan\left(\frac{|x_{\text{top}} - x_{\text{bottom}}|}{y_{\text{bottom}} - y_{\text{top}}}\right)$. If $\theta > 15^\circ$ with wobble oscillation, triggers `unstable_stacking`.

---

## 4. Relational Database Schema

```sql
-- Warehouse Incident Events
CREATE TABLE events (
    event_id VARCHAR PRIMARY KEY,
    timestamp DATETIME NOT NULL,
    camera_id VARCHAR DEFAULT 'cam_01',
    location VARCHAR DEFAULT 'loading_bay_1',
    event_type VARCHAR NOT NULL,
    risk_level VARCHAR DEFAULT 'MEDIUM',
    risk_score FLOAT DEFAULT 50.0,
    confidence FLOAT DEFAULT 0.5,
    object_ids JSON DEFAULT '[]',
    video_path VARCHAR,
    video_start FLOAT,
    video_end FLOAT,
    evidence JSON DEFAULT '{}',
    explanation TEXT,
    recommendation TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Video Processing Async Jobs
CREATE TABLE video_jobs (
    job_id VARCHAR PRIMARY KEY,
    video_path VARCHAR NOT NULL,
    status VARCHAR DEFAULT 'pending',
    progress FLOAT DEFAULT 0.0,
    total_frames INTEGER DEFAULT 0,
    processed_frames INTEGER DEFAULT 0,
    events_count INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    completed_at DATETIME,
    error_message TEXT
);

-- Real-Time Supervisor Alerts
CREATE TABLE alert_logs (
    id VARCHAR PRIMARY KEY,
    event_id VARCHAR REFERENCES events(event_id) ON DELETE SET NULL,
    alert_type VARCHAR DEFAULT 'visual_audio',
    severity VARCHAR DEFAULT 'HIGH',
    message TEXT,
    location VARCHAR,
    sent_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    acknowledged BOOLEAN DEFAULT FALSE,
    acknowledged_at DATETIME,
    acknowledged_by VARCHAR
);

-- Camera Registry
CREATE TABLE cameras (
    camera_id VARCHAR PRIMARY KEY,
    name VARCHAR NOT NULL,
    location VARCHAR NOT NULL,
    rtsp_url VARCHAR,
    status VARCHAR DEFAULT 'active',
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Operational & Throughput Metrics
CREATE TABLE metrics (
    id VARCHAR PRIMARY KEY,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    metric_name VARCHAR NOT NULL,
    metric_value FLOAT NOT NULL,
    location VARCHAR,
    metadata_json JSON DEFAULT '{}'
);
```

---

## 5. Grounded AI Supervisor Architecture

```
User Query: "What happened in Loading Bay 2 today?"
                      |
                      v
       +-------------------------------+
       |    Domain Guardrail Filter    | ---> If non-warehouse (weather/sports/trivia):
       +-------------------------------+      Strictly Refuse ("Domain restricted...")
                      |
                      v (Warehouse Query)
       +-------------------------------+
       |      Query Intent Parser      |
       +-------------------------------+
                      |
                      v
       +-------------------------------+
       | AssistantTools Data Grounding |
       |  * get_events(location="...") |
       |  * get_statistics()           |
       |  * get_warehouse_rules()      |
       +-------------------------------+
                      |
                      v
       +-------------------------------+
       | Grounded Response Generation  | ---> Returns facts strictly grounded on DB
       | (No Hallucinated Incidents)   |      with full citation of source records
       +-------------------------------+
```
