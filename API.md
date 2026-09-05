# REST API Specification & Endpoint Documentation

The AI Warehouse Intelligence platform exposes a comprehensive, high-throughput asynchronous REST API built with FastAPI, Pydantic v2, and SQLAlchemy.

- **Base URL**: `http://localhost:8000`
- **Swagger Interactive UI**: `http://localhost:8000/docs`
- **ReDoc Interactive UI**: `http://localhost:8000/redoc`
- **OpenAPI Schema JSON**: `http://localhost:8000/openapi.json`

---

## 1. Video Processing & Job Management

### `POST /api/video/upload`
Uploads a video file (MP4, AVI, MOV) for background analysis.

**Request**: `multipart/form-data`
- `file`: Video binary file

**Response (`200 OK`)**:
```json
{
  "job_id": "job_a1b2c3d4e5",
  "filename": "warehouse_dock2.mp4",
  "file_path": "uploads/warehouse_dock2.mp4",
  "status": "uploaded"
}
```

**cURL Example**:
```bash
curl -X POST "http://localhost:8000/api/video/upload" \
  -F "file=@demo/sample_warehouse_feed.mp4"
```

---

### `POST /api/video/analyze`
Starts asynchronous temporal behavior and risk analysis on an uploaded video job.

**Request (`application/json`)**:
```json
{
  "job_id": "job_a1b2c3d4e5",
  "location": "Loading Bay 2",
  "camera_id": "CAM-02-BAY2"
}
```

**Response (`200 OK`)**:
```json
{
  "job_id": "job_a1b2c3d4e5",
  "status": "processing",
  "message": "Video analysis queued in background"
}
```

---

### `GET /api/video/status/{job_id}`
Polls the processing status, progress percentage, and detected event counts of a video job.

**Response (`200 OK`)**:
```json
{
  "job_id": "job_a1b2c3d4e5",
  "status": "completed",
  "progress": 1.0,
  "total_frames": 300,
  "processed_frames": 300,
  "events_count": 4,
  "completed_at": "2026-09-02T14:30:15Z",
  "error_message": null
}
```

---

### `GET /api/video/jobs`
Returns a list of all recent video processing jobs.

**Response (`200 OK`)**: Array of VideoJob objects.

---

## 2. Warehouse Incident & Event Endpoints

### `GET /api/events`
Query filterable warehouse events with pagination, risk level, behavior type, location, and date filtering.

**Query Parameters**:
- `risk_level` (optional): `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`
- `event_type` (optional): `product_drop`, `product_throwing`, etc.
- `location` (optional): `Loading Bay 1`, `Loading Bay 2`, etc.
- `date` (optional): `YYYY-MM-DD`
- `start_date`, `end_date` (optional): Date range `YYYY-MM-DD`
- `skip` (default: `0`): Pagination offset
- `limit` (default: `100`): Max records to return

**Response (`200 OK`)**:
```json
[
  {
    "event_id": "evt_9876543210ab",
    "timestamp": "2026-09-02T14:22:15.340000Z",
    "camera_id": "CAM-02-BAY2",
    "location": "Loading Bay 2",
    "event_type": "product_drop",
    "risk_level": "HIGH",
    "risk_score": 78.5,
    "confidence": 0.92,
    "object_ids": [102],
    "video_path": "demo/sample_warehouse_feed.mp4",
    "video_start": 12.5,
    "video_end": 16.0,
    "evidence": {
      "drop_height_m": 1.45,
      "impact_velocity_mps": 5.2,
      "product_category": "fragile_electronics"
    },
    "explanation": "Observed: Carton dropped from operator handling height, accelerating rapidly to concrete floor impact. Risk Level: HIGH (Score: 78/100). Potential cargo damage.",
    "recommendation": "Inspect package integrity before staging; review ergonomic two-hand lifting posture with shift team.",
    "created_at": "2026-09-02T14:22:15.340000Z"
  }
]
```

---

### `POST /api/events`
Creates and registers a new warehouse event in the database.

**Request (`application/json`)**:
```json
{
  "camera_id": "CAM-01-NORTH",
  "location": "Loading Bay 1",
  "event_type": "product_throwing",
  "risk_level": "CRITICAL",
  "risk_score": 94.0,
  "confidence": 0.95,
  "object_ids": [101, 102],
  "evidence": {
    "velocity_mps": 7.5,
    "airborne_sec": 1.2
  },
  "explanation": "High-velocity parcel toss across loading aisle.",
  "recommendation": "Enforce zero-tolerance parcel throwing policy."
}
```

**Response (`201 Created`)**: EventResponse object.

---

### `GET /api/events/high-risk`
Retrieves events classified as `HIGH` or `CRITICAL` risk severity.

**Query Parameters**:
- `limit` (default: `50`)

---

### `GET /api/events/today`
Retrieves all incidents recorded since 00:00:00 UTC of the current calendar day.

---

### `GET /api/events/by-location` and `GET /api/events/by-location/{location}`
Retrieves all events filtered by warehouse loading bay or dock area.

---

### `GET /api/events/statistics`
Retrieves aggregate operational statistics across all logged events.

**Response (`200 OK`)**:
```json
{
  "total_events": 64,
  "high_risk": 18,
  "critical": 8,
  "events_today": 22,
  "by_behaviour": {
    "product_drop": 14,
    "product_throwing": 8,
    "improper_stacking": 12,
    "unstable_stacking": 10,
    "product_dragging": 8,
    "product_outside_zone": 12
  },
  "by_location": {
    "Loading Bay 1": 18,
    "Loading Bay 2": 24,
    "Loading Bay 3": 12,
    "Unloading Dock East": 10
  },
  "by_risk_level": {
    "LOW": 14,
    "MEDIUM": 24,
    "HIGH": 18,
    "CRITICAL": 8
  }
}
```

---

## 3. Dashboard & Analytics Endpoints

### `GET /api/dashboard/summary`
Returns high-level KPI cards (total events, high-risk counts, today's counts, safety index).

### `GET /api/dashboard/trends`
Returns daily/shift temporal time-series incident trends for chart visualization.

### `GET /api/dashboard/locations`
Returns location-based risk frequency and incident count distribution.

### `GET /api/dashboard/behaviours`
Returns frequency breakdown across all 10 detected behaviors.

---

## 4. Alert & Notification Endpoints

### `GET /api/alerts/recent`
Retrieves recent supervisor alerts, sorted by severity and timestamp.

### `POST /api/alerts`
Creates an active supervisor alert.

### `POST /api/alerts/acknowledge/{id}` & `POST /api/alerts/{id}/acknowledge`
Acknowledges an active alert by supervisor user ID.

**Query Parameters**:
- `user` (default: `"Supervisor"`)

**Response (`200 OK`)**:
```json
{
  "id": "alt_123456",
  "acknowledged": true,
  "acknowledged_by": "Supervisor_Jane",
  "acknowledged_at": "2026-09-02T14:45:00Z"
}
```

---

## 5. Conversational AI Supervisor Endpoint

### `POST /api/assistant/query` (Alias: `POST /assistant/query`)
Processes natural language operational queries grounded strictly on warehouse telemetry and rules.

**Request (`application/json`)**:
```json
{
  "query": "What high-risk incidents occurred in Loading Bay 2 today?"
}
```

**Response (`200 OK`)**:
```json
{
  "response": "Today, 6 high-risk events were detected in Loading Bay 2:\n- 🟠 Product Drop (Score: 78/100, drop height: 1.45m)\n- 🔴 Product Throwing (Score: 94/100, velocity: 7.5m/s)\n\nRecommended Action: Conduct supervisor debrief at Loading Bay 2 and inspect fragile cargo before staging.",
  "sources": ["event_database", "statistics"],
  "data_used": {
    "location": "Loading Bay 2",
    "high_risk_count": 6
  }
}
```

**cURL Example**:
```bash
curl -X POST "http://localhost:8000/api/assistant/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the warehouse stacking rules?"}'
```
