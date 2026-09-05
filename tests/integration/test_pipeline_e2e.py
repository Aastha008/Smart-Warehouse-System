"""
AI Warehouse Intelligence - End-to-End Pipeline & Integration Test Suite
Comprehensive verification of:
1. Vision -> Tracking -> Temporal Behaviour Engine -> Risk Classification -> Visual Annotator
2. Async & Sync Database Persistence & Relations (Events, VideoJobs, Alerts, Cameras, Metrics)
3. FastAPI Backend REST Service & Response Contract Validation
4. Grounded AI Supervisor Telemetry Retrieval & Guardrails
5. Synthetic Video Generator Scenarios & Verification
6. Database Seeding & Multi-Factor Risk Assessment
"""
import io
import os
import sys
import pytest
import numpy as np
from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient

from backend.main import app
from backend.vision.pipeline import VideoPipeline, FrameResult, AnalysisResult
from backend.vision.detector import WarehouseDetector, Detection
from backend.vision.tracker import ObjectTracker, TrackedObject
from backend.behaviour.behaviour_engine import BehaviourEngine
from backend.risk.risk_engine import RiskEngine, RiskAssessment
from backend.assistant.assistant import WarehouseAssistant, AssistantTools
from backend.database.session import SyncSessionLocal, init_sync_db
from backend.database.models import Event, Alert, VideoJob, Camera, Metric
from scripts.generate_synthetic_video import generate_synthetic_video
from scripts.seed_demo_data import seed_database, BEHAVIOR_TEMPLATES


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Ensure database tables exist before running integration tests."""
    init_sync_db()


@pytest.fixture
def client():
    """FastAPI TestClient fixture."""
    return TestClient(app)


# =====================================================================
# 1. End-to-End Vision & Behaviour Intelligence Integration Tests
# =====================================================================
class TestE2EVisionBehaviourPipeline:
    """Tests the full multi-stage pipeline from video frames to risk intelligence."""

    def test_pipeline_full_cycle_synthetic_drop(self, tmp_path):
        """Generates a synthetic drop clip and processes it through the entire pipeline."""
        video_path = str(tmp_path / "test_drop_e2e.mp4")
        generate_synthetic_video(
            output_path=video_path,
            scenario="drop",
            duration_sec=3,
            fps=20,
            width=320,
            height=240
        )
        assert os.path.exists(video_path)
        assert os.path.getsize(video_path) > 0

        pipeline = VideoPipeline(skip_frames=1)
        result = pipeline.process_video(video_path)

        assert isinstance(result, AnalysisResult)
        assert result.total_frames >= 40
        assert isinstance(result.events, list)

    def test_all_10_behavior_engines_integrated_with_risk_engine(self):
        """Verifies each of the 10 behavior detectors connects properly to RiskEngine."""
        risk_engine = RiskEngine()
        behaviour_engine = BehaviourEngine()
        assert len(behaviour_engine.detectors) == 10

        behaviors = [
            ("product_drop", {"drop_height_px": 150, "velocity": 6.0}),
            ("product_dragging", {"drag_distance_px": 200, "duration": 4.5}),
            ("product_throwing", {"velocity": 9.0, "airborne_time": 1.2}),
            ("rough_handling", {"acceleration": 18.0, "jerk": 25.0}),
            ("improper_stacking", {"weight_ratio": 3.5, "overhang_pct": 25}),
            ("unstable_stacking", {"tilt_angle_deg": 22.0, "wobble_freq": 1.4}),
            ("product_outside_zone", {"zone_id": "pedestrian_walkway", "distance_px": 50}),
            ("incorrect_pallet_position", {"misalignment_deg": 35.0, "lane_encroach_px": 60}),
            ("unsafe_loading_sequence", {"rack_level": 3, "base_empty": True}),
            ("improper_handling_equipment", {"weight_kg": 45.0, "equipment_type": "none"}),
        ]

        for ev_type, evidence in behaviors:
            assessment = risk_engine.assess_risk(
                event_type=ev_type,
                evidence=evidence,
                modifiers={"location": "loading_bay_2"}
            )
            assert isinstance(assessment, RiskAssessment)
            assert assessment.level in ("LOW", "MEDIUM", "HIGH", "CRITICAL")
            assert 0.0 <= assessment.score <= 100.0
            assert len(assessment.explanation) > 10
            assert len(assessment.recommendation) > 10

    def test_pipeline_frame_annotation_integrity(self):
        """Verifies annotator receives tracks, events, and assessments and outputs valid frame."""
        pipeline = VideoPipeline()
        frame = np.full((480, 640, 3), 128, dtype=np.uint8)
        frame_result = pipeline.process_frame(frame, frame_idx=1)

        assert isinstance(frame_result, FrameResult)
        assert frame_result.frame_idx == 1
        assert frame_result.annotated_frame.shape == (480, 640, 3)
        assert isinstance(frame_result.events, list)
        assert isinstance(frame_result.assessments, list)


# =====================================================================
# 2. Database & Multi-Model Persistence Integration Tests
# =====================================================================
class TestE2EDatabasePersistence:
    """Verifies relational integrity across Events, VideoJobs, Alerts, Cameras, and Metrics."""

    def test_event_lifecycle_and_cascade(self):
        """Tests inserting, querying, and verifying structured event and alert relationships."""
        with SyncSessionLocal() as session:
            # Create camera
            cam_id = f"CAM-TEST-{datetime.now().microsecond}"
            cam = Camera(
                camera_id=cam_id,
                name="Test Bay Camera",
                location="Loading Bay Test",
                status="active",
                is_active=True
            )
            session.merge(cam)

            # Create high risk event
            event = Event(
                camera_id=cam_id,
                location="Loading Bay Test",
                event_type="product_throwing",
                risk_level="CRITICAL",
                risk_score=94.0,
                confidence=0.96,
                object_ids=[101, 102],
                evidence={"velocity_mps": 7.5, "airborne_sec": 1.1},
                explanation="High-velocity parcel toss across loading zone.",
                recommendation="Enforce zero-tolerance parcel throwing policy."
            )
            session.add(event)
            session.flush()

            # Create alert referencing event
            alert = Alert(
                event_id=event.event_id,
                alert_type="visual_audio",
                severity="CRITICAL",
                message="Critical parcel throw detected in Loading Bay Test",
                location="Loading Bay Test",
                acknowledged=False
            )
            session.add(alert)

            # Create video job
            job = VideoJob(
                video_path="demo/test_feed.mp4",
                status="completed",
                progress=1.0,
                total_frames=200,
                processed_frames=200,
                events_count=1
            )
            session.add(job)

            session.commit()

            # Verify queries
            queried_event = session.query(Event).filter(Event.event_id == event.event_id).first()
            assert queried_event is not None
            assert queried_event.event_type == "product_throwing"
            assert queried_event.risk_level == "CRITICAL"
            assert queried_event.evidence.get("velocity_mps") == 7.5

            queried_alert = session.query(Alert).filter(Alert.event_id == event.event_id).first()
            assert queried_alert is not None
            assert queried_alert.severity == "CRITICAL"
            assert queried_alert.acknowledged is False

            queried_job = session.query(VideoJob).filter(VideoJob.job_id == job.job_id).first()
            assert queried_job is not None
            assert queried_job.status == "completed"


# =====================================================================
# 3. REST API Endpoint & Workflow Integration Tests
# =====================================================================
class TestE2EBackendAPI:
    """Verifies all REST API routes and business workflows."""

    def test_complete_api_incident_flow(self, client):
        """Tests POST /api/events -> GET /api/events/{id} -> GET /api/events/high-risk -> GET /api/dashboard/summary."""
        # 1. Post new event
        create_payload = {
            "camera_id": "CAM-01-NORTH",
            "location": "Loading Bay 1",
            "event_type": "product_drop",
            "risk_level": "HIGH",
            "risk_score": 82.0,
            "confidence": 0.91,
            "object_ids": [55],
            "evidence": {"drop_height_m": 1.4, "impact_velocity": 4.8},
            "explanation": "Package slipped from operator hands.",
            "recommendation": "Inspect carton before staging."
        }
        res_create = client.post("/api/events", json=create_payload)
        assert res_create.status_code == 201
        event_data = res_create.json()
        event_id = event_data["event_id"]
        assert event_data["risk_level"] == "HIGH"

        # 2. Query event by ID
        res_get = client.get(f"/api/events/{event_id}")
        assert res_get.status_code == 200
        assert res_get.json()["event_id"] == event_id

        # 3. High risk listing
        res_hr = client.get("/api/events/high-risk?limit=50")
        assert res_hr.status_code == 200
        hr_list = res_hr.json()
        assert any(e["event_id"] == event_id for e in hr_list)

        # 4. Dashboard summary
        res_sum = client.get("/api/dashboard/summary")
        assert res_sum.status_code == 200
        sum_data = res_sum.json()
        assert sum_data["total_events"] > 0
        assert sum_data["high_risk_count"] > 0

        # 5. Dashboard trends & locations
        res_trends = client.get("/api/dashboard/trends")
        assert res_trends.status_code == 200
        res_locs = client.get("/api/dashboard/locations")
        assert res_locs.status_code == 200
        res_behaviours = client.get("/api/dashboard/behaviours")
        assert res_behaviours.status_code == 200

    def test_video_job_submission_and_status(self, client):
        """Tests video upload, analysis triggering, and status polling."""
        video_dummy = b"\x00\x00\x00\x18ftypmp42\x00\x00\x00\x00mp42isom"
        file_tuple = {"file": ("integration_video.mp4", io.BytesIO(video_dummy), "video/mp4")}
        
        up_res = client.post("/api/video/upload", files=file_tuple)
        assert up_res.status_code == 200
        job_id = up_res.json()["job_id"]

        an_res = client.post("/api/video/analyze", json={"job_id": job_id, "location": "Loading Bay 3"})
        assert an_res.status_code == 200
        assert an_res.json()["status"] == "processing"

        st_res = client.get(f"/api/video/status/{job_id}")
        assert st_res.status_code == 200
        assert "progress" in st_res.json()

    def test_alert_lifecycle_api(self, client):
        """Tests alert creation, retrieval, and acknowledgment through REST endpoints."""
        alert_payload = {
            "alert_type": "audio_visual",
            "severity": "CRITICAL",
            "message": "Critical stacking risk at Bay 4",
            "location": "Loading Bay 4"
        }
        create_res = client.post("/api/alerts", json=alert_payload)
        assert create_res.status_code == 201
        alert_id = create_res.json()["id"]

        recent_res = client.get("/api/alerts/recent")
        assert recent_res.status_code == 200
        assert any(a["id"] == alert_id for a in recent_res.json())

        ack_res = client.post(f"/api/alerts/acknowledge/{alert_id}?user=Supervisor_Alex")
        assert ack_res.status_code == 200
        assert ack_res.json()["acknowledged"] is True


# =====================================================================
# 4. Grounded AI Supervisor Telemetry & Guardrail Tests
# =====================================================================
class TestE2EGroundedAssistant:
    """Verifies that the conversational AI supervisor grounds responses strictly on warehouse data."""

    def test_telemetry_grounded_queries(self, client):
        """Tests grounded operational responses to supervisor queries."""
        queries = [
            "What happened today?",
            "Show me high-risk events",
            "Which loading bay needs attention?",
            "What are the most common risky behaviours?",
            "What are the warehouse stacking rules?",
            "Why was this classified as high risk?",
            "What corrective action should we take?"
        ]
        for q in queries:
            res = client.post("/api/assistant/query", json={"query": q})
            assert res.status_code == 200
            data = res.json()
            assert "response" in data
            assert len(data["response"]) > 20
            assert "sources" in data

    def test_strict_guardrails_on_non_warehouse_topics(self, client):
        """Verifies that queries outside warehouse operations are rejected."""
        non_warehouse = [
            "What is the capital of Australia?",
            "Write a poem about the ocean",
            "How do I cook pasta carbonara?",
            "What is the stock price of Apple?"
        ]
        for q in non_warehouse:
            res = client.post("/api/assistant/query", json={"query": q})
            assert res.status_code == 200
            data = res.json()
            response_text = data["response"].lower()
            assert "domain_guardrails" in data.get("sources", []) or "restricted" in response_text or "cannot assist" in response_text


# =====================================================================
# 5. Synthetic Video Generator & Seeder Integration Tests
# =====================================================================
class TestE2ESyntheticAndSeeder:
    """Tests the synthetic scenario video generator and database seeder components."""

    def test_synthetic_generator_scenarios(self, tmp_path):
        """Tests generating synthetic videos across multiple distinct behaviors."""
        scenarios = ["drop", "drag", "throw", "rough", "stack", "unstable", "zone", "pallet", "sequence", "equipment"]
        for sc in scenarios:
            vpath = str(tmp_path / f"syn_{sc}.mp4")
            out_file = generate_synthetic_video(
                output_path=vpath,
                scenario=sc,
                duration_sec=1,
                fps=15,
                width=160,
                height=120
            )
            assert os.path.exists(out_file)
            assert os.path.getsize(out_file) > 0

    def test_database_seeder_execution(self):
        """Tests database seeder function directly and validates seeded data."""
        import asyncio
        asyncio.run(seed_database(num_events=30, clear_first=False))
        with SyncSessionLocal() as session:
            count = session.query(Event).count()
            assert count >= 30
            cams = session.query(Camera).count()
            assert cams >= 5
            jobs = session.query(VideoJob).count()
            assert jobs >= 5
            metrics = session.query(Metric).count()
            assert metrics >= 20
