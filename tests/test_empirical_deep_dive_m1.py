
import gc
import math
import time
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


class TestEmpiricalDeepDive:
    def test_end_to_end_video_pipeline_synthetic_run(self):
        pipeline = VideoPipeline(skip_frames=1)
        frames = [np.full((480, 640, 3), fill_value=i % 255, dtype=np.uint8) for i in range(30)]
        
        frame_results = []
        for f, frame in enumerate(frames):
            res = pipeline.process_frame(frame, frame_idx=f)
            assert isinstance(res, FrameResult)
            assert res.frame_idx == f
            assert res.annotated_frame is not None
            frame_results.append(res)
            
        assert len(frame_results) == 30

    def test_duplicate_event_suppression_across_consecutive_frames(self):
        engine = BehaviourEngine()
        # Simulate an improper stack resting motionless for 30 consecutive frames
        p_bottom = TrackedObject(
            object_id=10,
            class_name='package',
            bbox=(200.0, 300.0, 260.0, 350.0), # width=60
            center=(230.0, 325.0),
            velocity=(0.0, 0.0),
            trajectory=[(230.0, 325.0)]
        )
        p_top = TrackedObject(
            object_id=11,
            class_name='package',
            bbox=(180.0, 250.0, 280.0, 305.0), # width=100 (size ratio 100/60 = 1.66 > 1.2)
            center=(230.0, 277.5),
            velocity=(0.0, 0.0),
            trajectory=[(230.0, 277.5)]
        )
        
        events_by_frame = []
        for f in range(30):
            evs = engine.analyze([p_bottom, p_top], frame_idx=f, frame_shape=(720, 1280))
            events_by_frame.append(evs)
            
        total_events = sum(len(evs) for evs in events_by_frame)
        print(f'[Improper Stack Resting 30 Frames] Total events emitted: {total_events}')
        # StackingDetector reports once for the pair (11, 10), so total events across 30 frames should be 1
        assert total_events == 1, f'Expected 1 event for static stack, got {total_events}'

    def test_drop_detector_state_machine_transitions(self):
        detector = DropDetector()
        
        # Scenario: Object falls, rests, then is picked up again (new cycle)
        # Drop 1:
        f0 = TrackedObject(1, 'package', (100, 100, 150, 150), (125, 125), (0, 0), trajectory=[(125, 125)])
        detector.analyze([f0], 0, (720, 1280))
        
        f1 = TrackedObject(1, 'package', (100, 200, 150, 250), (125, 225), (0, 10), trajectory=[(125, 125), (125, 225)])
        detector.analyze([f1], 1, (720, 1280))
        
        f2 = TrackedObject(1, 'package', (100, 200, 150, 250), (125, 225), (0, 0), trajectory=[(125, 125), (125, 225), (125, 225)])
        evs2 = detector.analyze([f2], 2, (720, 1280))
        assert len(evs2) == 1
        assert evs2[0].event_type == 'product_drop'
        
        # Stationary on ground for 10 frames: should not re-trigger
        for f in range(3, 13):
            evs = detector.analyze([f2], f, (720, 1280))
            assert len(evs) == 0

    def test_all_detectors_robust_to_fuzzed_inputs(self):
        engine = BehaviourEngine()
        np.random.seed(42)
        
        for trial in range(50):
            num_objs = np.random.randint(0, 30)
            objs = []
            for i in range(num_objs):
                cls = np.random.choice(['package', 'carton', 'pallet', 'person', 'forklift', 'trolley', 'box', 'unknown', ''])
                x1 = np.random.uniform(-500, 2000)
                y1 = np.random.uniform(-500, 2000)
                w = np.random.uniform(-100, 300)
                h = np.random.uniform(-100, 300)
                vx = np.random.uniform(-100, 100)
                vy = np.random.uniform(-100, 100)
                traj_len = np.random.randint(0, 20)
                traj = [(np.random.uniform(-500, 2000), np.random.uniform(-500, 2000)) for _ in range(traj_len)]
                
                objs.append(TrackedObject(
                    object_id=i + 1,
                    class_name=cls,
                    bbox=(x1, y1, x1 + w, y1 + h),
                    center=(x1 + w / 2, y1 + h / 2),
                    velocity=(vx, vy),
                    acceleration=(vx * 0.1, vy * 0.1),
                    trajectory=traj,
                    confidence=float(np.random.uniform(0.0, 1.0))
                ))
                
            frame_shape = (np.random.randint(0, 1080), np.random.randint(0, 1920))
            try:
                events = engine.analyze(objs, frame_idx=trial, frame_shape=frame_shape)
                assert isinstance(events, list)
            except Exception as e:
                pytest.fail(f'Fuzz trial {trial} crashed with exception: {e}')
