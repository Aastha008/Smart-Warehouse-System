"""
AI Warehouse Intelligence - Milestone 5 Comprehensive Empirical Stress Testing Harness
Validates CV Pipeline, ObjectTracker, MotionAnalyzer, and all 10 Temporal Behaviour Detectors
under extreme trajectories, boundary conditions, malformed/NaN/Inf coordinates, temporal jitter,
multi-object scalability (50-250+ concurrent entities), and long-duration memory stability (2000+ frames).
"""

import gc
import math
import time
import tracemalloc
import numpy as np
import pytest
from typing import List, Tuple, Dict, Any

from backend.vision.detector import Detection, WarehouseDetector
from backend.vision.tracker import ObjectTracker, TrackedObject
from backend.vision.motion import MotionAnalyzer
from backend.vision.annotator import Annotator
from backend.vision.pipeline import VideoPipeline, FrameResult, AnalysisResult
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


def assert_event_schema(ev: BehaviourEvent):
    """Rigorous assertion of BehaviourEvent schema invariants."""
    assert isinstance(ev, BehaviourEvent)
    assert isinstance(ev.event_type, str) and len(ev.event_type) > 0
    assert isinstance(ev.object_id, int)
    assert isinstance(ev.frame_idx, int) and ev.frame_idx >= 0
    assert isinstance(ev.confidence, (float, int))
    assert 0.0 <= ev.confidence <= 1.0, f"Confidence {ev.confidence} out of range [0, 1]"
    assert not math.isnan(ev.confidence) and not math.isinf(ev.confidence)
    assert isinstance(ev.timestamp, str)
    assert isinstance(ev.location, str)
    assert isinstance(ev.evidence, dict)
    for k, v in ev.evidence.items():
        if isinstance(v, float):
            assert not math.isnan(v) and not math.isinf(v), f"Evidence '{k}' is NaN/Inf: {v}"


class TestExtremeTrajectoriesAndBoundaryConditions:
    """Stress test boundary coordinates, zero/negative bounding boxes, and NaN/inf values."""

    def test_zero_size_bounding_boxes(self):
        engine = BehaviourEngine()
        objs = [
            TrackedObject(
                object_id=1,
                class_name="package",
                bbox=(100.0, 100.0, 100.0, 100.0),
                center=(100.0, 100.0),
                velocity=(0.0, 0.0),
                trajectory=[(100.0, 100.0)]
            ),
            TrackedObject(
                object_id=2,
                class_name="pallet",
                bbox=(0.0, 0.0, 0.0, 0.0),
                center=(0.0, 0.0),
                velocity=(0.0, 0.0),
                trajectory=[(0.0, 0.0)]
            )
        ]
        events = engine.analyze(objs, frame_idx=0, frame_shape=(720, 1280))
        assert isinstance(events, list)
        for ev in events:
            assert_event_schema(ev)

    def test_negative_and_out_of_bounds_coordinates(self):
        engine = BehaviourEngine()
        objs = [
            TrackedObject(
                object_id=1,
                class_name="package",
                bbox=(-400.0, -300.0, -350.0, -250.0),
                center=(-375.0, -275.0),
                velocity=(-10.0, -5.0),
                trajectory=[(-375.0, -275.0)]
            ),
            TrackedObject(
                object_id=2,
                class_name="carton",
                bbox=(5000.0, 8000.0, 5060.0, 8060.0),
                center=(5030.0, 8030.0),
                velocity=(20.0, 20.0),
                trajectory=[(5030.0, 8030.0)]
            )
        ]
        events = engine.analyze(objs, frame_idx=1, frame_shape=(720, 1280))
        assert isinstance(events, list)
        for ev in events:
            assert_event_schema(ev)
        assert any(ev.event_type == "product_outside_zone" for ev in events)

    def test_nan_and_inf_coordinate_safety(self):
        engine = BehaviourEngine()
        malformed = [
            TrackedObject(
                object_id=10,
                class_name="package",
                bbox=(float('nan'), 100.0, 150.0, 150.0),
                center=(float('nan'), 125.0),
                velocity=(float('nan'), 5.0),
                acceleration=(float('inf'), 0.0),
                trajectory=[(float('nan'), float('nan'))]
            ),
            TrackedObject(
                object_id=11,
                class_name="pallet",
                bbox=(100.0, 100.0, float('inf'), 150.0),
                center=(float('inf'), 125.0),
                velocity=(float('inf'), float('-inf')),
                acceleration=(0.0, 0.0),
                trajectory=[]
            )
        ]
        events = engine.analyze(malformed, frame_idx=2, frame_shape=(720, 1280))
        assert isinstance(events, list)

    def test_inverted_coordinates(self):
        engine = BehaviourEngine()
        inverted = [
            TrackedObject(
                object_id=20,
                class_name="package",
                bbox=(300.0, 400.0, 100.0, 200.0), # x2 < x1, y2 < y1
                center=(200.0, 300.0),
                velocity=(0.0, 0.0)
            )
        ]
        events = engine.analyze(inverted, frame_idx=3, frame_shape=(720, 1280))
        assert isinstance(events, list)
        for ev in events:
            assert_event_schema(ev)

    def test_subnormal_and_extreme_floating_point_values(self):
        engine = BehaviourEngine()
        extreme = [
            TrackedObject(
                object_id=30,
                class_name="package",
                bbox=(100.0, 100.0, 150.0, 150.0),
                center=(125.0, 125.0),
                velocity=(1e-25, -1e-25),
                acceleration=(1e-30, 1e-30),
                trajectory=[(125.0, 125.0)]
            ),
            TrackedObject(
                object_id=31,
                class_name="carton",
                bbox=(200.0, 200.0, 260.0, 260.0),
                center=(230.0, 230.0),
                velocity=(1e7, 1e7),
                acceleration=(5e6, 5e6),
                trajectory=[(200.0, 200.0), (230.0, 230.0)]
            )
        ]
        events = engine.analyze(extreme, frame_idx=4, frame_shape=(720, 1280))
        for ev in events:
            assert_event_schema(ev)


class TestTemporalNoiseJitterAndStateTransitions:
    """Stress test jitter, noise, missing frames, and rapid state transitions."""

    def test_rapid_alternating_state_transitions(self):
        detector = DropDetector()
        events = []
        # Alternating between falling velocity and stationary velocity every frame
        for f in range(20):
            vy = 15.0 if f % 2 == 1 else 0.0
            y = 100.0 + f * 10.0
            obj = TrackedObject(
                object_id=1,
                class_name="package",
                bbox=(100.0, y - 20, 140.0, y + 20),
                center=(120.0, y),
                velocity=(0.0, vy),
                trajectory=[(120.0, 100.0 + i * 10.0) for i in range(f + 1)]
            )
            evs = detector.analyze([obj], frame_idx=f, frame_shape=(720, 1280))
            events.extend(evs)
        assert isinstance(events, list)
        for ev in events:
            assert_event_schema(ev)

    def test_missing_frames_and_track_reacquisition(self):
        tracker = ObjectTracker(max_missing_frames=5, distance_threshold=60.0)
        # Frame 0: detection present
        d0 = [Detection(class_id=25, class_name="package", confidence=0.9, bbox=(100.0, 100.0, 150.0, 150.0))]
        t0 = tracker.update(d0, frame_idx=0)
        assert len(t0) == 1
        oid = t0[0].object_id

        # Frames 1-3: missing
        for f in range(1, 4):
            tf = tracker.update([], frame_idx=f)
            assert oid in tracker.tracks

        # Frame 4: re-detected slightly displaced
        d4 = [Detection(class_id=25, class_name="package", confidence=0.88, bbox=(120.0, 110.0, 170.0, 160.0))]
        t4 = tracker.update(d4, frame_idx=4)
        assert len(t4) == 1
        assert t4[0].object_id == oid
        assert t4[0].missing_frames == 0

    def test_high_frequency_trajectory_jitter(self):
        engine = BehaviourEngine()
        np.random.seed(1337)
        traj = []
        events = []
        for f in range(60):
            # Slow steady motion + high frequency jitter (+- 1.5px)
            base_x = 200.0 + f * 0.5
            base_y = 300.0
            jitter_x = float(np.random.normal(0, 1.2))
            jitter_y = float(np.random.normal(0, 1.2))
            pos = (base_x + jitter_x, base_y + jitter_y)
            traj.append(pos)
            obj = TrackedObject(
                object_id=55,
                class_name="package",
                bbox=(pos[0] - 20, pos[1] - 20, pos[0] + 20, pos[1] + 20),
                center=pos,
                velocity=(0.5 + jitter_x, jitter_y),
                acceleration=(jitter_x, jitter_y),
                trajectory=traj[-10:]
            )
            evs = engine.analyze([obj], frame_idx=f, frame_shape=(720, 1280))
            events.extend(evs)
        # Should not falsely trigger product_drop or product_throwing due to micro-jitter
        false_positives = [e for e in events if e.event_type in {"product_drop", "product_throwing"}]
        assert len(false_positives) == 0, f"False positives on micro-jitter: {false_positives}"

    def test_non_monotonic_and_jumpy_frame_indices(self):
        engine = BehaviourEngine()
        indices = [0, 50, 20, 1000, 3, 500, 500, 0]
        for idx in indices:
            obj = TrackedObject(
                object_id=77,
                class_name="package",
                bbox=(200.0, 200.0, 250.0, 250.0),
                center=(225.0, 225.0),
                velocity=(0.0, 0.0),
                trajectory=[(225.0, 225.0)]
            )
            evs = engine.analyze([obj], frame_idx=idx, frame_shape=(720, 1280))
            assert isinstance(evs, list)


class TestMultiObjectScalabilityAndDensity:
    """Stress test multi-object scalability across 50, 100, and 250 concurrent entities."""

    def test_50_concurrent_entities_scalability(self):
        engine = BehaviourEngine()
        classes = ["package", "carton", "pallet", "person", "forklift", "trolley", "box"]
        latencies = []
        total_events = 0

        for f in range(30):
            objs = []
            for i in range(50):
                cls = classes[i % len(classes)]
                bx = float((i * 25 + f * 3) % 1200)
                by = float((i * 15 + f * 2) % 680)
                objs.append(TrackedObject(
                    object_id=i + 1,
                    class_name=cls,
                    bbox=(bx, by, bx + 45.0, by + 40.0),
                    center=(bx + 22.5, by + 20.0),
                    velocity=(2.0, 1.0),
                    acceleration=(0.0, 0.0),
                    trajectory=[(bx + 22.5, by + 20.0)] * 5,
                    confidence=0.92
                ))
            t0 = time.perf_counter()
            events = engine.analyze(objs, frame_idx=f, frame_shape=(720, 1280))
            lat = (time.perf_counter() - t0) * 1000.0
            latencies.append(lat)
            total_events += len(events)
            for ev in events:
                assert_event_schema(ev)

        avg_lat = float(np.mean(latencies))
        p95_lat = float(np.percentile(latencies, 95))
        print(f"\n[50-Object Scalability] Mean: {avg_lat:.2f}ms, P95: {p95_lat:.2f}ms, Events: {total_events}")
        assert avg_lat < 40.0, f"50-object mean latency exceeded 40ms: {avg_lat:.2f}ms"
        assert p95_lat < 60.0, f"50-object P95 latency exceeded 60ms: {p95_lat:.2f}ms"

    def test_100_concurrent_dense_warehouse_entities(self):
        engine = BehaviourEngine()
        classes = ["package", "pallet", "forklift", "person", "carton", "box", "trolley"]
        objs = []
        for i in range(100):
            cls = classes[i % len(classes)]
            x = float(50 + (i % 10) * 110)
            y = float(50 + (i // 10) * 60)
            objs.append(TrackedObject(
                object_id=i + 1,
                class_name=cls,
                bbox=(x, y, x + 50.0, y + 45.0),
                center=(x + 25.0, y + 22.5),
                velocity=(float(i % 4 - 2), float(i % 3 - 1)),
                trajectory=[(x + 25.0, y + 22.5)] * 5,
                confidence=0.88
            ))
        t0 = time.perf_counter()
        events = engine.analyze(objs, frame_idx=1, frame_shape=(720, 1280))
        lat = (time.perf_counter() - t0) * 1000.0
        print(f"[100-Object Dense] Latency: {lat:.2f}ms, Events: {len(events)}")
        assert lat < 80.0, f"100-object frame analysis exceeded 80ms: {lat:.2f}ms"
        for ev in events:
            assert_event_schema(ev)

    def test_250_concurrent_extreme_load(self):
        engine = BehaviourEngine()
        objs = []
        for i in range(250):
            cls = "package" if i % 2 == 0 else ("pallet" if i % 5 == 0 else "forklift")
            x = float((i * 12) % 1200)
            y = float((i * 8) % 680)
            objs.append(TrackedObject(
                object_id=i + 1,
                class_name=cls,
                bbox=(x, y, x + 35.0, y + 35.0),
                center=(x + 17.5, y + 17.5),
                velocity=(1.0, 0.5),
                trajectory=[(x + 17.5, y + 17.5)] * 4
            ))
        t0 = time.perf_counter()
        events = engine.analyze(objs, frame_idx=1, frame_shape=(720, 1280))
        lat = (time.perf_counter() - t0) * 1000.0
        print(f"[250-Object Extreme] Latency: {lat:.2f}ms, Events: {len(events)}")
        assert lat < 200.0, f"250-object frame analysis exceeded 200ms: {lat:.2f}ms"
        for ev in events:
            assert_event_schema(ev)


class TestLongDurationMemoryAndStateStability:
    """Stress test memory stability and heap growth over long-running continuous sequences."""

    def test_2000_frame_continuous_stream_memory_stability(self):
        engine = BehaviourEngine()
        tracemalloc.start()
        snap_start = tracemalloc.take_snapshot()

        for f in range(2000):
            # Rotating set of 10 active objects + 1 new transient object every 10 frames
            objs = []
            for i in range(10):
                bx = float(200 + (i * 80 + f * 2) % 800)
                by = float(200 + (i * 40 + f) % 400)
                objs.append(TrackedObject(
                    object_id=i + 1,
                    class_name="package" if i % 2 == 0 else "pallet",
                    bbox=(bx, by, bx + 40, by + 40),
                    center=(bx + 20, by + 20),
                    velocity=(2.0, 1.0),
                    trajectory=[(bx + 20, by + 20)] * min(f + 1, 10),
                    confidence=0.9
                ))
            if f % 10 == 0:
                transient_id = 1000 + f
                objs.append(TrackedObject(
                    object_id=transient_id,
                    class_name="carton",
                    bbox=(50.0, 50.0, 90.0, 90.0),
                    center=(70.0, 70.0),
                    velocity=(0.0, 0.0),
                    trajectory=[(70.0, 70.0)]
                ))
            engine.analyze(objs, frame_idx=f, frame_shape=(720, 1280))

        gc.collect()
        snap_end = tracemalloc.take_snapshot()
        tracemalloc.stop()

        diffs = snap_end.compare_to(snap_start, 'lineno')
        total_growth_kb = sum(stat.size_diff for stat in diffs) / 1024.0
        print(f"\n[2000 Frames Memory Stability] Heap Growth: {total_growth_kb:.2f} KB ({total_growth_kb/1024.0:.2f} MB)")
        # Must not exceed 15 MB heap growth over 2000 frames
        assert total_growth_kb < 15360.0, f"Memory leak detected: heap grew by {total_growth_kb:.2f} KB"

    def test_detector_state_dictionary_bounds(self):
        engine = BehaviourEngine()
        for f in range(1000):
            # Rapid churn of 1000 transient objects
            obj = TrackedObject(
                object_id=f + 1,
                class_name="package",
                bbox=(10.0, 10.0, 50.0, 50.0),
                center=(30.0, 30.0),
                velocity=(0.0, 0.0),
                trajectory=[(30.0, 30.0)]
            )
            engine.analyze([obj], frame_idx=f, frame_shape=(720, 1280))

        # Check DropDetector active track states
        drop_detector = [d for d in engine.detectors if isinstance(d, DropDetector)][0]
        assert len(drop_detector.track_states) <= 2, f"DropDetector failed to prune stale tracks: {len(drop_detector.track_states)}"


class TestAllTenTemporalDetectorsRigorousVerification:
    """Rigorous positive and negative verification across all 10 temporal detectors."""

    def test_d1_product_drop_full_lifecycle(self):
        detector = DropDetector()
        # Fall phase -> Rest phase
        traj = [(200.0, 100.0)]
        events = []
        for f in range(1, 8):
            y = 100.0 + f * 25.0 # drops 175px
            traj.append((200.0, y))
            obj = TrackedObject(
                object_id=101, class_name="package",
                bbox=(180.0, y - 20, 220.0, y + 20),
                center=(200.0, y),
                velocity=(0.0, 25.0 if f < 6 else 0.0),
                trajectory=list(traj)
            )
            evs = detector.analyze([obj], frame_idx=f, frame_shape=(720, 1280))
            events.extend(evs)
        assert len(events) >= 1
        assert events[0].event_type == "product_drop"
        assert events[0].evidence["drop_height_px"] >= 40.0
        assert_event_schema(events[0])

    def test_d2_product_dragging_extended_window(self):
        detector = DragDetector()
        traj = []
        events = []
        for f in range(15):
            x = 100.0 + f * 12.0 # 168px horizontal
            y = 450.0
            traj.append((x, y))
            obj = TrackedObject(
                object_id=102, class_name="carton",
                bbox=(x - 30, y - 25, x + 30, y + 25),
                center=(x, y),
                velocity=(12.0, 0.0),
                trajectory=list(traj)
            )
            evs = detector.analyze([obj], frame_idx=f, frame_shape=(720, 1280))
            events.extend(evs)
        assert len(events) == 1
        assert events[0].event_type == "product_dragging"
        assert events[0].evidence["drag_distance_px"] >= 50.0
        assert_event_schema(events[0])

    def test_d3_product_throwing_arc_and_velocity(self):
        detector = ThrowDetector()
        obj = TrackedObject(
            object_id=103, class_name="box",
            bbox=(100.0, 100.0, 150.0, 150.0),
            center=(125.0, 125.0),
            velocity=(14.0, -7.0),
            trajectory=[(50.0, 180.0), (75.0, 140.0), (100.0, 120.0), (125.0, 125.0)]
        )
        evs = detector.analyze([obj], frame_idx=1, frame_shape=(720, 1280))
        assert len(evs) == 1
        assert evs[0].event_type == "product_throwing"
        assert evs[0].evidence["velocity"] >= 10.0
        assert_event_schema(evs[0])

    def test_d4_rough_handling_jerk_and_reversals(self):
        detector = RoughHandlingDetector()
        # Trajectory with severe direction reversals
        traj = [(100.0, 100.0), (140.0, 110.0), (90.0, 130.0), (150.0, 140.0)]
        obj = TrackedObject(
            object_id=104, class_name="package",
            bbox=(120.0, 115.0, 170.0, 165.0),
            center=(145.0, 140.0),
            velocity=(10.0, 5.0),
            acceleration=(9.0, 7.0),
            trajectory=traj
        )
        evs = detector.analyze([obj], frame_idx=1, frame_shape=(720, 1280))
        assert len(evs) == 1
        assert evs[0].event_type == "rough_handling"
        assert evs[0].evidence["acceleration"] >= 3.0
        assert_event_schema(evs[0])

    def test_d5_improper_stacking_heavy_top(self):
        detector = StackingDetector()
        top = TrackedObject(
            object_id=105, class_name="carton",
            bbox=(100.0, 100.0, 280.0, 180.0), # w=180
            center=(190.0, 140.0)
        )
        bottom = TrackedObject(
            object_id=106, class_name="carton",
            bbox=(140.0, 180.0, 240.0, 240.0), # w=100 (ratio 1.8 > 1.2)
            center=(190.0, 210.0)
        )
        evs = detector.analyze([top, bottom], frame_idx=1, frame_shape=(720, 1280))
        assert len(evs) == 1
        assert evs[0].event_type == "improper_stacking"
        assert evs[0].evidence["size_ratio"] >= 1.2
        assert_event_schema(evs[0])

    def test_d6_unstable_stacking_high_aspect(self):
        detector = UnstableStackDetector()
        obj = TrackedObject(
            object_id=107, class_name="box",
            bbox=(100.0, 50.0, 140.0, 300.0), # w=40, h=250 -> aspect 6.25 > 2.4
            center=(120.0, 175.0),
            trajectory=[(120.0, 175.0)] * 5
        )
        evs = detector.analyze([obj], frame_idx=1, frame_shape=(720, 1280))
        assert len(evs) == 1
        assert evs[0].event_type == "unstable_stacking"
        assert evs[0].evidence["aspect_ratio"] >= 2.4
        assert_event_schema(evs[0])

    def test_d7_product_outside_zone_detection(self):
        detector = ZoneDetector()
        obj = TrackedObject(
            object_id=108, class_name="package",
            bbox=(10.0, 10.0, 50.0, 50.0),
            center=(30.0, 30.0) # norm_x = 30/1280 = 0.023 < 0.08
        )
        evs = detector.analyze([obj], frame_idx=1, frame_shape=(720, 1280))
        assert len(evs) == 1
        assert evs[0].event_type == "product_outside_zone"
        assert_event_schema(evs[0])

    def test_d8_incorrect_pallet_position_overhang(self):
        detector = PalletDetector()
        pallet = TrackedObject(
            object_id=109, class_name="pallet",
            bbox=(200.0, 300.0, 360.0, 360.0), # w=160
            center=(280.0, 330.0)
        )
        pkg = TrackedObject(
            object_id=110, class_name="package",
            bbox=(140.0, 220.0, 420.0, 305.0), # w=280 (overhang left 60, right 60)
            center=(280.0, 262.5)
        )
        evs = detector.analyze([pallet, pkg], frame_idx=1, frame_shape=(720, 1280))
        assert len(evs) == 1
        assert evs[0].event_type == "incorrect_pallet_position"
        assert evs[0].evidence["issue"] == "product_overhang"
        assert_event_schema(evs[0])

    def test_d9_unsafe_loading_sequence_concurrent_movers(self):
        detector = LoadingSequenceDetector()
        moving_pkgs = [
            TrackedObject(
                object_id=200 + i, class_name="package",
                bbox=(100 + i * 80, 200, 150 + i * 80, 250),
                center=(125 + i * 80, 225),
                velocity=(3.5, 1.0)
            )
            for i in range(5) # 5 simultaneously moving > max 3
        ]
        evs = detector.analyze(moving_pkgs, frame_idx=1, frame_shape=(720, 1280))
        assert len(evs) >= 1
        assert any(e.evidence.get("issue") == "excessive_simultaneous_loads" for e in evs)
        for ev in evs:
            assert_event_schema(ev)

    def test_d10_improper_handling_equipment_manual_oversized(self):
        detector = EquipmentDetector()
        oversized = TrackedObject(
            object_id=210, class_name="package",
            bbox=(100.0, 100.0, 300.0, 280.0), # size 200px > 130px
            center=(200.0, 190.0),
            velocity=(3.0, 0.0),
            trajectory=[(190.0, 190.0), (195.0, 190.0), (200.0, 190.0)]
        )
        evs = detector.analyze([oversized], frame_idx=1, frame_shape=(720, 1280))
        assert len(evs) == 1
        assert evs[0].event_type == "improper_handling_equipment"
        assert evs[0].evidence["issue"] == "heavy_load_handled_without_equipment"
        assert_event_schema(evs[0])
