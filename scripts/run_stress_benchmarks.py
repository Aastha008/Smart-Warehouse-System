"""
AI Warehouse Intelligence - Milestone 5 Empirical Stress Benchmark Runner
Executes comprehensive stress scenarios, captures runtime metrics (latency, memory, throughput, accuracy),
and generates a structured verification report.
"""

import os
import sys
import gc
import math
import time
import json
import tracemalloc
import numpy as np

# Ensure workspace root is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

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


def run_all_benchmarks():
    results = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "milestone": "M5",
        "benchmarks": {},
        "summary": {}
    }
    
    print("=" * 70)
    print("AI WAREHOUSE INTELLIGENCE - M5 EMPIRICAL STRESS BENCHMARK SUITE")
    print("=" * 70)

    # -------------------------------------------------------------
    # 1. Multi-Object Scalability Benchmark
    # -------------------------------------------------------------
    print("\n[Benchmark 1] Multi-Object Scalability (25, 50, 100, 200, 300 entities)...")
    engine = BehaviourEngine()
    classes = ["package", "carton", "pallet", "person", "forklift", "trolley", "box"]
    scalability_results = {}

    for count in [25, 50, 100, 200, 300]:
        latencies = []
        for f in range(20):
            objs = []
            for i in range(count):
                cls = classes[i % len(classes)]
                bx = float((i * 20 + f * 2) % 1200)
                by = float((i * 12 + f) % 650)
                objs.append(TrackedObject(
                    object_id=i + 1,
                    class_name=cls,
                    bbox=(bx, by, bx + 40.0, by + 40.0),
                    center=(bx + 20.0, by + 20.0),
                    velocity=(1.5, 0.5),
                    trajectory=[(bx + 20.0, by + 20.0)] * 5,
                    confidence=0.9
                ))
            t0 = time.perf_counter()
            events = engine.analyze(objs, frame_idx=f, frame_shape=(720, 1280))
            lat = (time.perf_counter() - t0) * 1000.0
            latencies.append(lat)

        mean_lat = float(np.mean(latencies))
        p95_lat = float(np.percentile(latencies, 95))
        fps = 1000.0 / mean_lat if mean_lat > 0 else 9999.0
        scalability_results[str(count)] = {
            "entity_count": count,
            "mean_latency_ms": round(mean_lat, 2),
            "p95_latency_ms": round(p95_lat, 2),
            "throughput_fps": round(fps, 1),
            "status": "PASS" if mean_lat < (200.0 if count == 300 else 100.0) else "FAIL"
        }
        print(f"  - {count:3d} Objects: Mean={mean_lat:6.2f}ms | P95={p95_lat:6.2f}ms | Throughput={fps:6.1f} FPS [{scalability_results[str(count)]['status']}]")

    results["benchmarks"]["multi_object_scalability"] = scalability_results

    # -------------------------------------------------------------
    # 2. Long-Duration Memory Stability (2,000 Continuous Frames)
    # -------------------------------------------------------------
    print("\n[Benchmark 2] Long-Duration Memory & State Stability (2,000 Frames)...")
    gc.collect()
    tracemalloc.start()
    snap_start = tracemalloc.take_snapshot()

    engine_long = BehaviourEngine()
    total_events_emitted = 0
    t0_long = time.perf_counter()

    for f in range(2000):
        objs = []
        for i in range(12):
            bx = float(100 + (i * 70 + f * 2) % 900)
            by = float(100 + (i * 35 + f) % 500)
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
            objs.append(TrackedObject(
                object_id=5000 + f,
                class_name="carton",
                bbox=(50.0, 50.0, 90.0, 90.0),
                center=(70.0, 70.0),
                velocity=(0.0, 0.0),
                trajectory=[(70.0, 70.0)]
            ))
        evs = engine_long.analyze(objs, frame_idx=f, frame_shape=(720, 1280))
        total_events_emitted += len(evs)

    gc.collect()
    snap_end = tracemalloc.take_snapshot()
    tracemalloc.stop()
    total_time_s = time.perf_counter() - t0_long

    diffs = snap_end.compare_to(snap_start, 'lineno')
    heap_growth_kb = sum(stat.size_diff for stat in diffs) / 1024.0
    heap_growth_mb = heap_growth_kb / 1024.0

    memory_result = {
        "frames_processed": 2000,
        "total_time_seconds": round(total_time_s, 2),
        "avg_frame_time_ms": round((total_time_s / 2000.0) * 1000.0, 3),
        "heap_growth_kb": round(heap_growth_kb, 2),
        "heap_growth_mb": round(heap_growth_mb, 3),
        "memory_leak_detected": bool(heap_growth_mb > 15.0),
        "total_events_emitted": total_events_emitted,
        "status": "PASS" if heap_growth_mb < 15.0 else "FAIL"
    }
    print(f"  - 2,000 Frames processed in {total_time_s:.2f}s ({memory_result['avg_frame_time_ms']:.2f} ms/frame)")
    print(f"  - Heap Growth: {heap_growth_kb:.2f} KB ({heap_growth_mb:.2f} MB) [Threshold < 15.0 MB] -> [{memory_result['status']}]")
    results["benchmarks"]["memory_stability"] = memory_result

    # -------------------------------------------------------------
    # 3. Boundary, Extreme & Malformed Coordinate Robustness
    # -------------------------------------------------------------
    print("\n[Benchmark 3] Boundary, Extreme & Malformed Coordinate Robustness...")
    boundary_cases = [
        ("zero_bounding_box", [TrackedObject(1, "package", (100, 100, 100, 100), (100, 100))]),
        ("negative_coords", [TrackedObject(2, "package", (-300, -200, -250, -150), (-275, -175))]),
        ("extreme_coords_10k", [TrackedObject(3, "pallet", (10000, 10000, 10200, 10200), (10100, 10100))]),
        ("nan_coordinates", [TrackedObject(4, "package", (float('nan'), 100, 150, 150), (float('nan'), 125))]),
        ("inf_velocities", [TrackedObject(5, "carton", (100, 100, 150, 150), (125, 125), velocity=(float('inf'), float('-inf')))]),
        ("subnormal_coords", [TrackedObject(6, "box", (100, 100, 150, 150), (125, 125), velocity=(1e-25, -1e-25))]),
        ("inverted_bbox", [TrackedObject(7, "package", (300, 300, 100, 100), (200, 200))]),
        ("extreme_aspect_tower", [TrackedObject(8, "box", (100, 50, 105, 500), (102.5, 275))]),
    ]

    boundary_results = {}
    engine_b = BehaviourEngine()
    for name, obj_list in boundary_cases:
        try:
            evs = engine_b.analyze(obj_list, frame_idx=0, frame_shape=(720, 1280))
            is_valid = isinstance(evs, list)
            for e in evs:
                assert 0.0 <= e.confidence <= 1.0
            boundary_results[name] = {"handled_safely": True, "events_emitted": len(evs), "status": "PASS"}
            print(f"  - {name:25s}: Handled Safely, {len(evs)} events emitted [PASS]")
        except Exception as exc:
            boundary_results[name] = {"handled_safely": False, "error": str(exc), "status": "FAIL"}
            print(f"  - {name:25s}: ERROR: {exc} [FAIL]")

    results["benchmarks"]["boundary_robustness"] = boundary_results

    # -------------------------------------------------------------
    # 4. Temporal Jitter & State Transition Robustness
    # -------------------------------------------------------------
    print("\n[Benchmark 4] Temporal Jitter, Noise & State Transitions...")
    jitter_results = {}
    
    # Micro-jitter test
    traj_jitter = []
    false_positives = 0
    engine_j = BehaviourEngine()
    for f in range(100):
        pos = (200.0 + f * 0.4 + np.random.normal(0, 1.0), 300.0 + np.random.normal(0, 1.0))
        traj_jitter.append(pos)
        obj = TrackedObject(
            object_id=99,
            class_name="package",
            bbox=(pos[0]-20, pos[1]-20, pos[0]+20, pos[1]+20),
            center=pos,
            velocity=(0.4, 0.0),
            trajectory=traj_jitter[-10:]
        )
        evs = engine_j.analyze([obj], frame_idx=f, frame_shape=(720, 1280))
        fp = [e for e in evs if e.event_type in {"product_drop", "product_throwing"}]
        false_positives += len(fp)

    jitter_results["micro_jitter_100_frames"] = {
        "false_positives": false_positives,
        "status": "PASS" if false_positives == 0 else "FAIL"
    }
    print(f"  - Micro-Jitter (100 frames): False Positives = {false_positives} [{jitter_results['micro_jitter_100_frames']['status']}]")

    # Missing frames reacquisition
    tracker = ObjectTracker(max_missing_frames=5, distance_threshold=60.0)
    tracker.update([Detection(25, "package", 0.9, (100, 100, 150, 150))], 0)
    for f in range(1, 4): tracker.update([], f)
    t_reacq = tracker.update([Detection(25, "package", 0.88, (120, 110, 170, 160))], 4)
    reacquired = len(t_reacq) == 1 and t_reacq[0].object_id == 1
    jitter_results["missing_frames_reacquisition"] = {
        "reacquired": reacquired,
        "status": "PASS" if reacquired else "FAIL"
    }
    print(f"  - Missing Frames Reacquisition (3 dropped frames): Success={reacquired} [{jitter_results['missing_frames_reacquisition']['status']}]")
    results["benchmarks"]["temporal_jitter"] = jitter_results

    # -------------------------------------------------------------
    # 5. All 10 Detectors Deterministic Accuracy & Verification
    # -------------------------------------------------------------
    print("\n[Benchmark 5] All 10 Temporal Behaviour Detectors Verification...")
    detector_suite = [
        ("product_drop", DropDetector(), [
            TrackedObject(1, "package", (180, 180, 220, 220), (200, 200), velocity=(0, 20),
                          trajectory=[(200, 50), (200, 100), (200, 150), (200, 200)])
        ]),
        ("product_dragging", DragDetector(), [
            TrackedObject(2, "package", (200, 380, 260, 420), (230, 400), velocity=(12, 0),
                          trajectory=[(float(100 + i * 15), 400.0) for i in range(10)])
        ]),
        ("product_throwing", ThrowDetector(), [
            TrackedObject(3, "carton", (100, 100, 150, 150), (125, 125), velocity=(15, -6),
                          trajectory=[(50, 180), (75, 140), (100, 120), (125, 125)])
        ]),
        ("rough_handling", RoughHandlingDetector(), [
            TrackedObject(4, "package", (100, 100, 150, 150), (125, 125), velocity=(10, 5), acceleration=(8, 7),
                          trajectory=[(100, 100), (130, 110), (100, 125), (135, 135)])
        ]),
        ("improper_stacking", StackingDetector(), [
            TrackedObject(5, "package", (100, 100, 260, 180), (180, 140)),
            TrackedObject(6, "package", (130, 180, 210, 240), (170, 210))
        ]),
        ("unstable_stacking", UnstableStackDetector(), [
            TrackedObject(7, "package", (100, 50, 140, 250), (120, 150), trajectory=[(120, 150)] * 5)
        ]),
        ("product_outside_zone", ZoneDetector(), [
            TrackedObject(8, "package", (10, 10, 40, 40), (25, 25))
        ]),
        ("incorrect_pallet_position", PalletDetector(), [
            TrackedObject(9, "pallet", (200, 300, 350, 350), (275, 325)),
            TrackedObject(10, "package", (150, 220, 400, 300), (275, 260))
        ]),
        ("unsafe_loading_sequence", LoadingSequenceDetector(), [
            TrackedObject(20 + i, "package", (100 + i * 80, 200, 150 + i * 80, 250), (125 + i * 80, 225), velocity=(4, 0))
            for i in range(5)
        ]),
        ("improper_handling_equipment", EquipmentDetector(), [
            TrackedObject(30, "package", (100, 100, 280, 280), (190, 190), velocity=(3, 0),
                          trajectory=[(180, 190), (185, 190), (190, 190)])
        ]),
    ]

    detector_results = {}
    for b_name, det, objs in detector_suite:
        evs = det.analyze(objs, frame_idx=1, frame_shape=(720, 1280))
        matched = len(evs) >= 1 and evs[0].event_type == b_name
        detector_results[b_name] = {
            "triggered": len(evs) >= 1,
            "event_type": evs[0].event_type if evs else None,
            "confidence": evs[0].confidence if evs else None,
            "evidence_keys": list(evs[0].evidence.keys()) if evs else [],
            "status": "PASS" if matched else "FAIL"
        }
        status_tag = detector_results[b_name]["status"]
        print(f"  - Detector [{b_name:28s}]: Triggered={len(evs)} | Conf={evs[0].confidence if evs else 0.0} [{status_tag}]")

    results["benchmarks"]["detectors_verification"] = detector_results

    # -------------------------------------------------------------
    # Overall Summary
    # -------------------------------------------------------------
    all_statuses = []
    for category in results["benchmarks"].values():
        for item in category.values():
            if isinstance(item, dict) and "status" in item:
                all_statuses.append(item["status"])

    passed = all_statuses.count("PASS")
    failed = all_statuses.count("FAIL")
    verdict = "APPROVE" if failed == 0 else "REQUEST_CHANGES"

    results["summary"] = {
        "total_stress_checks": len(all_statuses),
        "passed_checks": passed,
        "failed_checks": failed,
        "pass_rate_pct": round((passed / len(all_statuses)) * 100.0, 1) if all_statuses else 0.0,
        "verdict": verdict
    }

    print("\n" + "=" * 70)
    print(f"SUMMARY: {passed}/{len(all_statuses)} Checks Passed ({results['summary']['pass_rate_pct']}%) | Verdict: {verdict}")
    print("=" * 70)

    # Write output to JSON in challenger working directory
    out_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".agents", "challenger1_m5"))
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, "benchmark_results.json")
    with open(out_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Benchmark metrics written to {out_file}")

    return results


if __name__ == "__main__":
    run_all_benchmarks()
