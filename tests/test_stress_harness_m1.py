
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
from backend.vision.pipeline import VideoPipeline, FrameResult
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


class TestMultiObjectScalability:
    def test_50_concurrent_multi_class_objects(self):
        engine = BehaviourEngine()
        classes = ['package', 'carton', 'pallet', 'person', 'forklift', 'trolley', 'box', 'bottle']
        frame_latencies = []
        total_events = 0
        
        for f in range(50):
            tracked_objects = []
            for i in range(50):
                cls = classes[i % len(classes)]
                base_x = float((i * 24 + f * 2) % 1200)
                base_y = float((i * 14 + f) % 700)
                w, h = 40.0, 40.0
                tracked_objects.append(TrackedObject(
                    object_id=i + 1,
                    class_name=cls,
                    bbox=(base_x, base_y, base_x + w, base_y + h),
                    center=(base_x + w / 2, base_y + h / 2),
                    velocity=(2.0, 1.0),
                    acceleration=(0.0, 0.0),
                    trajectory=[(base_x + w / 2, base_y + h / 2)] * min(f + 1, 10),
                    confidence=0.9
                ))
            
            t0 = time.perf_counter()
            events = engine.analyze(tracked_objects, frame_idx=f, frame_shape=(720, 1280))
            t1 = time.perf_counter()
            
            frame_latencies.append((t1 - t0) * 1000.0)
            total_events += len(events)
            
            for ev in events:
                assert isinstance(ev, BehaviourEvent)
                assert 0.0 <= ev.confidence <= 1.0
        
        avg_latency = float(np.mean(frame_latencies))
        p95_latency = float(np.percentile(frame_latencies, 95))
        print(f'[50 Objects] Avg Latency: {avg_latency:.2f}ms, P95: {p95_latency:.2f}ms, Total Events: {total_events}')
        assert avg_latency < 50.0, f'50-object average latency too high: {avg_latency:.2f}ms'

    def test_100_concurrent_objects_dense_scene(self):
        engine = BehaviourEngine()
        tracked_objects = []
        for i in range(100):
            cls = 'package' if i % 2 == 0 else ('pallet' if i % 4 == 0 else 'forklift')
            x = float(100 + (i % 10) * 80)
            y = float(100 + (i // 10) * 50)
            tracked_objects.append(TrackedObject(
                object_id=i + 1,
                class_name=cls,
                bbox=(x, y, x + 60.0, y + 40.0),
                center=(x + 30.0, y + 20.0),
                velocity=(float((i % 5) - 2), float((i % 3) - 1)),
                trajectory=[(x + 30.0, y + 20.0)] * 5,
                confidence=0.85
            ))
            
        t0 = time.perf_counter()
        events = engine.analyze(tracked_objects, frame_idx=1, frame_shape=(720, 1280))
        latency = (time.perf_counter() - t0) * 1000.0
        print(f'[100 Objects Dense] Latency: {latency:.2f}ms, Events detected: {len(events)}')
        assert latency < 100.0, f'100-object frame analysis exceeded 100ms: {latency:.2f}ms'

    def test_200_concurrent_objects_scalability_curve(self):
        engine = BehaviourEngine()
        counts = [25, 50, 100, 200]
        latencies = {}
        
        for n in counts:
            objs = []
            for i in range(n):
                cls = 'package' if i % 2 == 0 else 'pallet'
                x = float((i * 15) % 1100)
                y = float((i * 12) % 650)
                objs.append(TrackedObject(
                    object_id=i + 1,
                    class_name=cls,
                    bbox=(x, y, x + 50.0, y + 40.0),
                    center=(x + 25.0, y + 20.0),
                    velocity=(1.0, 0.5),
                    trajectory=[(x + 25.0, y + 20.0)] * 5
                ))
            t0 = time.perf_counter()
            engine.analyze(objs, frame_idx=5, frame_shape=(720, 1280))
            latencies[n] = (time.perf_counter() - t0) * 1000.0
            
        print(f'[Scalability Curve] Latencies (ms): {latencies}')
        assert latencies[200] < 300.0, f'200 objects latency too high: {latencies[200]:.2f}ms'


class TestMemoryAndStateAccumulation:
    def test_long_running_pipeline_memory_stability(self):
        pipeline = VideoPipeline()
        dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        tracemalloc.start()
        snapshot_start = tracemalloc.take_snapshot()
        
        for f in range(500):
            dets = [
                Detection(class_id=25, class_name='package', confidence=0.88, bbox=(float(50 + (i*40 + f*2)%500), float(100 + i*30), float(90 + (i*40 + f*2)%500), float(140 + i*30)))
                for i in range(8)
            ]
            pipeline.detector.detect = lambda frame, d=dets: d
            pipeline.process_frame(dummy_frame, frame_idx=f)
            
        gc.collect()
        snapshot_end = tracemalloc.take_snapshot()
        tracemalloc.stop()
        
        top_stats = snapshot_end.compare_to(snapshot_start, 'lineno')
        total_growth_kb = sum(stat.size_diff for stat in top_stats) / 1024.0
        print(f'[VideoPipeline 500 frames] Total memory growth: {total_growth_kb:.2f} KB')
        assert total_growth_kb < 20480.0, f'Suspected memory leak in VideoPipeline: {total_growth_kb:.2f} KB'

    def test_detector_state_growth_under_continuous_stream_of_new_ids(self):
        engine = BehaviourEngine()
        for f in range(2000):
            obj_id = f + 1
            objs = [
                TrackedObject(
                    object_id=obj_id,
                    class_name='package',
                    bbox=(50.0, 50.0, 100.0, 100.0),
                    center=(75.0, 75.0),
                    velocity=(0.0, 0.0),
                    trajectory=[(75.0, 75.0)]
                )
            ]
            engine.analyze(objs, frame_idx=f, frame_shape=(720, 1280))
            
        state_sizes = {}
        for d in engine.detectors:
            name = d.__class__.__name__
            for attr in ['reported_tracks', 'reported_events', 'reported_pairs', 'track_states']:
                if hasattr(d, attr):
                    container = getattr(d, attr)
                    state_sizes[f'{name}.{attr}'] = len(container)
                    
        print(f'[2000 Transient Objects State Sizes]: {state_sizes}')
        # ZoneDetector should have recorded each transient object outside designated zone
        assert 'ZoneDetector.reported_tracks' in state_sizes
        assert 'DropDetector.track_states' in state_sizes
        # DropDetector purges disappeared tracks, so len should be 0 or 1
        assert state_sizes['DropDetector.track_states'] <= 1


class TestTemporalJitterAndHighFPS:
    def test_high_fps_micro_displacements(self):
        engine = BehaviourEngine()
        events = []
        traj = []
        for f in range(120):
            x = 200.0 + f * 0.2
            y = 300.0
            traj.append((x, y))
            obj = TrackedObject(
                object_id=42,
                class_name='package',
                bbox=(x - 20, y - 20, x + 20, y + 20),
                center=(x, y),
                velocity=(0.2, 0.0),
                acceleration=(0.0, 0.0),
                trajectory=traj[-10:]
            )
            evs = engine.analyze([obj], frame_idx=f, frame_shape=(720, 1280))
            events.extend(evs)
            
        throw_or_drop = [e for e in events if e.event_type in {'product_throwing', 'product_drop', 'rough_handling'}]
        assert len(throw_or_drop) == 0, f'False positive triggered on micro displacements: {throw_or_drop}'

    def test_irregular_frame_indices(self):
        engine = BehaviourEngine()
        indices = [0, 5, 5, 2, 100, 50, 1000]
        for f in indices:
            obj = TrackedObject(
                object_id=1,
                class_name='package',
                bbox=(100.0, 100.0, 150.0, 150.0),
                center=(125.0, 125.0),
                velocity=(0.0, 0.0),
                trajectory=[(125.0, 125.0)]
            )
            events = engine.analyze([obj], frame_idx=f, frame_shape=(720, 1280))
            assert isinstance(events, list)


class TestBoundaryOscillationsAndDuplicates:
    def test_zone_boundary_flutter(self):
        zone_detector = ZoneDetector()
        events = []
        for f in range(100):
            x = 79.0 if f % 2 == 0 else 81.0
            obj = TrackedObject(
                object_id=55,
                class_name='package',
                bbox=(x - 10, 200.0, x + 10, 220.0),
                center=(x, 210.0),
                velocity=(0.0, 0.0),
                trajectory=[(x, 210.0)]
            )
            evs = zone_detector.analyze([obj], frame_idx=f, frame_shape=(500, 1000))
            events.extend(evs)
            
        print(f'[Zone Boundary Flutter] Events generated across 100 oscillations: {len(events)}')
        assert len(events) == 1, f'Duplicate events generated during boundary flutter: {len(events)}'

    def test_pallet_misalignment_flutter(self):
        pallet_detector = PalletDetector()
        events = []
        for f in range(100):
            x = 119.0 if f % 2 == 0 else 121.0
            obj = TrackedObject(
                object_id=88,
                class_name='pallet',
                bbox=(x - 30, 400.0, x + 30, 430.0),
                center=(x, 415.0),
                velocity=(0.0, 0.0),
                trajectory=[(x, 415.0)]
            )
            evs = pallet_detector.analyze([obj], frame_idx=f, frame_shape=(500, 1000))
            events.extend(evs)
            
        print(f'[Pallet Boundary Flutter] Events generated across 100 oscillations: {len(events)}')
        assert len(events) == 1, f'Duplicate pallet misalignment events generated: {len(events)}'

    def test_behaviour_engine_per_frame_deduplication(self):
        engine = BehaviourEngine()
        obj = TrackedObject(
            object_id=99,
            class_name='package',
            bbox=(10.0, 10.0, 50.0, 50.0),
            center=(30.0, 30.0),
            velocity=(0.0, 0.0),
            trajectory=[(30.0, 30.0)]
        )
        events = engine.analyze([obj], frame_idx=1, frame_shape=(720, 1280))
        keys = [f'{e.event_type}_{e.object_id}_{e.frame_idx}' for e in events]
        assert len(keys) == len(set(keys)), f'Duplicates found in engine output: {keys}'


class TestMalformedInputsAndExceptions:
    def test_empty_and_corrupted_frame_inputs(self):
        pipeline = VideoPipeline()
        res1 = pipeline.behaviour.analyze([], frame_idx=0, frame_shape=(0, 0))
        assert isinstance(res1, list)
        
        res2 = pipeline.behaviour.analyze([], frame_idx=0, frame_shape=(-100, -100))
        assert isinstance(res2, list)
        
        frame_1x1 = np.zeros((1, 1, 3), dtype=np.uint8)
        res3 = pipeline.process_frame(frame_1x1, frame_idx=0)
        assert isinstance(res3, FrameResult)
        
        frame_gray = np.zeros((480, 640), dtype=np.uint8)
        res4 = pipeline.process_frame(frame_gray, frame_idx=1)
        assert isinstance(res4, FrameResult)

    def test_nan_and_inf_tracked_object_safety(self):
        engine = BehaviourEngine()
        malformed_objs = [
            TrackedObject(
                object_id=1,
                class_name='package',
                bbox=(float('nan'), 100.0, 150.0, 150.0),
                center=(float('nan'), 125.0),
                velocity=(0.0, float('nan')),
                acceleration=(float('inf'), 0.0),
                trajectory=[(float('nan'), float('nan'))]
            ),
            TrackedObject(
                object_id=2,
                class_name='pallet',
                bbox=(0.0, 0.0, float('inf'), 50.0),
                center=(float('inf'), 25.0),
                velocity=(float('inf'), 0.0),
                acceleration=(0.0, 0.0),
                trajectory=[]
            )
        ]
        events = engine.analyze(malformed_objs, frame_idx=1, frame_shape=(720, 1280))
        assert isinstance(events, list)

    def test_inverted_and_zero_bbox_safety(self):
        engine = BehaviourEngine()
        objs = [
            TrackedObject(
                object_id=1,
                class_name='package',
                bbox=(200.0, 200.0, 100.0, 100.0),
                center=(150.0, 150.0),
                velocity=(0.0, 0.0),
                trajectory=[(150.0, 150.0)]
            ),
            TrackedObject(
                object_id=2,
                class_name='package',
                bbox=(100.0, 100.0, 100.0, 100.0),
                center=(100.0, 100.0),
                velocity=(0.0, 0.0),
                trajectory=[(100.0, 100.0)]
            )
        ]
        events = engine.analyze(objs, frame_idx=1, frame_shape=(720, 1280))
        assert isinstance(events, list)


class TestPathologicalGeometryAndLoops:
    def test_massive_trajectory_history(self):
        engine = BehaviourEngine()
        large_traj = [(float(i % 500), float(i % 300)) for i in range(5000)]
        obj = TrackedObject(
            object_id=1,
            class_name='package',
            bbox=(100.0, 100.0, 150.0, 150.0),
            center=(125.0, 125.0),
            velocity=(1.0, 1.0),
            acceleration=(0.0, 0.0),
            trajectory=large_traj
        )
        t0 = time.perf_counter()
        events = engine.analyze([obj], frame_idx=1, frame_shape=(720, 1280))
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        print(f'[5000 Trajectory Points] Latency: {elapsed_ms:.2f}ms')
        assert elapsed_ms < 50.0, f'Trajectory processing took too long: {elapsed_ms:.2f}ms'

    def test_50_identical_co_located_objects(self):
        engine = BehaviourEngine()
        objs = [
            TrackedObject(
                object_id=i + 1,
                class_name='package',
                bbox=(200.0, 200.0, 250.0, 250.0),
                center=(225.0, 225.0),
                velocity=(0.0, 0.0),
                trajectory=[(225.0, 225.0)]
            )
            for i in range(50)
        ]
        t0 = time.perf_counter()
        events = engine.analyze(objs, frame_idx=1, frame_shape=(720, 1280))
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        print(f'[50 Co-located Objects] Latency: {elapsed_ms:.2f}ms, Events: {len(events)}')
        assert elapsed_ms < 100.0, f'Co-located processing exceeded threshold: {elapsed_ms:.2f}ms'
