"""
AI Warehouse Intelligence - Comprehensive Empirical Adversarial Challenge Suite (Milestone 1)
Validates CV Pipeline, ObjectTracker, MotionAnalyzer, and all 10 Behaviour Detectors under
exhaustive multi-frame trajectories, boundary values, geometric edge cases, and stress conditions.
"""
import math
import time
import numpy as np
import pytest
from datetime import datetime
from typing import List, Tuple, Dict, Any

from backend.vision.detector import Detection, WarehouseDetector
from backend.vision.tracker import ObjectTracker, TrackedObject
from backend.vision.motion import MotionAnalyzer
from backend.vision.annotator import Annotator
from backend.vision.pipeline import VideoPipeline
from backend.behaviour.base_detector import BehaviourEvent
from backend.behaviour.behaviour_engine import BehaviourEngine
from backend.behaviour.drop_detector import DropDetector
from backend.behaviour.drag_detector import DragDetector
from backend.behaviour.throw_detector import ThrowDetector
from backend.behaviour.rough_handling_detector import RoughHandlingDetector
from backend.behaviour.stacking_detector import StackingDetector
from backend.behaviour.unstable_stack_detector import UnstableStackDetector
from backend.behaviour.zone_detector import ZoneDetector
from backend.behaviour.pallet_detector import PalletDetector
from backend.behaviour.loading_sequence_detector import LoadingSequenceDetector
from backend.behaviour.equipment_detector import EquipmentDetector


VALID_BEHAVIOUR_TYPES = {
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
}


def validate_behaviour_event_schema(event: BehaviourEvent):
    """Rigorous schema validation for BehaviourEvent."""
    assert isinstance(event, BehaviourEvent), f"Expected BehaviourEvent, got {type(event)}"
    assert isinstance(event.event_type, str) and event.event_type in VALID_BEHAVIOUR_TYPES, (
        f"Invalid event_type: {event.event_type}"
    )
    assert isinstance(event.object_id, int), f"object_id must be int, got {type(event.object_id)}"
    assert isinstance(event.frame_idx, int) and event.frame_idx >= 0, (
        f"frame_idx must be non-negative int, got {event.frame_idx}"
    )
    assert isinstance(event.confidence, (float, int)), f"confidence must be float, got {type(event.confidence)}"
    assert 0.0 <= event.confidence <= 1.0, f"confidence must be in [0.0, 1.0], got {event.confidence}"
    assert not math.isnan(event.confidence) and not math.isinf(event.confidence), "confidence cannot be NaN/Inf"
    assert isinstance(event.timestamp, str) and len(event.timestamp) > 0, "timestamp must be non-empty string"
    assert isinstance(event.location, str) and len(event.location) > 0, "location must be non-empty string"
    assert isinstance(event.evidence, dict), f"evidence must be dict, got {type(event.evidence)}"
    
    # Evidence values must not contain NaN or Inf
    for k, v in event.evidence.items():
        if isinstance(v, float):
            assert not math.isnan(v) and not math.isinf(v), f"Evidence key '{k}' contains NaN or Inf: {v}"


class TestDetector1ProductDrop:
    """Empirical verification of DropDetector."""

    def test_drop_positive_free_fall_and_impact(self):
        detector = DropDetector()
        events = []
        traj = [(200.0, 100.0)]
        for f in range(1, 10):
            y = 100.0 + f * 20.0 # drops 180px
            traj.append((200.0, y))
            obj = TrackedObject(
                object_id=1, class_name="package",
                bbox=(180.0, y - 20.0, 220.0, y + 20.0),
                center=(200.0, y),
                velocity=(0.0, 20.0 if f < 8 else 0.0),
                trajectory=list(traj)
            )
            events.extend(detector.analyze([obj], frame_idx=f, frame_shape=(720, 1280)))
            
        assert len(events) >= 1
        assert events[0].event_type == "product_drop"
        assert events[0].evidence["drop_height_px"] >= 40.0
        validate_behaviour_event_schema(events[0])

    def test_drop_negative_upward_movement(self):
        """Moving upwards (lifted from floor to shelf) should NOT trigger drop."""
        detector = DropDetector()
        events = []
        traj = [(200.0, 500.0)]
        for f in range(1, 10):
            y = 500.0 - f * 20.0 # lifts 180px up
            traj.append((200.0, y))
            obj = TrackedObject(
                object_id=2, class_name="package",
                bbox=(180.0, y - 20.0, 220.0, y + 20.0),
                center=(200.0, y),
                velocity=(0.0, -20.0),
                trajectory=list(traj)
            )
            events.extend(detector.analyze([obj], frame_idx=f, frame_shape=(720, 1280)))
        assert len(events) == 0, "Lifting upward should not trigger drop event"


class TestDetector2ProductDragging:
    """Empirical verification of DragDetector."""

    def test_drag_positive_horizontal_sliding(self):
        detector = DragDetector()
        events = []
        traj = []
        for f in range(12):
            x = 100.0 + f * 10.0 # 110px horizontal movement
            y = 400.0
            traj.append((x, y))
            obj = TrackedObject(
                object_id=3, class_name="package",
                bbox=(x - 25.0, y - 20.0, x + 25.0, y + 20.0),
                center=(x, y),
                velocity=(10.0, 0.0),
                trajectory=list(traj)
            )
            events.extend(detector.analyze([obj], frame_idx=f, frame_shape=(720, 1280)))
            
        assert len(events) >= 1
        assert events[0].event_type == "product_dragging"
        assert events[0].evidence["drag_distance_px"] >= 30.0
        validate_behaviour_event_schema(events[0])

    def test_drag_negative_vertical_carry(self):
        """High vertical lift while walking should NOT trigger drag."""
        detector = DragDetector()
        events = []
        traj = []
        for f in range(12):
            x = 100.0 + f * 10.0
            y = 400.0 - f * 15.0 # substantial vertical lift (165px)
            traj.append((x, y))
            obj = TrackedObject(
                object_id=4, class_name="package",
                bbox=(x - 25.0, y - 20.0, x + 25.0, y + 20.0),
                center=(x, y),
                velocity=(10.0, -15.0),
                trajectory=list(traj)
            )
            events.extend(detector.analyze([obj], frame_idx=f, frame_shape=(720, 1280)))
        assert len(events) == 0, "Carrying with lift must not trigger dragging"


class TestDetector3ProductThrowing:
    """Empirical verification of ThrowDetector."""

    def test_throw_positive_high_release_velocity(self):
        detector = ThrowDetector()
        obj = TrackedObject(
            object_id=5, class_name="carton",
            bbox=(100.0, 100.0, 150.0, 150.0),
            center=(125.0, 125.0),
            velocity=(15.0, -6.0),
            trajectory=[(60.0, 150.0), (80.0, 130.0), (100.0, 120.0), (125.0, 125.0)]
        )
        events = detector.analyze([obj], frame_idx=1, frame_shape=(720, 1280))
        assert len(events) >= 1
        assert events[0].event_type == "product_throwing"
        assert events[0].evidence["velocity"] >= 5.0
        validate_behaviour_event_schema(events[0])

    def test_throw_negative_slow_movement(self):
        detector = ThrowDetector()
        obj = TrackedObject(
            object_id=6, class_name="carton",
            bbox=(100.0, 100.0, 150.0, 150.0),
            center=(125.0, 125.0),
            velocity=(1.0, 0.5),
            trajectory=[(120.0, 123.0), (125.0, 125.0)]
        )
        events = detector.analyze([obj], frame_idx=1, frame_shape=(720, 1280))
        assert len(events) == 0


class TestDetector4RoughHandling:
    """Empirical verification of RoughHandlingDetector."""

    def test_rough_positive_high_acceleration(self):
        detector = RoughHandlingDetector()
        obj = TrackedObject(
            object_id=7, class_name="package",
            bbox=(100.0, 100.0, 150.0, 150.0),
            center=(125.0, 125.0),
            velocity=(10.0, 10.0),
            acceleration=(8.0, 6.0),
            trajectory=[(100.0, 100.0), (115.0, 110.0), (105.0, 125.0)]
        )
        events = detector.analyze([obj], frame_idx=1, frame_shape=(720, 1280))
        assert len(events) >= 1
        assert events[0].event_type == "rough_handling"
        assert events[0].evidence["acceleration"] >= 3.0
        validate_behaviour_event_schema(events[0])

    def test_rough_negative_smooth_linear_motion(self):
        detector = RoughHandlingDetector()
        obj = TrackedObject(
            object_id=8, class_name="package",
            bbox=(100.0, 100.0, 150.0, 150.0),
            center=(125.0, 125.0),
            velocity=(3.0, 0.0),
            acceleration=(0.0, 0.0),
            trajectory=[(100.0, 125.0), (110.0, 125.0), (120.0, 125.0), (125.0, 125.0)]
        )
        events = detector.analyze([obj], frame_idx=1, frame_shape=(720, 1280))
        assert len(events) == 0


class TestDetector5ImproperStacking:
    """Empirical verification of StackingDetector."""

    def test_stacking_positive_heavy_on_light(self):
        detector = StackingDetector()
        top = TrackedObject(
            object_id=9, class_name="package",
            bbox=(100.0, 100.0, 260.0, 180.0), # width 160
            center=(180.0, 140.0)
        )
        bottom = TrackedObject(
            object_id=10, class_name="package",
            bbox=(130.0, 180.0, 210.0, 240.0), # width 80
            center=(170.0, 210.0)
        )
        events = detector.analyze([top, bottom], frame_idx=1, frame_shape=(720, 1280))
        assert len(events) >= 1
        assert events[0].event_type == "improper_stacking"
        assert events[0].evidence["size_ratio"] >= 1.2
        validate_behaviour_event_schema(events[0])

    def test_stacking_negative_small_on_large(self):
        detector = StackingDetector()
        top = TrackedObject(
            object_id=11, class_name="package",
            bbox=(130.0, 100.0, 210.0, 160.0), # width 80
            center=(170.0, 130.0)
        )
        bottom = TrackedObject(
            object_id=12, class_name="package",
            bbox=(100.0, 160.0, 260.0, 240.0), # width 160
            center=(180.0, 200.0)
        )
        events = detector.analyze([top, bottom], frame_idx=1, frame_shape=(720, 1280))
        assert len(events) == 0, "Proper stacking (small on large) must not trigger improper_stacking"


class TestDetector6UnstableStacking:
    """Empirical verification of UnstableStackDetector."""

    def test_unstable_positive_high_aspect_ratio_and_wobble(self):
        detector = UnstableStackDetector()
        tall_obj = TrackedObject(
            object_id=13, class_name="package",
            bbox=(100.0, 50.0, 140.0, 250.0), # w=40, h=200 -> aspect 5.0
            center=(120.0, 150.0),
            trajectory=[(115.0, 150.0), (125.0, 150.0), (116.0, 150.0), (124.0, 150.0), (120.0, 150.0)]
        )
        events = detector.analyze([tall_obj], frame_idx=1, frame_shape=(720, 1280))
        assert len(events) >= 1
        assert events[0].event_type == "unstable_stacking"
        assert events[0].evidence["aspect_ratio"] >= 2.4
        validate_behaviour_event_schema(events[0])

    def test_unstable_negative_standard_low_aspect_box(self):
        detector = UnstableStackDetector()
        stable_obj = TrackedObject(
            object_id=14, class_name="package",
            bbox=(100.0, 100.0, 200.0, 180.0), # w=100, h=80 -> aspect 0.8
            center=(150.0, 140.0),
            trajectory=[(150.0, 140.0)] * 5
        )
        events = detector.analyze([stable_obj], frame_idx=1, frame_shape=(720, 1280))
        assert len(events) == 0


class TestDetector7ProductOutsideZone:
    """Empirical verification of ZoneDetector."""

    def test_zone_positive_perimeter_violation(self):
        detector = ZoneDetector()
        outside_obj = TrackedObject(
            object_id=15, class_name="package",
            bbox=(10.0, 10.0, 40.0, 40.0),
            center=(25.0, 25.0) # norm_x = 25/1280 = 0.019 (< 0.08)
        )
        events = detector.analyze([outside_obj], frame_idx=1, frame_shape=(720, 1280))
        assert len(events) >= 1
        assert events[0].event_type == "product_outside_zone"
        validate_behaviour_event_schema(events[0])

    def test_zone_negative_inside_center_bay(self):
        detector = ZoneDetector()
        inside_obj = TrackedObject(
            object_id=16, class_name="package",
            bbox=(500.0, 300.0, 600.0, 400.0),
            center=(550.0, 350.0) # perfectly centered
        )
        events = detector.analyze([inside_obj], frame_idx=1, frame_shape=(720, 1280))
        assert len(events) == 0


class TestDetector8IncorrectPalletPosition:
    """Empirical verification of PalletDetector."""

    def test_pallet_positive_overhang(self):
        detector = PalletDetector()
        pallet = TrackedObject(
            object_id=17, class_name="pallet",
            bbox=(200.0, 300.0, 350.0, 350.0), # width 150
            center=(275.0, 325.0)
        )
        pkg = TrackedObject(
            object_id=18, class_name="package",
            bbox=(150.0, 230.0, 400.0, 305.0), # overhangs both sides (width 250)
            center=(275.0, 267.5)
        )
        events = detector.analyze([pallet, pkg], frame_idx=1, frame_shape=(720, 1280))
        assert len(events) >= 1
        assert events[0].event_type == "incorrect_pallet_position"
        assert events[0].evidence["issue"] == "product_overhang"
        validate_behaviour_event_schema(events[0])

    def test_pallet_negative_centered_load(self):
        detector = PalletDetector()
        pallet = TrackedObject(
            object_id=19, class_name="pallet",
            bbox=(200.0, 300.0, 400.0, 360.0), # width 200
            center=(300.0, 330.0)
        )
        pkg = TrackedObject(
            object_id=20, class_name="package",
            bbox=(220.0, 240.0, 380.0, 305.0), # width 160 (fits nicely inside pallet)
            center=(300.0, 272.5)
        )
        events = detector.analyze([pallet, pkg], frame_idx=1, frame_shape=(720, 1280))
        overhang_evs = [e for e in events if e.evidence.get("issue") == "product_overhang"]
        assert len(overhang_evs) == 0


class TestDetector9UnsafeLoadingSequence:
    """Empirical verification of LoadingSequenceDetector."""

    def test_sequence_positive_multiple_simultaneous_loads(self):
        detector = LoadingSequenceDetector()
        moving_loads = [
            TrackedObject(object_id=100 + i, class_name="package",
                          bbox=(100 + i * 80, 200, 150 + i * 80, 250),
                          center=(125 + i * 80, 225),
                          velocity=(4.0, 1.0))
            for i in range(5) # 5 moving simultaneously > max 3
        ]
        events = detector.analyze(moving_loads, frame_idx=1, frame_shape=(720, 1280))
        assert len(events) >= 1
        assert any(e.evidence.get("issue") == "excessive_simultaneous_loads" for e in events)
        for ev in events:
            validate_behaviour_event_schema(ev)

    def test_sequence_positive_insufficient_clearance(self):
        detector = LoadingSequenceDetector()
        o1 = TrackedObject(object_id=110, class_name="package", bbox=(100, 100, 140, 140),
                           center=(120, 120), velocity=(3.0, 0.0))
        o2 = TrackedObject(object_id=111, class_name="package", bbox=(115, 100, 155, 140),
                           center=(135, 120), velocity=(3.0, 0.0)) # dist = 15px < min 30px
        events = detector.analyze([o1, o2], frame_idx=1, frame_shape=(720, 1280))
        assert any(e.evidence.get("issue") == "insufficient_load_clearance" for e in events)


class TestDetector10ImproperHandlingEquipment:
    """Empirical verification of EquipmentDetector."""

    def test_equipment_positive_oversized_load_manual_movement(self):
        detector = EquipmentDetector()
        heavy_load = TrackedObject(
            object_id=120, class_name="package",
            bbox=(100.0, 100.0, 280.0, 280.0), # size 180px > 130px
            center=(190.0, 190.0),
            velocity=(3.0, 0.0),
            trajectory=[(180.0, 190.0), (185.0, 190.0), (190.0, 190.0), (195.0, 190.0)]
        )
        events = detector.analyze([heavy_load], frame_idx=1, frame_shape=(720, 1280))
        assert len(events) >= 1
        assert events[0].event_type == "improper_handling_equipment"
        assert events[0].evidence["issue"] == "heavy_load_handled_without_equipment"
        validate_behaviour_event_schema(events[0])

    def test_equipment_positive_vehicle_pedestrian_hazard(self):
        detector = EquipmentDetector()
        forklift = TrackedObject(
            object_id=121, class_name="forklift",
            bbox=(200.0, 200.0, 350.0, 350.0),
            center=(275.0, 275.0),
            velocity=(4.0, 0.0)
        )
        pedestrian = TrackedObject(
            object_id=122, class_name="person",
            bbox=(300.0, 260.0, 340.0, 340.0),
            center=(320.0, 300.0) # dist = 51.4px < 60px
        )
        events = detector.analyze([forklift, pedestrian], frame_idx=1, frame_shape=(720, 1280))
        assert len(events) >= 1
        assert any(e.evidence.get("issue") == "equipment_pedestrian_hazard" for e in events)


class TestBoundaryAndExtremeValues:
    """Stress test extreme numerical inputs, negative coords, zero velocities, and high speeds."""

    def test_zero_velocity_and_acceleration(self):
        engine = BehaviourEngine()
        obj = TrackedObject(
            object_id=201, class_name="package",
            bbox=(300.0, 300.0, 360.0, 360.0),
            center=(330.0, 330.0),
            velocity=(0.0, 0.0),
            acceleration=(0.0, 0.0),
            trajectory=[(330.0, 330.0)] * 10
        )
        events = engine.analyze([obj], frame_idx=1, frame_shape=(720, 1280))
        triggered = {e.event_type for e in events}
        assert "product_drop" not in triggered
        assert "product_dragging" not in triggered
        assert "product_throwing" not in triggered
        assert "rough_handling" not in triggered

    def test_hyper_velocity_and_acceleration(self):
        engine = BehaviourEngine()
        obj = TrackedObject(
            object_id=202, class_name="package",
            bbox=(100.0, 100.0, 160.0, 160.0),
            center=(130.0, 130.0),
            velocity=(1_000_000.0, 1_000_000.0),
            acceleration=(500_000.0, 500_000.0),
            trajectory=[(100.0, 100.0), (130.0, 130.0)]
        )
        events = engine.analyze([obj], frame_idx=1, frame_shape=(720, 1280))
        for ev in events:
            validate_behaviour_event_schema(ev)
            assert ev.confidence <= 1.0

    def test_negative_coordinates_and_offscreen(self):
        engine = BehaviourEngine()
        obj = TrackedObject(
            object_id=203, class_name="package",
            bbox=(-150.0, -150.0, -50.0, -50.0),
            center=(-100.0, -100.0),
            velocity=(-10.0, -10.0),
            trajectory=[(-100.0, -100.0)]
        )
        events = engine.analyze([obj], frame_idx=1, frame_shape=(720, 1280))
        assert any(e.event_type == "product_outside_zone" for e in events)
        for ev in events:
            validate_behaviour_event_schema(ev)

    def test_subnormal_floating_point_velocities(self):
        engine = BehaviourEngine()
        obj = TrackedObject(
            object_id=204, class_name="package",
            bbox=(200.0, 200.0, 250.0, 250.0),
            center=(225.0, 225.0),
            velocity=(1e-18, -1e-18),
            acceleration=(1e-20, 1e-20),
            trajectory=[(225.0, 225.0), (225.0 + 1e-18, 225.0 - 1e-18)]
        )
        events = engine.analyze([obj], frame_idx=1, frame_shape=(720, 1280))
        for ev in events:
            validate_behaviour_event_schema(ev)


class TestUnusualBoundingBoxesAndGeometries:
    """Stress test zero-area boxes, inverted coordinates, and extreme aspect ratios."""

    def test_zero_area_bounding_box(self):
        engine = BehaviourEngine()
        obj = TrackedObject(
            object_id=301, class_name="package",
            bbox=(100.0, 100.0, 100.0, 100.0),
            center=(100.0, 100.0),
            velocity=(0.0, 0.0)
        )
        events = engine.analyze([obj], frame_idx=1, frame_shape=(720, 1280))
        for ev in events:
            validate_behaviour_event_schema(ev)

    def test_inverted_bounding_box_coordinates(self):
        engine = BehaviourEngine()
        obj = TrackedObject(
            object_id=302, class_name="package",
            bbox=(300.0, 300.0, 100.0, 100.0),
            center=(200.0, 200.0),
            velocity=(0.0, 0.0)
        )
        events = engine.analyze([obj], frame_idx=1, frame_shape=(720, 1280))
        for ev in events:
            validate_behaviour_event_schema(ev)

    def test_extreme_aspect_ratios_tall_tower(self):
        detector = UnstableStackDetector()
        obj = TrackedObject(
            object_id=303, class_name="package",
            bbox=(200.0, 50.0, 210.0, 250.0), # w=10, h=200
            center=(205.0, 150.0),
            trajectory=[(205.0, 150.0)]
        )
        events = detector.analyze([obj], frame_idx=1, frame_shape=(720, 1280))
        assert len(events) >= 1
        assert events[0].event_type == "unstable_stacking"
        assert events[0].evidence["aspect_ratio"] >= 10.0
        validate_behaviour_event_schema(events[0])

    def test_extreme_aspect_ratios_flat_sheet(self):
        detector = UnstableStackDetector()
        obj = TrackedObject(
            object_id=304, class_name="package",
            bbox=(100.0, 300.0, 600.0, 305.0), # w=500, h=5
            center=(350.0, 302.5),
            trajectory=[(350.0, 302.5)]
        )
        events = detector.analyze([obj], frame_idx=1, frame_shape=(720, 1280))
        assert len(events) == 0


class TestOverlappingAndCrowdedScenes:
    """Stress test dense overlapping bounding boxes and high track counts."""

    def test_hundred_co_located_objects(self):
        engine = BehaviourEngine()
        objects = [
            TrackedObject(
                object_id=i, class_name="package",
                bbox=(200.0, 200.0, 250.0, 250.0),
                center=(225.0, 225.0),
                velocity=(0.0, 0.0)
            )
            for i in range(1, 101)
        ]
        events = engine.analyze(objects, frame_idx=1, frame_shape=(720, 1280))
        for ev in events:
            validate_behaviour_event_schema(ev)

    def test_massively_crowded_frame_throughput(self):
        engine = BehaviourEngine()
        objects = []
        for i in range(300):
            cls = "package" if i % 2 == 0 else ("pallet" if i % 5 == 0 else "person")
            objects.append(TrackedObject(
                object_id=i + 1,
                class_name=cls,
                bbox=(float((i * 10) % 1000), float((i * 8) % 600), float((i * 10) % 1000 + 40), float((i * 8) % 600 + 40)),
                center=(float((i * 10) % 1000 + 20), float((i * 8) % 600 + 20)),
                velocity=(float(i % 5), float(i % 3)),
                trajectory=[(float((i * 10) % 1000 + 20), float((i * 8) % 600 + 20))] * 4
            ))

        start_time = time.perf_counter()
        events = engine.analyze(objects, frame_idx=10, frame_shape=(720, 1280))
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        # Performance constraint: 300 tracks must process in under 200ms
        assert elapsed_ms < 200.0, f"Engine processing too slow for 300 tracks: {elapsed_ms:.1f}ms"
        for ev in events:
            validate_behaviour_event_schema(ev)


class TestStateManagementAndMemoryLeaks:
    """Stress test track lifecycle, cleanup of stale states, and tracker ID churn."""

    def test_drop_detector_stale_track_cleanup(self):
        detector = DropDetector()
        
        # Frame 1: Object 501 appears
        obj = TrackedObject(
            object_id=501, class_name="package",
            bbox=(100.0, 100.0, 150.0, 150.0),
            center=(125.0, 125.0)
        )
        detector.analyze([obj], frame_idx=1, frame_shape=(720, 1280))
        assert 501 in detector.track_states

        # Frame 2: Object 501 disappears, Object 502 appears
        obj2 = TrackedObject(
            object_id=502, class_name="package",
            bbox=(200.0, 200.0, 250.0, 250.0),
            center=(225.0, 225.0)
        )
        detector.analyze([obj2], frame_idx=2, frame_shape=(720, 1280))
        assert 501 not in detector.track_states, "Stale track 501 was not purged from track_states"
        assert 502 in detector.track_states


class TestCVPipelineRobustness:
    """Stress test VideoPipeline, MotionAnalyzer, and Annotator with synthetic inputs."""

    def test_motion_analyzer_empty_and_degraded_trajectories(self):
        analyzer = MotionAnalyzer()
        assert analyzer.compute_velocity([]) == (0.0, 0.0)
        assert analyzer.compute_velocity([(10.0, 10.0)]) == (0.0, 0.0)
        assert analyzer.compute_acceleration([(10.0, 10.0), (20.0, 20.0)]) == (0.0, 0.0)
        
        tracks = [
            TrackedObject(object_id=1, class_name="package", bbox=(0,0,10,10), center=(5,5), trajectory=[]),
            TrackedObject(object_id=2, class_name="package", bbox=(0,0,10,10), center=(5,5), trajectory=[(5,5)]),
            TrackedObject(object_id=3, class_name="package", bbox=(0,0,10,10), center=(5,5),
                          trajectory=[(5, 5), (10, 15), (15, 30), (20, 50)])
        ]
        feats = analyzer.analyze(tracks)
        assert len(feats) == 3
        assert feats[1].avg_velocity == 0.0
        assert feats[3].total_displacement > 0.0

    def test_annotator_draws_without_error_on_edge_cases(self):
        annotator = Annotator()
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        assert annotator.annotate(None, [], [], []) is None

        track = TrackedObject(
            object_id=999, class_name="package",
            bbox=(-100.0, -100.0, 2000.0, 2000.0),
            center=(950.0, 950.0),
            trajectory=[(-100.0, -100.0), (2000.0, 2000.0)]
        )
        from backend.risk.risk_engine import RiskAssessment
        event = BehaviourEvent(event_type="product_drop", object_id=999, confidence=0.9)
        assessment = RiskAssessment(level="HIGH", score=75, explanation="High risk drop", recommendation="Check load")
        
        out = annotator.annotate(frame, [track], [event], [assessment])
        assert out is not None
        assert out.shape == (480, 640, 3)


class TestObjectTrackerRobustness:
    """Stress test ObjectTracker under occlusion, missing frames, and rapid movement."""

    def test_tracker_maintains_consistent_id_across_trajectory(self):
        tracker = ObjectTracker(max_missing_frames=5, distance_threshold=80.0)
        
        tracked_ids = []
        for f in range(10):
            x = 100.0 + f * 20.0
            y = 200.0
            det = [Detection(class_id=25, class_name="package", confidence=0.9, bbox=(x, y, x + 40, y + 40))]
            tracks = tracker.update(det, frame_idx=f)
            assert len(tracks) == 1
            tracked_ids.append(tracks[0].object_id)

        assert len(set(tracked_ids)) == 1, f"Tracker ID changed across trajectory: {tracked_ids}"
        assert tracks[0].object_id == tracked_ids[0]
        assert len(tracks[0].trajectory) == 10

    def test_tracker_prunes_after_max_missing_frames(self):
        tracker = ObjectTracker(max_missing_frames=3, distance_threshold=60.0)
        
        d0 = [Detection(class_id=25, class_name="package", confidence=0.9, bbox=(100, 100, 150, 150))]
        t0 = tracker.update(d0, frame_idx=0)
        assert len(t0) == 1
        oid = t0[0].object_id

        # Missing for 1 frame (missing_frames=1 < 3)
        t1 = tracker.update([], frame_idx=1)
        assert oid in tracker.tracks
        
        # Missing for 2 frames (missing_frames=2 < 3)
        t2 = tracker.update([], frame_idx=2)
        assert oid in tracker.tracks

        # Missing for 3 frames (missing_frames=3 == max) -> pruned
        t3 = tracker.update([], frame_idx=3)
        assert oid not in tracker.tracks
        assert len(t3) == 0


class TestPipelineEndToEndStress:
    """End-to-end multi-frame integration test with VideoPipeline."""

    def test_pipeline_50_frame_synthetic_sequence(self):
        pipeline = VideoPipeline()
        
        all_events = []
        all_assessments = []

        for f in range(50):
            frame = np.full((480, 640, 3), 40, dtype=np.uint8)
            y_box = min(400, 50 + f * 12)
            frame[y_box:y_box+40, 200:260] = 220
            
            res = pipeline.process_frame(frame, frame_idx=f)
            assert res.frame_idx == f
            assert res.annotated_frame is not None
            assert res.annotated_frame.shape == (480, 640, 3)
            
            all_events.extend(res.events)
            all_assessments.extend(res.assessments)

        assert len(all_events) == len(all_assessments)
        for ev, assess in zip(all_events, all_assessments):
            validate_behaviour_event_schema(ev)
            assert assess.level in {"LOW", "MEDIUM", "HIGH", "CRITICAL"}
            assert 0 <= assess.score <= 100
            assert len(assess.explanation) > 0
            assert len(assess.recommendation) > 0
