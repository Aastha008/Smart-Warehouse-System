# Demo Execution Guide & Feature Walkthrough

This guide provides step-by-step instructions to run the AI Warehouse Intelligence demonstration environment, generate synthetic scenarios, process video feeds, and explore the interactive web dashboard.

---

## 1. Quickstart: 3-Minute Demo Run

### Step 1: Seed Warehouse Database Telemetry
Populate the database with 50+ multi-factor events across all 10 behaviors, cameras, alerts, and metrics:
```bash
python scripts/seed_demo_data.py --clear --count 50
```

### Step 2: Generate Synthetic Warehouse Video
Create a multi-behavior 200-frame synthetic warehouse video clip (`demo/sample_warehouse_feed.mp4`):
```bash
python scripts/generate_synthetic_video.py --scenario all --duration 10 --fps 20 --output demo/sample_warehouse_feed.mp4
```

### Step 3: Execute End-to-End Automated Demo Runner
Run the automated end-to-end demo script that tests video decoding, tracking, behavior detection, risk scoring, persistence, and AI supervisor queries:
```bash
python demo/demo_runner.py --scenario all
```

---

## 2. Interactive Web Dashboard Walkthrough

### Step 1: Start Backend and Frontend
In terminal 1 (Backend):
```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```
In terminal 2 (Frontend):
```bash
cd frontend
npm run dev
```
Open **`http://localhost:5173`** in your browser.

---

## 3. Key Feature Tour

### 🖥️ 1. Enterprise Executive Dashboard (`/`)
- **KPI Summary Cards**: Real-time counters for Total Monitored Events, High-Risk Incidents, Critical Hazards, and Active Unacknowledged Alerts.
- **Risk Severity Distribution**: Interactive Donut chart displaying Low, Medium, High, and Critical proportions.
- **Top Risky Handling Behaviors**: Bar chart highlighting frequent anomalies (e.g. Package Drop, Unstable Stacking).
- **Loading Bay Risk Heatmap**: Visual breakdown of risk index across Loading Bays 1-4 and Staging Areas.
- **Recent Incident Feed**: Live scrolling feed of recent dock detections with severity badges.

---

### 🎥 2. Synchronized Video Player & Incident Replay (`/video`)
- **Synchronized Canvas Overlays**: Bounding boxes color-coded by class (Operator: Blue, Cargo: Orange, Pallet: Gray, Forklift: Yellow) and labeled with persistent Track IDs.
- **Interactive Timeline Markers**: Color-coded markers indicating exact seconds where high-risk anomalies occurred.
- **Click-to-Seek Timestamp Jump**: Click any incident in the detected event list to jump directly to the exact frame where the event happened.
- **Video Upload & Background Processing**: Upload custom warehouse video files (MP4/AVI) and watch progress bars update in real time.

---

### 📡 3. Live Multi-Camera Dock Monitoring (`/live`)
- Grid view of simulated warehouse dock feeds (`CAM-01-NORTH`, `CAM-02-BAY2`, `CAM-03-BAY3`, `CAM-04-EAST`).
- Real-time status indicators, active hazard tags, and instant audio-visual alert triggers.

---

### 📋 4. Filterable Incident Log & Detail Modal (`/incidents`)
- Filter incidents by **Risk Level** (LOW, MEDIUM, HIGH, CRITICAL), **Behavior Type**, **Bay Location**, and **Date Range**.
- **Incident Detail Dialog**: Click any row to inspect full kinematic evidence parameters:
  - Estimated drop height (meters / pixels)
  - Impact velocity & jerk
  - Stack tilt angle & overhang percentage
  - Prevention-focused, non-accusatory explanation
  - Actionable corrective recommendations
- **CSV Export**: Export filtered incident logs for shift reports.

---

### 📊 5. Analytics & Trends (`/analytics`)
- **Hourly Risk Trends**: Time-series area chart tracking incident rates throughout the shift.
- **Damage Prevention Rate**: KPI metric tracking percentage of potential cargo damage events detected and flagged before permanent freight loss.

---

### 🤖 6. Grounded AI Supervisor Assistant (`/assistant`)
Interactive conversational AI grounded strictly on warehouse telemetry:
- Try asking:
  - *"What high-risk events occurred today?"*
  - *"Which loading bay needs supervisor attention?"*
  - *"What are the safety guidelines for pallet stacking?"*
  - *"Why was the incident at Bay 2 flagged as critical?"*
- **Guardrail Test**: Ask out-of-domain questions (*"What is the weather in Tokyo?"*) to observe strict refusal and guardrail protection.

---

### 🔔 7. Real-Time Audio & Visual Alerts
- High-priority banner notifications on CRITICAL and HIGH severity events.
- Audio alert chime synthesized via Web Audio API.
- One-click supervisor acknowledgment logging.
