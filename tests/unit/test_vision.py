"""
AI Warehouse Intelligence - Unit Tests for Vision Pipeline
"""
import pytest
import numpy as np
from unittest.mock import MagicMock, patch
from dataclasses import dataclass


# ============================================================
# Test Detection
# ============================================================

class TestWarehouseDetector:
    """Tests for the object detection module."""

    def test_detector_initialization(self):
        """Test detector can be initialized."""
        try:
            from backend.vision.detector import WarehouseDetector
            detector = WarehouseDetector()
            assert detector is not None
        except ImportError:
            pytest.skip("Vision module not yet available")

    def test_detection_output_format(self):
        """Test that detection produces proper output format."""
        try:
            from backend.vision.detector import WarehouseDetector, Detection
            detector = WarehouseDetector()
            
            # Create a test frame
            frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
            detections = detector.detect(frame)
            
            assert isinstance(detections, list)
            for det in detections:
                assert hasattr(det, 'bbox')
                assert hasattr(det, 'class_name')
                assert hasattr(det, 'confidence')
                assert 0 <= det.confidence <= 1
        except ImportError:
            pytest.skip("Vision module not yet available")

    def test_empty_frame_handling(self):
        """Test detector handles empty/black frames."""
        try:
            from backend.vision.detector import WarehouseDetector
            detector = WarehouseDetector()
            
            # Black frame - should return empty or minimal detections
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            detections = detector.detect(frame)
            assert isinstance(detections, list)
        except ImportError:
            pytest.skip("Vision module not yet available")


# ============================================================
# Test Tracking
# ============================================================

class TestObjectTracker:
    """Tests for the object tracking module."""

    def test_tracker_initialization(self):
        """Test tracker can be initialized."""
        try:
            from backend.vision.tracker import ObjectTracker
            tracker = ObjectTracker()
            assert tracker is not None
        except ImportError:
            pytest.skip("Tracking module not yet available")

    def test_track_assignment(self):
        """Test that tracker assigns consistent IDs."""
        try:
            from backend.vision.tracker import ObjectTracker
            from backend.vision.detector import Detection
            
            tracker = ObjectTracker()
            
            # Simulate detections in consecutive frames
            det1 = [Detection(bbox=[100, 100, 200, 200], class_name="person", confidence=0.9)]
            tracks1 = tracker.update(det1, frame_idx=0)
            
            # Same object slightly moved
            det2 = [Detection(bbox=[105, 105, 205, 205], class_name="person", confidence=0.9)]
            tracks2 = tracker.update(det2, frame_idx=1)
            
            assert len(tracks1) >= 1
            assert len(tracks2) >= 1
            # Same object should keep same ID
            if len(tracks1) > 0 and len(tracks2) > 0:
                assert tracks1[0].track_id == tracks2[0].track_id
        except ImportError:
            pytest.skip("Tracking module not yet available")


# ============================================================
# Test Motion Analysis
# ============================================================

class TestMotionAnalyzer:
    """Tests for motion feature extraction."""

    def test_velocity_calculation(self):
        """Test velocity is calculated correctly."""
        try:
            from backend.vision.motion import MotionAnalyzer
            analyzer = MotionAnalyzer()
            
            # Simulate trajectory: object moving right
            trajectory = [
                (100, 200),  # frame 0
                (110, 200),  # frame 1
                (120, 200),  # frame 2
            ]
            
            velocity = analyzer.compute_velocity(trajectory)
            assert velocity is not None
            assert velocity[0] > 0  # moving right
            assert abs(velocity[1]) < 1  # not moving vertically
        except ImportError:
            pytest.skip("Motion module not yet available")

    def test_fall_detection(self):
        """Test downward motion is detected."""
        try:
            from backend.vision.motion import MotionAnalyzer
            analyzer = MotionAnalyzer()
            
            # Simulate trajectory: object falling
            trajectory = [
                (200, 100),  # frame 0
                (200, 130),  # frame 1
                (200, 170),  # frame 2
                (200, 220),  # frame 3
            ]
            
            velocity = analyzer.compute_velocity(trajectory)
            assert velocity is not None
            assert velocity[1] > 0  # moving downward (y increases)
        except ImportError:
            pytest.skip("Motion module not yet available")


# ============================================================
# Test Behaviour Detection
# ============================================================

class TestDropDetector:
    """Tests for product drop detection."""

    def test_drop_detection_basic(self):
        """Test basic drop detection logic."""
        try:
            from backend.behaviour.drop_detector import DropDetector
            detector = DropDetector()
            assert detector is not None
        except ImportError:
            pytest.skip("Behaviour module not yet available")

    def test_drop_event_structure(self):
        """Test drop event has required fields."""
        try:
            from backend.behaviour.drop_detector import DropDetector
            from backend.behaviour.base_detector import BehaviourEvent
            
            # A BehaviourEvent should have these fields
            event = BehaviourEvent(
                event_type="product_drop",
                object_id=1,
                frame_idx=100,
                confidence=0.8,
                location="loading_bay_1",
                evidence={"drop_height_px": 120, "velocity": 4.2},
            )
            
            assert event.event_type == "product_drop"
            assert event.confidence == 0.8
            assert "drop_height_px" in event.evidence
        except ImportError:
            pytest.skip("Behaviour module not yet available")


class TestDragDetector:
    """Tests for product dragging detection."""

    def test_drag_detection_basic(self):
        """Test basic drag detection."""
        try:
            from backend.behaviour.drag_detector import DragDetector
            detector = DragDetector()
            assert detector is not None
        except ImportError:
            pytest.skip("Behaviour module not yet available")


class TestBehaviourEngine:
    """Tests for the behaviour engine."""

    def test_engine_initialization(self):
        """Test behaviour engine initializes all detectors."""
        from backend.behaviour.behaviour_engine import BehaviourEngine
        engine = BehaviourEngine()
        assert engine is not None
        assert len(engine.detectors) >= 10


# ============================================================
# Test Annotator & Pipeline
# ============================================================

class TestAnnotator:
    """Tests for frame annotation."""

    def test_annotator_colors(self):
        """Test annotator has all severity colors including CRITICAL."""
        from backend.vision.annotator import Annotator
        annotator = Annotator()
        assert "CRITICAL" in annotator.colors
        assert annotator.colors["CRITICAL"] == (0, 0, 220)

    def test_annotator_draws_frame(self):
        """Test annotator renders tracks and alerts onto frame."""
        from backend.vision.annotator import Annotator
        from backend.vision.tracker import TrackedObject
        from backend.behaviour.base_detector import BehaviourEvent
        from backend.risk.risk_engine import RiskAssessment

        annotator = Annotator()
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        tracks = [
            TrackedObject(object_id=1, class_name="package", bbox=(100, 100, 200, 200), center=(150, 150))
        ]
        events = [
            BehaviourEvent(event_type="product_drop", object_id=1, frame_idx=1, confidence=0.9, evidence={"drop_height_px": 50})
        ]
        assessments = [
            RiskAssessment(level="CRITICAL", score=90, explanation="High risk drop", recommendation="Inspect package")
        ]
        out_frame = annotator.annotate(frame, tracks, events, assessments)
        assert out_frame is not None
        assert out_frame.shape == frame.shape


class TestVideoPipeline:
    """Tests for full vision pipeline integration."""

    def test_pipeline_initialization(self):
        """Test pipeline initialization with configs."""
        from backend.vision.pipeline import VideoPipeline
        pipeline = VideoPipeline()
        assert pipeline.detector is not None
        assert pipeline.tracker is not None
        assert pipeline.behaviour is not None
        assert pipeline.risk is not None
        assert pipeline.annotator is not None

    def test_pipeline_process_frame(self):
        """Test pipeline frame processing."""
        from backend.vision.pipeline import VideoPipeline
        pipeline = VideoPipeline()
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        result = pipeline.process_frame(frame, frame_idx=0)
        assert result.frame_idx == 0
        assert result.annotated_frame is not None



# ============================================================
# Test Risk Scoring
# ============================================================

class TestRiskEngine:
    """Tests for risk scoring."""

    def test_risk_engine_initialization(self):
        """Test risk engine loads config."""
        try:
            from backend.risk.risk_engine import RiskEngine
            engine = RiskEngine()
            assert engine is not None
        except ImportError:
            pytest.skip("Risk module not yet available")

    def test_risk_levels(self):
        """Test risk level classification."""
        try:
            from backend.risk.risk_engine import RiskEngine
            engine = RiskEngine()
            
            # Product drop should be HIGH risk
            assessment = engine.assess_risk(
                event_type="product_drop",
                evidence={"drop_height_px": 120, "velocity": 4.2},
            )
            
            assert assessment is not None
            assert assessment.level in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
            assert 0 <= assessment.score <= 100
        except ImportError:
            pytest.skip("Risk module not yet available")

    def test_critical_risk_threshold(self):
        """Test that severe events get CRITICAL rating."""
        try:
            from backend.risk.risk_engine import RiskEngine
            engine = RiskEngine()
            
            # Thrown product with high velocity should be critical
            assessment = engine.assess_risk(
                event_type="product_throwing",
                evidence={"velocity": 8.0, "height": 150},
                modifiers={"repeat_offence": "third_plus", "product_type": "fragile"},
            )
            
            assert assessment.level in ["HIGH", "CRITICAL"]
        except ImportError:
            pytest.skip("Risk module not yet available")

    def test_risk_explanation_present(self):
        """Test that risk assessment includes explanation."""
        try:
            from backend.risk.risk_engine import RiskEngine
            engine = RiskEngine()
            
            assessment = engine.assess_risk(
                event_type="product_drop",
                evidence={"drop_height_px": 100},
            )
            
            assert assessment.explanation is not None
            assert len(assessment.explanation) > 0
            # Should NOT claim definite damage
            assert "definitely damaged" not in assessment.explanation.lower()
        except ImportError:
            pytest.skip("Risk module not yet available")


# ============================================================
# Test Config Loading
# ============================================================

class TestConfig:
    """Tests for configuration loading."""

    def test_detection_config_loads(self):
        """Test detection config loads."""
        import yaml
        from pathlib import Path
        
        config_path = Path("configs/detection.yaml")
        if config_path.exists():
            with open(config_path) as f:
                config = yaml.safe_load(f)
            assert "model" in config
            assert "confidence_threshold" in config["model"]
        else:
            pytest.skip("Config not found - not in project root")

    def test_behaviour_config_loads(self):
        """Test behaviour config loads."""
        import yaml
        from pathlib import Path
        
        config_path = Path("configs/behaviour.yaml")
        if config_path.exists():
            with open(config_path) as f:
                config = yaml.safe_load(f)
            assert "behaviours" in config
            assert "product_drop" in config["behaviours"]
        else:
            pytest.skip("Config not found")

    def test_risk_config_loads(self):
        """Test risk config loads."""
        import yaml
        from pathlib import Path
        
        config_path = Path("configs/risk.yaml")
        if config_path.exists():
            with open(config_path) as f:
                config = yaml.safe_load(f)
            assert "levels" in config
            assert "base_scores" in config
        else:
            pytest.skip("Config not found")
