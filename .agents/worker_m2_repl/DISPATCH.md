# Dispatch for worker_m2_repl (Replacement Backend and AI Worker)
Role: teamwork_preview_worker
Target Directory: .agents/worker_m2_repl/

## 2026-09-02T15:03:13Z
You are worker_m2_repl (teamwork_preview_worker) taking over Milestone 2: FastAPI Backend & Grounded AI Supervisor for the AI Warehouse Intelligence project.

Your working directory: C:/Users/hp/.gemini/antigravity/scratch/ai-warehouse-intelligence/.agents/worker_m2_repl
Workspace root: C:/Users/hp/.gemini/antigravity/scratch/ai-warehouse-intelligence

Please read the following documents first:
- C:/Users/hp/.gemini/antigravity/scratch/ai-warehouse-intelligence/ORIGINAL_REQUEST.md
- C:/Users/hp/.gemini/antigravity/scratch/ai-warehouse-intelligence/PROJECT.md
- C:/Users/hp/.gemini/antigravity/scratch/ai-warehouse-intelligence/TEST_INFRA.md

Your exclusive write ownership:
- backend/api/ (events.py, video.py, dashboard.py, alerts.py, assistant.py, __init__.py)
- backend/services/ (event_service.py, video_service.py, dashboard_service.py, alert_service.py, __init__.py)
- backend/database/ (models.py, session.py, database.py, __init__.py)
- backend/risk/ (risk_engine.py, risk_explanation.py, __init__.py)
- backend/assistant/ (assistant.py, __init__.py)
- backend/main.py
- tests/api/

Tasks:
1. Inspect the backend code and API endpoints.
2. Verify and implement all required FastAPI endpoints:
   - `/api/events`, `/api/events/{id}`, `/api/events/high-risk`, `/api/events/today`, `/api/events/by-location`, `/api/statistics` (support filtering by risk_level, event_type, location, date).
   - `/api/dashboard/summary`, `/api/dashboard/trends`, `/api/dashboard/locations`.
   - `/api/alerts/recent`, `/api/alerts/acknowledge/{id}`, `/api/alerts/stats`.
   - `/api/video/upload`, `/api/video/analyze`, `/api/video/status/{job_id}`, `/api/video/jobs`.
   - `/api/assistant/query` and `/assistant/query`.
3. Verify Risk Scoring & Damage Prevention Engine (`backend/risk/`):
   - Multi-factor risk scoring matching `configs/risk.yaml` (base severity + velocity modifier + height modifier + equipment modifier + location modifier * confidence).
   - Damage-prevention explainability (non-accusatory explanations and actionable recommendations for LOW, MEDIUM, HIGH, CRITICAL).
4. Verify Database & Storage (`backend/database/`):
   - SQLite persistence with async SQLAlchemy session and fallback to sync SQLite for CLI/scripts.
   - Models for Event, VideoJob, Alert, Camera, Metric.
5. Verify Grounded AI Supervisor (`backend/assistant/assistant.py`):
   - Telemetry tool grounding (`get_events`, `get_statistics`, `get_high_risk_events`, `get_location_stats`, `get_warehouse_rules`).
   - Strict domain guardrails (refuses ungrounded or non-warehouse queries, never fabricates events).
6. Run API tests (`pytest tests/api/ -v`) and full test suite (`pytest tests/ -v`). Ensure all tests pass.
7. Write your handoff report to `C:/Users/hp/.gemini/antigravity/scratch/ai-warehouse-intelligence/.agents/worker_m2_repl/handoff.md` with sections: Observation, Logic Chain, Caveats, Conclusion, Verification Method.
