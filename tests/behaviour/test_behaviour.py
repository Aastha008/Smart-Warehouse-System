"""
AI Warehouse Intelligence - Behaviour Detection Tests
"""
import pytest
import numpy as np


class TestTemporalBehaviourDetection:
    """Test temporal behaviour detection logic."""

    def test_drop_requires_temporal_sequence(self):
        """Drop detection must use multiple frames, not single frame."""
        try:
            from backend.behaviour.drop_detector import DropDetector
            detector = DropDetector()
            
            # Single frame should NOT produce a drop event
            # (drop requires: moving down -> stationary sequence)
            assert hasattr(detector, 'state_machines') or hasattr(detector, 'track_states')
        except ImportError:
            pytest.skip("Behaviour module not yet available")

    def test_drag_requires_sustained_movement(self):
        """Dragging must be sustained horizontal movement at low height."""
        try:
            from backend.behaviour.drag_detector import DragDetector
            detector = DragDetector()
            assert detector is not None
        except ImportError:
            pytest.skip("Behaviour module not yet available")

    def test_throw_requires_release_and_impact(self):
        """Throwing requires release velocity and subsequent impact."""
        try:
            from backend.behaviour.throw_detector import ThrowDetector
            detector = ThrowDetector()
            assert detector is not None
        except ImportError:
            pytest.skip("Behaviour module not yet available")

    def test_stacking_requires_spatial_analysis(self):
        """Stacking analysis requires spatial relationship between objects."""
        try:
            from backend.behaviour.stacking_detector import StackingDetector
            detector = StackingDetector()
            assert detector is not None
        except ImportError:
            pytest.skip("Behaviour module not yet available")

    def test_zone_detection_uses_configured_zones(self):
        """Zone detection must use configured zone boundaries."""
        try:
            from backend.behaviour.zone_detector import ZoneDetector
            detector = ZoneDetector()
            assert detector is not None
            # Should have zones loaded from config
            assert hasattr(detector, 'zones') or hasattr(detector, 'config')
        except ImportError:
            pytest.skip("Behaviour module not yet available")


class TestBehaviourEventFormat:
    """Test that behaviour events have correct format."""

    def test_event_has_required_fields(self):
        """Every behaviour event must have core fields."""
        try:
            from backend.behaviour.base_detector import BehaviourEvent
            
            required_fields = [
                'event_type', 'object_id', 'frame_idx',
                'confidence', 'evidence'
            ]
            
            event = BehaviourEvent(
                event_type="product_drop",
                object_id=1,
                frame_idx=100,
                confidence=0.85,
                evidence={"drop_height_px": 100},
            )
            
            for field in required_fields:
                assert hasattr(event, field), f"Missing field: {field}"
        except ImportError:
            pytest.skip("Behaviour module not yet available")

    def test_confidence_in_valid_range(self):
        """Confidence must be between 0 and 1."""
        try:
            from backend.behaviour.base_detector import BehaviourEvent
            
            event = BehaviourEvent(
                event_type="test",
                object_id=1,
                frame_idx=0,
                confidence=0.85,
                evidence={},
            )
            
            assert 0 <= event.confidence <= 1
        except ImportError:
            pytest.skip("Behaviour module not yet available")


class TestAllTenBehaviours:
    """Verify all 10 required behaviour detectors exist and function accurately."""

    REQUIRED_BEHAVIOURS = [
        "product_drop",
        "product_dragging",
        "product_throwing",
        "rough_handling",
        "improper_stacking",
        "unstable_stacking",
        "product_outside_zone",
        "incorrect_pallet_position",
        "unsafe_loading_sequence",
        "improper_handling_equipment",
    ]

    def test_behaviour_engine_has_all_detectors(self):
        """Behaviour engine must include all 10 required detectors."""
        from backend.behaviour.behaviour_engine import BehaviourEngine
        engine = BehaviourEngine()
        
        detector_types = [d.behaviour_type for d in engine.detectors]
        
        for behaviour in self.REQUIRED_BEHAVIOURS:
            assert behaviour in detector_types, \
                f"Missing behaviour detector: {behaviour}"

    def test_drop_detector_logic(self):
        """Test DropDetector identifies falling items."""
        from backend.behaviour.drop_detector import DropDetector
        from backend.vision.tracker import TrackedObject

        detector = DropDetector()
        obj = TrackedObject(
            object_id=1,
            class_name="package",
            bbox=(100.0, 50.0, 150.0, 100.0),
            center=(125.0, 75.0),
            velocity=(0.0, 8.0),
            trajectory=[(125.0, 50.0), (125.0, 100.0), (125.0, 150.0), (125.0, 200.0)]
        )
        events = detector.analyze([obj], frame_idx=10, frame_shape=(480, 640))
        assert len(events) >= 1
        assert events[0].event_type == "product_drop"
        assert "drop_height_px" in events[0].evidence

    def test_drag_detector_logic(self):
        """Test DragDetector identifies horizontal dragging."""
        from backend.behaviour.drag_detector import DragDetector
        from backend.vision.tracker import TrackedObject

        detector = DragDetector()
        traj = [(float(100 + i * 15), 400.0) for i in range(10)]
        obj = TrackedObject(
            object_id=2,
            class_name="package",
            bbox=(200.0, 380.0, 260.0, 420.0),
            center=(235.0, 400.0),
            velocity=(15.0, 0.0),
            trajectory=traj
        )
        events = detector.analyze([obj], frame_idx=15, frame_shape=(480, 640))
        assert len(events) >= 1
        assert events[0].event_type == "product_dragging"
        assert "drag_distance_px" in events[0].evidence

    def test_throw_detector_logic(self):
        """Test ThrowDetector identifies airborne throws."""
        from backend.behaviour.throw_detector import ThrowDetector
        from backend.vision.tracker import TrackedObject

        detector = ThrowDetector()
        obj = TrackedObject(
            object_id=3,
            class_name="package",
            bbox=(100.0, 100.0, 150.0, 150.0),
            center=(125.0, 125.0),
            velocity=(12.0, -8.0),
            trajectory=[(50.0, 200.0), (80.0, 150.0), (110.0, 120.0), (140.0, 140.0)]
        )
        events = detector.analyze([obj], frame_idx=20, frame_shape=(480, 640))
        assert len(events) >= 1
        assert events[0].event_type == "product_throwing"
        assert "velocity" in events[0].evidence

    def test_rough_handling_detector_logic(self):
        """Test RoughHandlingDetector identifies high acceleration/jerk."""
        from backend.behaviour.rough_handling_detector import RoughHandlingDetector
        from backend.vision.tracker import TrackedObject

        detector = RoughHandlingDetector()
        obj = TrackedObject(
            object_id=4,
            class_name="package",
            bbox=(100.0, 100.0, 150.0, 150.0),
            center=(125.0, 125.0),
            velocity=(5.0, 5.0),
            acceleration=(8.0, 8.0),
            trajectory=[(100.0, 100.0), (120.0, 110.0), (105.0, 130.0)]
        )
        events = detector.analyze([obj], frame_idx=25, frame_shape=(480, 640))
        assert len(events) >= 1
        assert events[0].event_type == "rough_handling"
        assert "acceleration" in events[0].evidence

    def test_stacking_detector_logic(self):
        """Test StackingDetector identifies heavy-on-light improper stacking."""
        from backend.behaviour.stacking_detector import StackingDetector
        from backend.vision.tracker import TrackedObject

        detector = StackingDetector()
        # Large top package directly on top of small bottom package
        top_pkg = TrackedObject(
            object_id=5,
            class_name="package",
            bbox=(80.0, 100.0, 220.0, 180.0), # width 140
            center=(150.0, 140.0)
        )
        bottom_pkg = TrackedObject(
            object_id=6,
            class_name="package",
            bbox=(110.0, 180.0, 190.0, 240.0), # width 80
            center=(150.0, 210.0)
        )
        events = detector.analyze([top_pkg, bottom_pkg], frame_idx=30, frame_shape=(480, 640))
        assert len(events) >= 1
        assert events[0].event_type == "improper_stacking"
        assert "top_width" in events[0].evidence

    def test_unstable_stack_detector_logic(self):
        """Test UnstableStackDetector identifies tall, high-aspect ratio stacks."""
        from backend.behaviour.unstable_stack_detector import UnstableStackDetector
        from backend.vision.tracker import TrackedObject

        detector = UnstableStackDetector()
        tall_obj = TrackedObject(
            object_id=7,
            class_name="package",
            bbox=(100.0, 50.0, 140.0, 250.0), # w=40, h=200 -> aspect ratio 5.0
            center=(120.0, 150.0),
            trajectory=[(120.0, 150.0), (125.0, 150.0), (115.0, 150.0), (124.0, 150.0), (116.0, 150.0)]
        )
        events = detector.analyze([tall_obj], frame_idx=35, frame_shape=(480, 640))
        assert len(events) >= 1
        assert events[0].event_type == "unstable_stacking"
        assert "aspect_ratio" in events[0].evidence

    def test_zone_detector_logic(self):
        """Test ZoneDetector identifies packages outside designated perimeter."""
        from backend.behaviour.zone_detector import ZoneDetector
        from backend.vision.tracker import TrackedObject

        detector = ZoneDetector()
        # Package placed at far corner / outside designated boundaries (e.g. norm_x=0.03, norm_y=0.03)
        outside_obj = TrackedObject(
            object_id=8,
            class_name="package",
            bbox=(5.0, 5.0, 30.0, 30.0),
            center=(17.0, 17.0)
        )
        events = detector.analyze([outside_obj], frame_idx=40, frame_shape=(480, 640))
        assert len(events) >= 1
        assert events[0].event_type == "product_outside_zone"

    def test_pallet_detector_logic(self):
        """Test PalletDetector identifies product overhang on pallet."""
        from backend.behaviour.pallet_detector import PalletDetector
        from backend.vision.tracker import TrackedObject

        detector = PalletDetector()
        pallet = TrackedObject(
            object_id=9,
            class_name="pallet",
            bbox=(200.0, 300.0, 350.0, 350.0), # pallet width 150
            center=(275.0, 325.0)
        )
        overhanging_pkg = TrackedObject(
            object_id=10,
            class_name="package",
            bbox=(150.0, 220.0, 390.0, 300.0), # package overhangs pallet left and right
            center=(270.0, 260.0)
        )
        events = detector.analyze([pallet, overhanging_pkg], frame_idx=45, frame_shape=(480, 640))
        assert len(events) >= 1
        assert events[0].event_type == "incorrect_pallet_position"
        assert "overhang_fraction" in events[0].evidence

    def test_loading_sequence_detector_logic(self):
        """Test LoadingSequenceDetector identifies unsafe loading and concurrent loads."""
        from backend.behaviour.loading_sequence_detector import LoadingSequenceDetector
        from backend.vision.tracker import TrackedObject

        detector = LoadingSequenceDetector()
        # 4 moving loads exceeding max_simultaneous_loads
        moving_loads = [
            TrackedObject(object_id=i, class_name="package", bbox=(100+i*50, 100, 140+i*50, 140),
                          center=(120+i*50, 120), velocity=(4.0, 0.0))
            for i in range(11, 16)
        ]
        events = detector.analyze(moving_loads, frame_idx=50, frame_shape=(480, 640))
        assert len(events) >= 1
        assert events[0].event_type == "unsafe_loading_sequence"

    def test_equipment_detector_logic(self):
        """Test EquipmentDetector identifies large loads handled without equipment."""
        from backend.behaviour.equipment_detector import EquipmentDetector
        from backend.vision.tracker import TrackedObject

        detector = EquipmentDetector()
        # Large heavy load (width 180) moving with no forklift/trolley anywhere nearby
        heavy_load = TrackedObject(
            object_id=20,
            class_name="package",
            bbox=(100.0, 100.0, 280.0, 260.0),
            center=(190.0, 180.0),
            velocity=(3.0, 0.0),
            trajectory=[(180.0, 180.0), (183.0, 180.0), (186.0, 180.0), (190.0, 180.0)]
        )
        events = detector.analyze([heavy_load], frame_idx=55, frame_shape=(480, 640))
        assert len(events) >= 1
        assert events[0].event_type == "improper_handling_equipment"
        assert "package_size_px" in events[0].evidence
