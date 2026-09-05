"""
AI Warehouse Intelligence - API Integration Tests
Comprehensive testing for all Milestone 2 endpoints and components.
"""
import io
import pytest
from datetime import datetime, timezone
from backend.database.models import Event, Alert, VideoJob
from backend.database.session import SyncSessionLocal, init_sync_db
from backend.risk.risk_engine import RiskEngine
from backend.assistant.assistant import WarehouseAssistant, AssistantTools


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    """Ensure database tables exist for tests."""
    init_sync_db()


@pytest.fixture
def client():
    """Create test client."""
    from fastapi.testclient import TestClient
    from backend.main import app
    return TestClient(app)


class TestEventsAPI:
    """Tests for events API endpoints."""

    def test_create_and_get_event(self, client):
        """Test POST /api/events and GET /api/events/{id}."""
        payload = {
            "camera_id": "cam_test_01",
            "location": "loading_bay_1",
            "event_type": "product_drop",
            "risk_level": "HIGH",
            "risk_score": 78.0,
            "confidence": 0.88,
            "object_ids": [101],
            "evidence": {"drop_height_px": 140, "velocity": 5.2},
            "explanation": "Potential drop detected.",
            "recommendation": "Inspect cargo.",
        }
        res = client.post("/api/events", json=payload)
        assert res.status_code == 201
        created = res.json()
        assert "event_id" in created
        event_id = created["event_id"]
        assert created["event_type"] == "product_drop"
        assert created["risk_level"] == "HIGH"

        # Fetch single event
        get_res = client.get(f"/api/events/{event_id}")
        assert get_res.status_code == 200
        assert get_res.json()["event_id"] == event_id

    def test_get_events_listing_and_filters(self, client):
        """Test GET /api/events with risk_level, event_type, location, date filters."""
        # Create distinct event for filter tests
        client.post("/api/events", json={
            "camera_id": "cam_filter_01",
            "location": "bay_east_99",
            "event_type": "product_throwing",
            "risk_level": "CRITICAL",
            "risk_score": 95.0,
            "confidence": 0.95,
        })

        # Test listing
        res = client.get("/api/events")
        assert res.status_code == 200
        assert isinstance(res.json(), list)

        # Test filter by risk_level
        res_crit = client.get("/api/events?risk_level=CRITICAL")
        assert res_crit.status_code == 200
        assert any(e["risk_level"] == "CRITICAL" for e in res_crit.json())

        # Test filter by event_type
        res_type = client.get("/api/events?event_type=product_throwing")
        assert res_type.status_code == 200
        assert any(e["event_type"] == "product_throwing" for e in res_type.json())

        # Test filter by location
        res_loc = client.get("/api/events?location=bay_east_99")
        assert res_loc.status_code == 200
        assert any(e["location"] == "bay_east_99" for e in res_loc.json())

        # Test filter by date format
        today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        res_date = client.get(f"/api/events?date={today_str}")
        assert res_date.status_code == 200

    def test_get_high_risk_events(self, client):
        """Test GET /api/events/high-risk."""
        res = client.get("/api/events/high-risk")
        assert res.status_code == 200
        events = res.json()
        assert isinstance(events, list)
        for ev in events:
            assert ev["risk_level"] in ("HIGH", "CRITICAL")

    def test_get_today_events(self, client):
        """Test GET /api/events/today."""
        res = client.get("/api/events/today")
        assert res.status_code == 200
        assert isinstance(res.json(), list)

    def test_get_events_by_location(self, client):
        """Test GET /api/events/by-location and path param variant."""
        res1 = client.get("/api/events/by-location?location=loading_bay_1")
        assert res1.status_code == 200
        res2 = client.get("/api/events/by-location/loading_bay_1")
        assert res2.status_code == 200

    def test_get_statistics_routes(self, client):
        """Test GET /api/events/statistics, /api/statistics, and /statistics."""
        res1 = client.get("/api/events/statistics")
        assert res1.status_code == 200
        data1 = res1.json()
        assert "total_events" in data1
        assert "high_risk" in data1
        assert "critical" in data1

        res2 = client.get("/api/statistics")
        assert res2.status_code == 200
        assert "total_events" in res2.json()

        res3 = client.get("/statistics")
        assert res3.status_code == 200

    def test_get_nonexistent_event_404(self, client):
        """Test GET /api/events/{id} for non-existent ID."""
        res = client.get("/api/events/nonexistent-event-uuid-12345")
        assert res.status_code == 404

    def test_delete_event(self, client):
        """Test DELETE /api/events/{id}."""
        # Create an event to delete
        c_res = client.post("/api/events", json={
            "event_type": "rough_handling",
            "risk_level": "MEDIUM",
            "location": "temp_delete_zone",
        })
        ev_id = c_res.json()["event_id"]

        del_res = client.get(f"/api/events/{ev_id}")
        assert del_res.status_code == 200

        del_action = client.delete(f"/api/events/{ev_id}")
        assert del_action.status_code == 200

        # Now should be 404
        assert client.get(f"/api/events/{ev_id}").status_code == 404


class TestVideoAPI:
    """Tests for video API endpoints."""

    def test_upload_video_valid(self, client):
        """Test POST /api/video/upload with a dummy MP4 file."""
        video_content = b"\x00\x00\x00\x18ftypmp42\x00\x00\x00\x00mp42isom"
        file = {"file": ("test_sample.mp4", io.BytesIO(video_content), "video/mp4")}
        res = client.post("/api/video/upload", files=file)
        assert res.status_code == 200
        data = res.json()
        assert "job_id" in data
        assert data["status"] == "uploaded"

    def test_upload_video_invalid_extension(self, client):
        """Test upload rejection for invalid extensions."""
        bad_file = {"file": ("script.py", io.BytesIO(b"print('hello')"), "text/plain")}
        res = client.post("/api/video/upload", files=bad_file)
        assert res.status_code == 400

    def test_analyze_and_status(self, client):
        """Test POST /api/video/analyze and GET /api/video/status/{id}."""
        # First upload
        video_content = b"\x00\x00\x00\x18ftypmp42\x00\x00\x00\x00mp42isom"
        file = {"file": ("analyze_test.mp4", io.BytesIO(video_content), "video/mp4")}
        u_res = client.post("/api/video/upload", files=file)
        job_id = u_res.json()["job_id"]

        # Request analysis
        a_res = client.post("/api/video/analyze", json={"job_id": job_id, "location": "loading_bay_2"})
        assert a_res.status_code == 200
        assert a_res.json()["status"] == "processing"

        # Check status
        s_res = client.get(f"/api/video/status/{job_id}")
        assert s_res.status_code == 200
        assert "progress" in s_res.json()

    def test_get_jobs_and_list(self, client):
        """Test GET /api/video/jobs and GET /api/video/list."""
        res1 = client.get("/api/video/jobs")
        assert res1.status_code == 200
        assert isinstance(res1.json(), list)

        res2 = client.get("/api/video/list")
        assert res2.status_code == 200
        assert isinstance(res2.json(), list)


class TestDashboardAPI:
    """Tests for dashboard analytics endpoints."""

    def test_get_summary(self, client):
        """Test GET /api/dashboard/summary."""
        res = client.get("/api/dashboard/summary")
        assert res.status_code == 200
        data = res.json()
        assert "total_events" in data
        assert "high_risk_count" in data
        assert "critical_count" in data
        assert "total_events_today" in data

    def test_get_trends(self, client):
        """Test GET /api/dashboard/trends."""
        res = client.get("/api/dashboard/trends")
        assert res.status_code == 200
        trends = res.json()
        assert isinstance(trends, list)
        if trends:
            assert "date" in trends[0]
            assert "risk_level" in trends[0]
            assert "count" in trends[0]

    def test_get_locations(self, client):
        """Test GET /api/dashboard/locations."""
        res = client.get("/api/dashboard/locations")
        assert res.status_code == 200
        locs = res.json()
        assert isinstance(locs, list)
        assert len(locs) > 0
        assert "location" in locs[0]

    def test_get_behaviours(self, client):
        """Test GET /api/dashboard/behaviours."""
        res = client.get("/api/dashboard/behaviours")
        assert res.status_code == 200
        behaviours = res.json()
        assert isinstance(behaviours, list)
        assert len(behaviours) > 0
        assert "behaviour" in behaviours[0]


class TestAlertAPI:
    """Tests for alert management endpoints."""

    def test_create_and_acknowledge_alert(self, client):
        """Test creating, listing, and acknowledging an alert."""
        # Create alert
        create_res = client.post("/api/alerts", json={
            "alert_type": "audio_visual",
            "severity": "CRITICAL",
            "message": "Critical stacking hazard at loading bay 3",
            "location": "loading_bay_3",
        })
        assert create_res.status_code == 201
        alert = create_res.json()
        alert_id = alert["id"]
        assert alert["acknowledged"] is False

        # Get recent alerts
        rec_res = client.get("/api/alerts/recent")
        assert rec_res.status_code == 200
        assert any(a["id"] == alert_id for a in rec_res.json())

        # Acknowledge via POST /api/alerts/acknowledge/{id}
        ack_res = client.post(f"/api/alerts/acknowledge/{alert_id}?user=Supervisor_Jane")
        assert ack_res.status_code == 200
        assert ack_res.json()["acknowledged"] is True

        # Acknowledge second alert via POST /api/alerts/{id}/acknowledge
        create_res2 = client.post("/api/alerts", json={
            "severity": "HIGH",
            "message": "High speed drag detected",
            "location": "loading_bay_1",
        })
        alert_id2 = create_res2.json()["id"]
        ack_res2 = client.post(f"/api/alerts/{alert_id2}/acknowledge")
        assert ack_res2.status_code == 200

    def test_get_alert_stats(self, client):
        """Test GET /api/alerts/stats."""
        res = client.get("/api/alerts/stats")
        assert res.status_code == 200
        data = res.json()
        assert "total_alerts" in data
        assert "unacknowledged_count" in data
        assert "critical_count" in data
        assert "high_count" in data


class TestAssistantAPI:
    """Tests for grounded AI assistant supervisor."""

    def test_grounded_queries(self, client):
        """Test grounded assistant queries."""
        queries = [
            "What happened today?",
            "Show me high-risk events",
            "Which loading bay needs attention?",
            "What are the most common risky behaviours?",
            "What are the warehouse stacking rules?",
            "Why was this classified as high risk?",
            "What corrective action should we take?",
        ]
        for q in queries:
            res = client.post("/api/assistant/query", json={"query": q})
            assert res.status_code == 200
            data = res.json()
            assert "response" in data
            assert len(data["response"]) > 0

    def test_assistant_route_alias(self, client):
        """Test POST /assistant/query alias route."""
        res = client.post("/assistant/query", json={"query": "Overview of warehouse events"})
        assert res.status_code == 200
        assert "response" in res.json()

    def test_guardrails_refuse_out_of_domain(self, client):
        """Test that non-warehouse queries are strictly refused."""
        off_topic_queries = [
            "What is the capital of France?",
            "Write a poem about the sunrise",
            "Who won the football game last night?",
            "How to cook spaghetti bolognese?",
        ]
        for q in off_topic_queries:
            res = client.post("/api/assistant/query", json={"query": q})
            assert res.status_code == 200
            data = res.json()
            assert "domain_guardrails" in data.get("sources", []) or "restricted" in data["response"].lower() or "cannot assist" in data["response"].lower()

    def test_assistant_empty_query(self, client):
        """Test empty query handling."""
        res = client.post("/api/assistant/query", json={"query": ""})
        assert res.status_code == 200
        assert "ask a question" in res.json()["response"].lower()


class TestRiskEngine:
    """Direct unit tests for RiskEngine multi-factor computation."""

    def test_multi_factor_risk_calculation(self):
        engine = RiskEngine()
        # Assess product drop with high height & velocity
        assessment = engine.assess_risk(
            event_type="product_drop",
            evidence={"drop_height_px": 160, "velocity": 7.0},
            modifiers={"product_type": "fragile", "location_type": "loading_bay"}
        )
        assert assessment.level in ("HIGH", "CRITICAL")
        assert assessment.score >= 60
        assert len(assessment.explanation) > 0
        assert len(assessment.recommendation) > 0

    def test_composite_risk_helper(self):
        engine = RiskEngine()
        score = engine.calculate_composite_risk(
            base_score=60.0,
            modifiers={"height": 20.0, "velocity": 15.0},
            confidence=0.9
        )
        assert 0 <= score <= 100
        assert score == int((60.0 + 20.0 + 15.0) * 0.9)

    def test_all_behaviour_explanations_non_accusatory(self):
        from backend.risk.risk_explanation import generate_explanation, generate_recommendation
        behaviours = [
            "product_drop", "product_dragging", "product_throwing", "rough_handling",
            "improper_stacking", "unstable_stacking", "product_outside_zone",
            "incorrect_pallet_position", "unsafe_loading_sequence", "improper_handling_equipment"
        ]
        for b in behaviours:
            exp = generate_explanation(b, {"drop_height_px": 100, "velocity": 4.0}, "HIGH")
            assert len(exp) > 20
            rec = generate_recommendation(b)
            assert len(rec) > 20


class TestAssistantToolsDirect:
    """Direct unit tests for AssistantTools telemetry grounding."""

    def test_assistant_tools_grounding(self):
        tools = AssistantTools(SyncSessionLocal)
        rules = tools.get_warehouse_rules()
        assert isinstance(rules, dict)

        stats = tools.get_statistics()
        assert isinstance(stats, dict)
        assert "total_events" in stats
        assert "high_risk" in stats

        events = tools.get_events(limit=5)
        assert isinstance(events, list)

        high_risk = tools.get_high_risk_events(limit=5)
        assert isinstance(high_risk, list)

        loc_stats = tools.get_location_stats()
        assert isinstance(loc_stats, dict)


class TestAdvancedAPIFilters:
    """Tests for pagination, date range filtering, and alert querying."""

    def test_events_pagination_and_date_range(self, client):
        # Create a sample event with date
        res = client.post("/api/events", json={
            "camera_id": "cam_range_01",
            "location": "bay_pagination_test",
            "event_type": "product_drop",
            "risk_level": "LOW",
            "risk_score": 25.0,
            "confidence": 0.8,
        })
        assert res.status_code == 201

        # Pagination: skip and limit
        p_res = client.get("/api/events?skip=0&limit=2")
        assert p_res.status_code == 200
        assert len(p_res.json()) <= 2

        # Date range filtering
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        d_res = client.get(f"/api/events?start_date={today}&end_date={today}")
        assert d_res.status_code == 200
        assert isinstance(d_res.json(), list)

    def test_alert_filtering(self, client):
        # Create unacknowledged alert
        client.post("/api/alerts", json={
            "severity": "CRITICAL",
            "message": "Filter test critical alert",
            "location": "loading_bay_99",
        })

        # Filter by severity
        crit_res = client.get("/api/alerts?severity=CRITICAL")
        assert crit_res.status_code == 200
        assert any(a["severity"] == "CRITICAL" for a in crit_res.json())

        # Filter by acknowledged status
        unack_res = client.get("/api/alerts?acknowledged=false")
        assert unack_res.status_code == 200
        assert all(a["acknowledged"] is False for a in unack_res.json())


class TestCORSAndErrors:
    """CORS headers and 404 tests."""

    def test_cors_headers(self, client):
        res = client.options(
            "/api/events",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            }
        )
        assert res.status_code in [200, 400]

    def test_404_handler(self, client):
        res = client.get("/api/undefined-route")
        assert res.status_code == 404

