## 2026-09-02T12:47:24Z
Investigate the authoritative source of truth for:
1. R1: Video ingestion, YOLO entity detection (person, carton, package, pallet, trolley, forklift, vehicle), ByteTrack/BoT-SORT tracking.
2. R2: Temporal behavior engine (all 10 behaviors: product_drop, product_dragging, product_throwing, rough_handling, improper_stacking, unstable_stacking, product_outside_zone, incorrect_pallet_position, unsafe_loading_sequence, improper_handling_equipment) and YAML configs in configs/.
3. R3: Risk scoring engine (LOW, MEDIUM, HIGH, CRITICAL), observed vs potential vs damage logic, SQLite/PostgreSQL incident storage, database schema.
4. R4: FastAPI backend endpoints (/video/*, /events/*, /dashboard/*, /assistant/*), error handling, async jobs, and backend architecture.
Inspect existing files in backend/, configs/, models/, training/, create_backend.py, create_pipeline.py, warehouse.db, etc.
Write analysis.md and handoff.md.
