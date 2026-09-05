import os
import sys
import json
import base64

PROJECT_ROOT = r"C:\Users\hp\.gemini\antigravity\scratch\ai-warehouse-intelligence"
os.makedirs(os.path.join(PROJECT_ROOT, "scripts"), exist_ok=True)
os.makedirs(os.path.join(PROJECT_ROOT, "demo"), exist_ok=True)
os.makedirs(os.path.join(PROJECT_ROOT, "tests", "integration"), exist_ok=True)
os.makedirs(os.path.join(PROJECT_ROOT, "docs"), exist_ok=True)

print("Scaffolding directories ready.")

files["backend/vision/__init__.py"] = ""

files["backend/vision/detector.py"] = """
import yaml
import torch
import numpy as np
from dataclasses import dataclass
from typing import List, Dict, Any, Tuple
try:
    from ultralytics import YOLO
except ImportError:
    # Fallback/Mock for testing without ultralytics
    class YOLO:
        def __init__(self, model): pass
        def __call__(self, frame, verbose=False): return []
        def to(self, device): pass

@dataclass
class Detection:
    class_id: int
    class_name: str
    confidence: float
    bbox: Tuple[float, float, float, float] # x1, y1, x2, y2

class WarehouseDetector:
    def __init__(self, config_path: str = "configs/detection.yaml"):
        self.config_path = config_path
        self.config = self._load_config()
        model_path = self.config.get("model_path", "yolov8s.pt")
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.model = YOLO(model_path)
        if hasattr(self.model, 'to'):
            self.model.to(self.device)
        self.conf_threshold = self.config.get("conf_threshold", 0.3)
        self.iou_threshold = self.config.get("iou_threshold", 0.45)
        # Map COCO to Warehouse classes
        self.class_mapping = {
            0: "person",
            2: "vehicle", # car -> forklift approximation
            7: "vehicle", # truck -> forklift approximation
            39: "bottle", # approximation for some items
            41: "cup",
            63: "laptop",
            67: "cell phone",
            # We treat generic objects like boxes
            # in a real setup we would train a custom model
        }

    def _load_config(self) -> Dict[str, Any]:
        try:
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f) or {}
        except FileNotFoundError:
            return {}

    def detect(self, frame: np.ndarray) -> List[Detection]:
        results = self.model(frame, verbose=False, conf=self.conf_threshold, iou=self.iou_threshold)
        detections = []
        if not results: return []
        result = results[0]
        if result.boxes is None: return []
        for box in result.boxes:
            cls_id = int(box.cls[0].item())
            conf = float(box.conf[0].item())
            xyxy = box.xyxy[0].tolist()
            class_name = self.class_mapping.get(cls_id, "package") # default to package
            
            detections.append(Detection(
                class_id=cls_id,
                class_name=class_name,
                confidence=conf,
                bbox=(xyxy[0], xyxy[1], xyxy[2], xyxy[3])
            ))
        return detections
"""

files["backend/vision/tracker.py"] = """
import numpy as np
from dataclasses import dataclass, field
from typing import List, Tuple, Dict
from backend.vision.detector import Detection
import time

@dataclass
class TrackedObject:
    object_id: int
    class_name: str
    bbox: Tuple[float, float, float, float]
    center: Tuple[float, float]
    velocity: Tuple[float, float] = (0.0, 0.0)
    acceleration: Tuple[float, float] = (0.0, 0.0)
    trajectory: List[Tuple[float, float]] = field(default_factory=list)
    timestamp: float = 0.0
    confidence: float = 0.0
    last_updated: int = 0
    missing_frames: int = 0

class ObjectTracker:
    def __init__(self, max_missing_frames: int = 5, distance_threshold: float = 50.0):
        self.max_missing_frames = max_missing_frames
        self.distance_threshold = distance_threshold
        self.tracks: Dict[int, TrackedObject] = {}
        self.next_id = 1
    
    def _compute_center(self, bbox: Tuple[float, float, float, float]) -> Tuple[float, float]:
        return ((bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2)
        
    def _compute_distance(self, c1: Tuple[float, float], c2: Tuple[float, float]) -> float:
        return np.sqrt((c1[0] - c2[0])**2 + (c1[1] - c2[1])**2)

    def update(self, detections: List[Detection], frame_idx: int) -> List[TrackedObject]:
        current_centers = [self._compute_center(d.bbox) for d in detections]
        
        # Simple Greedy Matching (Replace with Hungarian algorithm for prod)
        matched_detections = set()
        matched_tracks = set()
        
        for t_id, track in self.tracks.items():
            if track.missing_frames >= self.max_missing_frames:
                continue
                
            best_match_idx = -1
            best_dist = float('inf')
            
            for d_idx, d in enumerate(detections):
                if d_idx in matched_detections: continue
                if d.class_name != track.class_name: continue
                
                dist = self._compute_distance(track.center, current_centers[d_idx])
                if dist < best_dist and dist < self.distance_threshold:
                    best_dist = dist
                    best_match_idx = d_idx
            
            if best_match_idx != -1:
                # Update track
                d = detections[best_match_idx]
                new_center = current_centers[best_match_idx]
                
                # Update velocity/acceleration
                dt = 1.0 # Assuming constant framerate for simple velocity
                vx = new_center[0] - track.center[0]
                vy = new_center[1] - track.center[1]
                
                ax = vx - track.velocity[0]
                ay = vy - track.velocity[1]
                
                track.bbox = d.bbox
                track.center = new_center
                track.velocity = (vx, vy)
                track.acceleration = (ax, ay)
                track.trajectory.append(new_center)
                if len(track.trajectory) > 50:
                    track.trajectory.pop(0)
                track.confidence = d.confidence
                track.last_updated = frame_idx
                track.missing_frames = 0
                track.timestamp = time.time()
                
                matched_detections.add(best_match_idx)
                matched_tracks.add(t_id)
            else:
                track.missing_frames += 1
                
        # Create new tracks
        for d_idx, d in enumerate(detections):
            if d_idx not in matched_detections:
                center = current_centers[d_idx]
                self.tracks[self.next_id] = TrackedObject(
                    object_id=self.next_id,
                    class_name=d.class_name,
                    bbox=d.bbox,
                    center=center,
                    trajectory=[center],
                    confidence=d.confidence,
                    last_updated=frame_idx,
                    timestamp=time.time()
                )
                self.next_id += 1
                
        # Remove old tracks
        self.tracks = {k: v for k, v in self.tracks.items() if v.missing_frames < self.max_missing_frames}
        
        return list(self.tracks.values())
"""

files["backend/vision/motion.py"] = """
import numpy as np
from typing import List, Dict, Any
from dataclasses import dataclass
from backend.vision.tracker import TrackedObject

@dataclass
class MotionFeatures:
    object_id: int
    avg_velocity: float
    max_velocity: float
    is_dropping: bool
    is_jerky: bool
    horizontal_movement: float
    vertical_movement: float
    total_displacement: float

class MotionAnalyzer:
    def __init__(self):
        pass

    def analyze(self, tracks: List[TrackedObject]) -> Dict[int, MotionFeatures]:
        features = {}
        for track in tracks:
            if len(track.trajectory) < 3:
                features[track.object_id] = MotionFeatures(
                    object_id=track.object_id,
                    avg_velocity=0.0, max_velocity=0.0, is_dropping=False,
                    is_jerky=False, horizontal_movement=0.0, vertical_movement=0.0, total_displacement=0.0
                )
                continue
                
            velocities = []
            for i in range(1, len(track.trajectory)):
                dx = track.trajectory[i][0] - track.trajectory[i-1][0]
                dy = track.trajectory[i][1] - track.trajectory[i-1][1]
                velocities.append(np.sqrt(dx**2 + dy**2))
                
            avg_vel = np.mean(velocities)
            max_vel = np.max(velocities)
            
            start_pos = track.trajectory[0]
            end_pos = track.trajectory[-1]
            dx_total = end_pos[0] - start_pos[0]
            dy_total = end_pos[1] - start_pos[1]
            
            # y goes down in images
            is_dropping = dy_total > 20 and avg_vel > 10 
            
            # Acceleration variance for jerkiness
            accels = [velocities[i] - velocities[i-1] for i in range(1, len(velocities))]
            is_jerky = len(accels) > 0 and np.std(accels) > 5.0
            
            features[track.object_id] = MotionFeatures(
                object_id=track.object_id,
                avg_velocity=float(avg_vel),
                max_velocity=float(max_vel),
                is_dropping=bool(is_dropping),
                is_jerky=bool(is_jerky),
                horizontal_movement=float(abs(dx_total)),
                vertical_movement=float(dy_total),
                total_displacement=float(np.sqrt(dx_total**2 + dy_total**2))
            )
        return features
"""

files["backend/behaviour/__init__.py"] = ""

files["backend/behaviour/base_detector.py"] = """
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass, field
from backend.vision.tracker import TrackedObject

@dataclass
class BehaviourEvent:
    event_type: str
    object_id: int
    timestamp: str
    frame_idx: int
    confidence: float
    location: str
    evidence: Dict[str, Any] = field(default_factory=dict)
    
class BaseBehaviourDetector(ABC):
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}

    @abstractmethod
    def analyze(self, tracked_objects: List[TrackedObject], frame_idx: int, frame_shape: Tuple[int, int]) -> List[BehaviourEvent]:
        pass
"""

files["backend/behaviour/drop_detector.py"] = """
from typing import List, Tuple
from backend.behaviour.base_detector import BaseBehaviourDetector, BehaviourEvent
from backend.vision.tracker import TrackedObject
from datetime import datetime

class DropDetector(BaseBehaviourDetector):
    def analyze(self, tracked_objects: List[TrackedObject], frame_idx: int, frame_shape: Tuple[int, int]) -> List[BehaviourEvent]:
        events = []
        for obj in tracked_objects:
            if obj.class_name not in ["package", "bottle", "laptop", "cell phone"]: continue
            if len(obj.trajectory) < 5: continue
            
            # Check rapid downward movement
            start_y = obj.trajectory[-5][1]
            end_y = obj.trajectory[-1][1]
            drop_height = end_y - start_y
            
            if drop_height > self.config.get("drop_threshold", 50.0):
                events.append(BehaviourEvent(
                    event_type="product_drop",
                    object_id=obj.object_id,
                    timestamp=datetime.now().strftime("%H:%M:%S"),
                    frame_idx=frame_idx,
                    confidence=0.85,
                    location="zone_unknown",
                    evidence={"drop_height_px": drop_height, "velocity": obj.velocity[1]}
                ))
        return events
"""

files["backend/behaviour/drag_detector.py"] = """
from typing import List, Tuple
from backend.behaviour.base_detector import BaseBehaviourDetector, BehaviourEvent
from backend.vision.tracker import TrackedObject
from datetime import datetime

class DragDetector(BaseBehaviourDetector):
    def analyze(self, tracked_objects: List[TrackedObject], frame_idx: int, frame_shape: Tuple[int, int]) -> List[BehaviourEvent]:
        events = []
        for obj in tracked_objects:
            if obj.class_name not in ["package"]: continue
            if len(obj.trajectory) < 10: continue
            
            dx = abs(obj.trajectory[-1][0] - obj.trajectory[-10][0])
            dy = abs(obj.trajectory[-1][1] - obj.trajectory[-10][1])
            
            if dx > self.config.get("drag_x_threshold", 40.0) and dy < self.config.get("drag_y_threshold", 10.0):
                events.append(BehaviourEvent(
                    event_type="product_dragging",
                    object_id=obj.object_id,
                    timestamp=datetime.now().strftime("%H:%M:%S"),
                    frame_idx=frame_idx,
                    confidence=0.8,
                    location="zone_unknown",
                    evidence={"dx": dx, "dy": dy}
                ))
        return events
"""

files["backend/behaviour/throw_detector.py"] = """
from typing import List, Tuple
from backend.behaviour.base_detector import BaseBehaviourDetector, BehaviourEvent
from backend.vision.tracker import TrackedObject
from datetime import datetime
import numpy as np

class ThrowDetector(BaseBehaviourDetector):
    def analyze(self, tracked_objects: List[TrackedObject], frame_idx: int, frame_shape: Tuple[int, int]) -> List[BehaviourEvent]:
        events = []
        for obj in tracked_objects:
            if obj.class_name not in ["package", "bottle"]: continue
            if len(obj.trajectory) < 5: continue
            
            v_mag = np.sqrt(obj.velocity[0]**2 + obj.velocity[1]**2)
            if v_mag > self.config.get("throw_velocity", 30.0) and obj.velocity[1] < 0: # moving up and fast
                events.append(BehaviourEvent(
                    event_type="product_throwing",
                    object_id=obj.object_id,
                    timestamp=datetime.now().strftime("%H:%M:%S"),
                    frame_idx=frame_idx,
                    confidence=0.9,
                    location="zone_unknown",
                    evidence={"velocity_magnitude": v_mag}
                ))
        return events
"""

files["backend/behaviour/rough_handling_detector.py"] = """
from typing import List, Tuple
from backend.behaviour.base_detector import BaseBehaviourDetector, BehaviourEvent
from backend.vision.tracker import TrackedObject
from datetime import datetime
import numpy as np

class RoughHandlingDetector(BaseBehaviourDetector):
    def analyze(self, tracked_objects: List[TrackedObject], frame_idx: int, frame_shape: Tuple[int, int]) -> List[BehaviourEvent]:
        events = []
        for obj in tracked_objects:
            if obj.class_name not in ["package"]: continue
            
            accel_mag = np.sqrt(obj.acceleration[0]**2 + obj.acceleration[1]**2)
            if accel_mag > self.config.get("jerk_threshold", 15.0):
                events.append(BehaviourEvent(
                    event_type="rough_handling",
                    object_id=obj.object_id,
                    timestamp=datetime.now().strftime("%H:%M:%S"),
                    frame_idx=frame_idx,
                    confidence=0.75,
                    location="zone_unknown",
                    evidence={"acceleration": accel_mag}
                ))
        return events
"""

files["backend/behaviour/stacking_detector.py"] = """
from typing import List, Tuple
from backend.behaviour.base_detector import BaseBehaviourDetector, BehaviourEvent
from backend.vision.tracker import TrackedObject
from datetime import datetime

class StackingDetector(BaseBehaviourDetector):
    def analyze(self, tracked_objects: List[TrackedObject], frame_idx: int, frame_shape: Tuple[int, int]) -> List[BehaviourEvent]:
        events = []
        packages = [obj for obj in tracked_objects if obj.class_name == "package"]
        for i, p1 in enumerate(packages):
            for j, p2 in enumerate(packages):
                if i == j: continue
                
                # Check if p1 is directly on top of p2
                p1_w = p1.bbox[2] - p1.bbox[0]
                p2_w = p2.bbox[2] - p2.bbox[0]
                
                is_above = (p1.bbox[3] > p2.bbox[1] - 10) and (p1.bbox[3] < p2.bbox[1] + 10)
                is_centered = (p1.center[0] > p2.bbox[0]) and (p1.center[0] < p2.bbox[2])
                
                if is_above and is_centered and p1_w > p2_w * 1.2:
                    events.append(BehaviourEvent(
                        event_type="improper_stacking",
                        object_id=p1.object_id,
                        timestamp=datetime.now().strftime("%H:%M:%S"),
                        frame_idx=frame_idx,
                        confidence=0.85,
                        location="zone_unknown",
                        evidence={"top_width": p1_w, "bottom_width": p2_w}
                    ))
        return events
"""

files["backend/behaviour/unstable_stack_detector.py"] = """
from typing import List, Tuple
from backend.behaviour.base_detector import BaseBehaviourDetector, BehaviourEvent
from backend.vision.tracker import TrackedObject
from datetime import datetime

class UnstableStackDetector(BaseBehaviourDetector):
    def analyze(self, tracked_objects: List[TrackedObject], frame_idx: int, frame_shape: Tuple[int, int]) -> List[BehaviourEvent]:
        events = []
        # Simplified: Check if bounding box ratio is highly skewed or tilted (difficult with pure ax-aligned bboxes, fallback to aspect ratio variation)
        for obj in tracked_objects:
            if obj.class_name != "package": continue
            w = obj.bbox[2] - obj.bbox[0]
            h = obj.bbox[3] - obj.bbox[1]
            if w == 0 or h == 0: continue
            if h/w > 3.0: # Very tall and thin, potentially unstable
                 events.append(BehaviourEvent(
                    event_type="unstable_stacking",
                    object_id=obj.object_id,
                    timestamp=datetime.now().strftime("%H:%M:%S"),
                    frame_idx=frame_idx,
                    confidence=0.6,
                    location="zone_unknown",
                    evidence={"aspect_ratio": h/w}
                ))
        return events
"""

files["backend/behaviour/zone_detector.py"] = """
from typing import List, Tuple
from backend.behaviour.base_detector import BaseBehaviourDetector, BehaviourEvent
from backend.vision.tracker import TrackedObject
from datetime import datetime

class ZoneDetector(BaseBehaviourDetector):
    def analyze(self, tracked_objects: List[TrackedObject], frame_idx: int, frame_shape: Tuple[int, int]) -> List[BehaviourEvent]:
        events = []
        for obj in tracked_objects:
            if obj.class_name == "person":
                # Mock zone check: if person is too far right, assume unauthorized
                if obj.center[0] > frame_shape[1] * 0.9:
                    events.append(BehaviourEvent(
                        event_type="product_outside_zone", # adapting the name
                        object_id=obj.object_id,
                        timestamp=datetime.now().strftime("%H:%M:%S"),
                        frame_idx=frame_idx,
                        confidence=0.8,
                        location="restricted_zone",
                        evidence={"x_pos": obj.center[0]}
                    ))
        return events
"""

files["backend/behaviour/pallet_detector.py"] = """
from typing import List, Tuple
from backend.behaviour.base_detector import BaseBehaviourDetector, BehaviourEvent
from backend.vision.tracker import TrackedObject
from datetime import datetime

class PalletDetector(BaseBehaviourDetector):
    def analyze(self, tracked_objects: List[TrackedObject], frame_idx: int, frame_shape: Tuple[int, int]) -> List[BehaviourEvent]:
        # Placeholder for incorrect_pallet_position
        events = []
        return events
"""

files["backend/behaviour/loading_sequence_detector.py"] = """
from typing import List, Tuple
from backend.behaviour.base_detector import BaseBehaviourDetector, BehaviourEvent
from backend.vision.tracker import TrackedObject
from datetime import datetime

class LoadingSequenceDetector(BaseBehaviourDetector):
    def analyze(self, tracked_objects: List[TrackedObject], frame_idx: int, frame_shape: Tuple[int, int]) -> List[BehaviourEvent]:
        # Placeholder for unsafe_loading_sequence
        return []
"""

files["backend/behaviour/equipment_detector.py"] = """
from typing import List, Tuple
from backend.behaviour.base_detector import BaseBehaviourDetector, BehaviourEvent
from backend.vision.tracker import TrackedObject
from datetime import datetime

class EquipmentDetector(BaseBehaviourDetector):
    def analyze(self, tracked_objects: List[TrackedObject], frame_idx: int, frame_shape: Tuple[int, int]) -> List[BehaviourEvent]:
        return []
"""

files["backend/behaviour/behaviour_engine.py"] = """
from typing import List, Tuple, Dict, Any
from backend.vision.tracker import TrackedObject
from backend.behaviour.base_detector import BehaviourEvent
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

class BehaviourEngine:
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.detectors = [
            DropDetector(self.config),
            DragDetector(self.config),
            ThrowDetector(self.config),
            RoughHandlingDetector(self.config),
            StackingDetector(self.config),
            UnstableStackDetector(self.config),
            ZoneDetector(self.config),
            PalletDetector(self.config),
            LoadingSequenceDetector(self.config),
            EquipmentDetector(self.config)
        ]
        
    def analyze(self, tracked_objects: List[TrackedObject], frame_idx: int, frame_shape: Tuple[int, int]) -> List[BehaviourEvent]:
        all_events = []
        for detector in self.detectors:
            events = detector.analyze(tracked_objects, frame_idx, frame_shape)
            all_events.extend(events)
            
        # Basic deduplication
        deduped = []
        seen = set()
        for e in all_events:
            key = f"{e.event_type}_{e.object_id}"
            if key not in seen:
                seen.add(key)
                deduped.append(e)
                
        return deduped
"""

files["backend/risk/__init__.py"] = ""

files["backend/risk/risk_explanation.py"] = """
from typing import Dict, Any

def generate_explanation(event_type: str, evidence: Dict[str, Any], risk_level: str) -> str:
    explanations = {
        "product_drop": "Product experienced a rapid downward acceleration indicative of a fall.",
        "product_dragging": "Product moved horizontally without sufficient vertical clearance.",
        "product_throwing": "Product exhibited high velocity and parabolic trajectory.",
        "rough_handling": "Product subjected to rapid changes in acceleration (jerking).",
        "improper_stacking": "A larger item was placed atop a significantly smaller item.",
        "unstable_stacking": "Stacked items exhibited unstable geometry or aspect ratios.",
        "product_outside_zone": "Item detected in an unauthorized or restricted area.",
        "incorrect_pallet_position": "Pallet misaligned or items overhanging.",
        "unsafe_loading_sequence": "Multiple concurrent heavy item movements detected.",
        "improper_handling_equipment": "Large item moved manually without suitable equipment."
    }
    
    base = explanations.get(event_type, "Unusual behavior detected.")
    return f"{base} This is a potential damage-causing event. Evidence: {evidence}"

def generate_recommendation(event_type: str) -> str:
    return "Inspect product for potential damage and review handling procedures with personnel."
"""

files["backend/risk/risk_engine.py"] = """
import yaml
from typing import Dict, Any
from dataclasses import dataclass
from backend.behaviour.base_detector import BehaviourEvent
from backend.risk.risk_explanation import generate_explanation, generate_recommendation

@dataclass
class RiskAssessment:
    level: str
    score: int
    explanation: str
    recommendation: str
    
class RiskEngine:
    def __init__(self, config_path: str = "configs/risk.yaml"):
        self.config_path = config_path
        self.config = self._load_config()
        self.base_scores = {
            "product_drop": 80,
            "product_dragging": 40,
            "product_throwing": 90,
            "rough_handling": 60,
            "improper_stacking": 50,
            "unstable_stacking": 70,
            "product_outside_zone": 30,
            "incorrect_pallet_position": 40,
            "unsafe_loading_sequence": 60,
            "improper_handling_equipment": 70
        }
        
    def _load_config(self) -> Dict[str, Any]:
        try:
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f) or {}
        except FileNotFoundError:
            return {}

    def classify_risk(self, event: BehaviourEvent) -> RiskAssessment:
        score = self.base_scores.get(event.event_type, 10)
        
        # Modifiers based on confidence
        score = int(score * event.confidence)
        
        if score >= 75:
            level = "HIGH"
        elif score >= 40:
            level = "MEDIUM"
        else:
            level = "LOW"
            
        explanation = generate_explanation(event.event_type, event.evidence, level)
        recommendation = generate_recommendation(event.event_type)
        
        return RiskAssessment(
            level=level,
            score=score,
            explanation=explanation,
            recommendation=recommendation
        )
"""

files["backend/vision/annotator.py"] = """
import cv2
import numpy as np
from typing import List
from backend.vision.tracker import TrackedObject
from backend.behaviour.base_detector import BehaviourEvent
from backend.risk.risk_engine import RiskAssessment

class Annotator:
    def __init__(self):
        self.colors = {
            "LOW": (0, 255, 0),
            "MEDIUM": (0, 165, 255), # Orange
            "HIGH": (0, 0, 255) # Red
        }
        
    def annotate(self, frame: np.ndarray, tracks: List[TrackedObject], events: List[BehaviourEvent], assessments: List[RiskAssessment]) -> np.ndarray:
        out_frame = frame.copy()
        
        # Draw tracks
        for t in tracks:
            x1, y1, x2, y2 = map(int, t.bbox)
            cv2.rectangle(out_frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
            cv2.putText(out_frame, f"ID:{t.object_id} {t.class_name}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
            
            # Draw trajectory
            if len(t.trajectory) > 1:
                pts = np.array(t.trajectory, np.int32)
                pts = pts.reshape((-1, 1, 2))
                cv2.polylines(out_frame, [pts], False, (255, 255, 0), 1)
                
        # Draw events
        event_dict = {e.object_id: (e, a) for e, a in zip(events, assessments)}
        for t in tracks:
            if t.object_id in event_dict:
                e, a = event_dict[t.object_id]
                x1, y1, x2, y2 = map(int, t.bbox)
                color = self.colors.get(a.level, (255, 255, 255))
                cv2.rectangle(out_frame, (x1, y1), (x2, y2), color, 4)
                cv2.putText(out_frame, f"ALERT: {e.event_type}", (x1, y2 + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                
        return out_frame
"""

files["backend/vision/pipeline.py"] = """
import cv2
from typing import List, Dict, Any
from dataclasses import dataclass
from backend.vision.detector import WarehouseDetector
from backend.vision.tracker import ObjectTracker
from backend.vision.motion import MotionAnalyzer
from backend.behaviour.behaviour_engine import BehaviourEngine
from backend.risk.risk_engine import RiskEngine
from backend.vision.annotator import Annotator

@dataclass
class FrameResult:
    frame_idx: int
    annotated_frame: Any
    events: List[Any]
    assessments: List[Any]

@dataclass
class AnalysisResult:
    total_frames: int
    events: List[Dict[str, Any]]

class VideoPipeline:
    def __init__(self, skip_frames: int = 2):
        self.skip_frames = skip_frames
        self.detector = WarehouseDetector()
        self.tracker = ObjectTracker()
        self.motion = MotionAnalyzer()
        self.behaviour = BehaviourEngine()
        self.risk = RiskEngine()
        self.annotator = Annotator()
        
    def process_frame(self, frame, frame_idx: int) -> FrameResult:
        detections = self.detector.detect(frame)
        tracks = self.tracker.update(detections, frame_idx)
        # self.motion.analyze(tracks) # updates internal state if needed, not strictly req for return
        
        events = self.behaviour.analyze(tracks, frame_idx, frame.shape)
        assessments = [self.risk.classify_risk(e) for e in events]
        
        annotated_frame = self.annotator.annotate(frame, tracks, events, assessments)
        
        return FrameResult(
            frame_idx=frame_idx,
            annotated_frame=annotated_frame,
            events=events,
            assessments=assessments
        )

    def process_video(self, video_path: str, output_path: str = None) -> AnalysisResult:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Could not open video {video_path}")
            
        frame_idx = 0
        all_events = []
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret: break
            
            if frame_idx % self.skip_frames == 0:
                result = self.process_frame(frame, frame_idx)
                for e, a in zip(result.events, result.assessments):
                    all_events.append({
                        "event_type": e.event_type,
                        "object_id": e.object_id,
                        "timestamp": e.timestamp,
                        "frame_idx": e.frame_idx,
                        "confidence": e.confidence,
                        "location": e.location,
                        "risk_level": a.level,
                        "evidence": e.evidence,
                        "explanation": a.explanation,
                        "recommendation": a.recommendation
                    })
                    
            frame_idx += 1
            
        cap.release()
        return AnalysisResult(total_frames=frame_idx, events=all_events)
"""

for filepath, content in files.items():
    with open(os.path.join(PROJECT_ROOT, filepath), "w", encoding='utf-8') as f:
        f.write(content)

print("Pipeline created successfully.")
