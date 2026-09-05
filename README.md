# AI Warehouse Intelligence

> Production-Grade AI-Powered Video Intelligence & Damage-Prevention Assistant for Warehouse Loading and Unloading Operations.

![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.14-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-teal)
![React](https://img.shields.io/badge/React-18.x%20%2B%20TypeScript-blue)
![YOLOv8](https://img.shields.io/badge/YOLO-v8%20%2B%20ByteTrack-orange)
![Tests](https://img.shields.io/badge/Tests-130%2B%20Passing%20(100%25)-success)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 🎯 System Overview

**AI Warehouse Intelligence** transforms passive warehouse CCTV cameras into an active, intelligent operational assistant. The system analyzes video feeds in real time, performs multi-object detection and persistent tracking, detects complex temporal handling behaviors across 10+ risk categories, computes composite multi-factor risk scores, alerts supervisors to critical hazards, and exposes a conversational AI supervisor grounded strictly on warehouse telemetry.

```
+------------------+     +-------------------+     +--------------------+
|  Video Ingestion | --> | Computer Vision   | --> | Temporal Behaviour |
|  MP4/AVI/RTSP    |     | YOLOv8+ByteTrack  |     | 10 Stateful FSMs   |
+------------------+     +-------------------+     +--------------------+
                                                             |
                                                             v
+------------------+     +-------------------+     +--------------------+
| React Dashboard  | <-- | FastAPI REST API  | <-- | Multi-Factor Risk  |
| Video Replay UI  |     | SQLAlchemy Store  |     | Scoring Engine     |
+------------------+     +-------------------+     +--------------------+
         |                         |
         v                         v
+------------------+     +-------------------+
| Audio/Visual     |     | Grounded AI       |
| Alerts & Chimes  |     | Supervisor Chat   |
+------------------+     +-------------------+
```

---

## ✨ Key Features

1. **Multi-Object Detection & Tracking**: Identifies operators, cartons, packages, pallets, and forklifts with persistent IDs, velocity, acceleration, and 2D trajectories.
2. **10 Stateful Temporal Behavior Detectors**:
   - `product_drop`: Drops from handling heights with gravity acceleration.
   - `product_dragging`: Lateral floor movement causing bottom surface abrasion.
   - `product_throwing`: High-velocity airborne parabolic tosses between operators.
   - `rough_handling`: Severe deceleration spikes and jerky impacts.
   - `improper_stacking`: Inverted weight hierarchy (heavy on small/fragile boxes).
   - `unstable_stacking`: Pallet stacks tilted $>15^\circ$ with wobble oscillation.
   - `product_outside_zone`: Freight obstructing red-hatched pedestrian pathways.
   - `incorrect_pallet_position`: Pallet overhang protruding into forklift lanes.
   - `unsafe_loading_sequence`: Top-rack loading prior to securing foundation tiers.
   - `improper_handling_equipment`: Manual lifting of freight exceeding 35kg.
3. **Deterministic Multi-Factor Risk Engine**: Calculates risk score (0-100) and assigns `LOW`, `MEDIUM`, `HIGH`, `CRITICAL` based on height, velocity, product fragility, and repeat patterns.
4. **Damage-Prevention Explainability**: Generates non-accusatory, prevention-first explanations and actionable recommendations.
5. **Synchronized Video Player & Incident Replay**: HTML5 video playback with canvas-drawn bounding boxes, timeline anomaly markers, and instant click-to-seek timestamp navigation.
6. **Grounded AI Supervisor Assistant**: Tool-calling conversational assistant grounded strictly on database telemetry with domain guardrails that reject off-topic questions.
7. **Complete Demo & Simulation Harness**: Procedural synthetic video generator, demo runner, and database seeder.

---

## 🚀 Quick Start (3 Steps)

### Step 1: Install Dependencies
```bash
# Clone repository
git clone https://github.com/organization/ai-warehouse-intelligence.git
cd ai-warehouse-intelligence

# Install Python backend dependencies
pip install -r requirements.txt
copy .env.example .env
```

### Step 2: Seed Telemetry & Generate Demo Video
```bash
# Seed 50+ realistic multi-factor warehouse incidents
python scripts/seed_demo_data.py --clear --count 50

# Generate synthetic warehouse video feed
python scripts/generate_synthetic_video.py --scenario all --duration 10 --output demo/sample_warehouse_feed.mp4
```

### Step 3: Run Interactive Automated Demo
```bash
python demo/demo_runner.py --scenario all
```

---

## 🌐 Running Backend & Frontend Services

### Start FastAPI REST Service:
```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```
- **Interactive Swagger Docs**: `http://localhost:8000/docs`
- **ReDoc Specification**: `http://localhost:8000/redoc`

### Start React Web Dashboard:
```bash
cd frontend
npm install
npm run dev
```
Open **`http://localhost:5173`** in your browser.

### Docker Compose Stack:
```bash
docker-compose up --build -d
```
- Backend REST API: `http://localhost:8000`
- React Dashboard: `http://localhost:3000`

---

## 🧪 Testing & Verification

Run the comprehensive 130+ test suite:
```bash
# Run all automated tests
python -m pytest tests/ -v

# Run E2E integration tests
python -m pytest tests/integration/test_pipeline_e2e.py -v

# Run API endpoint tests
python -m pytest tests/api/test_api.py -v

# Run behaviour detector tests
python -m pytest tests/behaviour/test_behaviour.py -v
```

---

## 📚 Complete Documentation Suite

| Document | Purpose |
|---|---|
| [ARCHITECTURE.md](ARCHITECTURE.md) | Edge-to-cloud design, FSM state machines, math risk formula, database schema |
| [SETUP.md](SETUP.md) | Step-by-step setup, GPU vs CPU instructions, troubleshooting guide |
| [MODEL_CARD.md](MODEL_CARD.md) | YOLOv8s + ByteTrack specs, benchmark latency, accuracy metrics, limitations |
| [DATASET.md](DATASET.md) | Video formats, annotation JSON schemas, synthetic generator parameters |
| [API.md](API.md) | Complete OpenAPI / REST endpoint specifications and sample curl queries |
| [DEMO.md](DEMO.md) | Step-by-step demo execution guide and web UI feature walkthrough |
| [PROJECT_STATUS.md](PROJECT_STATUS.md) | Milestone tracking, feature inventory audit, test coverage summary |
| [CHALLENGE_COMPLIANCE.md](CHALLENGE_COMPLIANCE.md) | Detailed verification matrix for requirements §R1–§R7 and Acceptance Criteria |
| [FINAL_REPORT.md](FINAL_REPORT.md) | Executive engineering report, technical innovations, damage-prevention ROI |
| [PRESENTATION.md](PRESENTATION.md) | Presentation pitch deck and slide structure for operations leadership |
| [RESPONSIBLE_AI.md](RESPONSIBLE_AI.md) | Ethical governance, zero facial biometrics, privacy retention, explainable AI |

---

## 🔒 Responsible AI & Privacy

- **Zero Facial Biometrics**: Operates exclusively on generic bounding boxes (`person`, `carton`, `pallet`, `forklift`). No facial recognition or demographic classification.
- **Process Safety Focus**: Designed to improve ergonomic safety and prevent freight damage, never for worker surveillance or individual punitive grading.
- **Explainable Evidence**: Every flagged incident provides quantifiable kinematic metrics (drop height, velocity, tilt degrees).
- **Configurable Retention**: Automated clip pruning policies comply with global privacy standards (GDPR/CCPA).

---

## 📝 License

Distributed under the MIT License. See `LICENSE` for details.
