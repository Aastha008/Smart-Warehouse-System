# Setup & Installation Guide

AI Warehouse Intelligence is an edge-to-cloud computer vision and temporal behavior intelligence platform. This guide provides comprehensive step-by-step instructions for installing, configuring, and verifying the system across Windows, Linux, macOS, and Docker environments.

---

## 1. System Requirements

### Hardware:
- **CPU**: 4+ cores (Intel Core i5/i7/i9, AMD Ryzen, or ARM64 Apple Silicon)
- **RAM**: 8 GB minimum (16 GB recommended for multi-stream video analysis)
- **GPU (Optional)**: NVIDIA GPU with CUDA 11.8+ or 12.0+ (GTX 1660, RTX 3060/4090, T4, A10)
- **Disk Space**: 2 GB free disk space

### Software:
- **Python**: 3.10, 3.11, 3.12, or 3.14
- **Node.js**: 18.x, 20.x, or 22.x (with `npm` 9+)
- **OpenCV / FFmpeg**: Video codecs for MP4 (H.264/AVC) and AVI (XVID)
- **Git**

---

## 2. Step-by-Step Installation

### Step 1: Clone Repository
```bash
git clone https://github.com/organization/ai-warehouse-intelligence.git
cd ai-warehouse-intelligence
```

### Step 2: Set Up Python Virtual Environment
**On Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**On Linux / macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Backend Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
# On Windows
copy .env.example .env

# On Linux/macOS
cp .env.example .env
```

Edit `.env` as required:
```ini
# Database (SQLite default, PostgreSQL optional)
DATABASE_URL=sqlite+aiosqlite:///./warehouse.db
SYNC_DATABASE_URL=sqlite:///./warehouse.db

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=True

# Vision & Detector Config
DETECTION_CONFIG=configs/detection.yaml
BEHAVIOUR_CONFIG=configs/behaviour.yaml
RISK_CONFIG=configs/risk.yaml
WAREHOUSE_RULES=configs/warehouse_rules.yaml

# AI Assistant (Optional - Fallback to deterministic telemetry grounding if unset)
OPENAI_API_KEY=
```

---

## 3. GPU vs CPU Acceleration Setup

### CPU-Only Mode (Default):
The pipeline automatically detects CUDA availability. If no GPU is present, it uses CPU inference with multi-threaded NumPy matrix operations and heuristic fallback detectors. No extra configuration is needed.

### NVIDIA GPU (CUDA Acceleration):
To enable PyTorch with CUDA acceleration on NVIDIA GPUs:
```bash
# Install PyTorch with CUDA 12.1
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121

# Install Ultralytics YOLO
pip install ultralytics
```
Verify CUDA detection:
```bash
python -c "import torch; print('CUDA Available:', torch.cuda.is_available(), '| Device:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'None')"
```

---

## 4. Frontend Web Dashboard Setup

```bash
cd frontend
npm install
npm run build
```

To run the Vite development server on port 5173:
```bash
npm run dev
```

---

## 5. Running the Application

### 1. Seed Demo Warehouse Telemetry
Populate `warehouse.db` with 50+ realistic multi-factor events across all 10 behaviors:
```bash
python scripts/seed_demo_data.py --clear --count 50
```

### 2. Generate Synthetic Warehouse Scenarios
Generate realistic MP4 synthetic video feeds:
```bash
# Generate all-scenario montage
python scripts/generate_synthetic_video.py --scenario all --duration 10 --output demo/sample_warehouse_feed.mp4

# Generate specific behavior (e.g. drop)
python scripts/generate_synthetic_video.py --scenario drop --duration 5 --output demo/sample_drop.mp4
```

### 3. Run Automated Interactive Demo
```bash
python demo/demo_runner.py --scenario all
```

### 4. Start FastAPI REST Backend
```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```
- Interactive Swagger UI: `http://localhost:8000/docs`
- ReDoc UI: `http://localhost:8000/redoc`

### 5. Start React Frontend Dashboard
```bash
cd frontend
npm run dev
```
Open `http://localhost:5173` in your browser.

---

## 6. Running Tests & Quality Verification

Run the complete test suite:
```bash
# Run all tests
python -m pytest tests/ -v

# Run specific integration tests
python -m pytest tests/integration/test_pipeline_e2e.py -v

# Run API endpoint tests
python -m pytest tests/api/test_api.py -v
```

---

## 7. Docker Deployment

Launch the complete stack using Docker Compose:
```bash
docker-compose up --build -d
```
Services started:
- **FastAPI Backend**: `http://localhost:8000`
- **React Dashboard**: `http://localhost:3000`

To stop containers:
```bash
docker-compose down
```

---

## 8. Troubleshooting

| Issue | Cause | Solution |
|---|---|---|
| `cv2.VideoWriter fails to write MP4` | Missing H.264 codec in OpenCV build | Script automatically falls back to `.avi` (XVID). Ensure `opencv-python` is installed. |
| `UnicodeEncodeError on Windows terminal` | Default console codepage cp1252 | Run `$OutputEncoding = [Console]::OutputEncoding = [System.Text.Encoding]::UTF8` in PowerShell. |
| `Database Locked Error` | Multiple processes writing SQLite | Use connection pooling in `backend/database/connection.py` or switch to PostgreSQL in `.env`. |
| `Frontend npm build error` | Missing TypeScript types or dependencies | Run `npm install --force` and `npm run build`. |
| `Port 8000 already in use` | Another instance of uvicorn running | Start backend with `--port 8001` or terminate existing process. |
