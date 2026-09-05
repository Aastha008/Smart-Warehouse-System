from typing import List, Tuple, Dict, Any, Optional
from datetime import datetime
import numpy as np
from backend.behaviour.base_detector import BaseBehaviourDetector, BehaviourEvent
from backend.vision.tracker import TrackedObject

class ThrowDetector(BaseBehaviourDetector):
    behaviour_type = "product_throwing"

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.behaviour_type = "product_throwing"
        cfg = self.config.get("behaviours", {}).get("product_throwing", self.config)
        self.min_release_velocity = cfg.get("min_release_velocity", 4.0)
        self.high_arc_threshold = cfg.get("high_arc_threshold", 20.0)
        self.min_confidence = cfg.get("min_confidence", 0.65)
        self.reported_tracks = set()

    def analyze(self, tracked_objects: List[TrackedObject], frame_idx: int, frame_shape: Tuple[int, int]) -> List[BehaviourEvent]:
        events = []
        target_classes = {"package", "carton", "bottle", "box"}

        for obj in tracked_objects:
            if obj.class_name not in target_classes:
                continue
            if obj.object_id in self.reported_tracks:
                continue

            v_mag = float(np.sqrt(obj.velocity[0]**2 + obj.velocity[1]**2))
            
            # Check trajectory arc or high release speed
            is_high_speed = v_mag >= self.min_release_velocity
            is_upward_or_lateral = obj.velocity[1] < -1.0 or abs(obj.velocity[0]) >= self.min_release_velocity * 0.8
            
            # Parabolic arc check on trajectory
            has_arc = False
            arc_height = 0.0
            if len(obj.trajectory) >= 4:
                ys = [pt[1] for pt in obj.trajectory[-6:]]
                min_y = min(ys)
                arc_height = max(ys[0], ys[-1]) - min_y
                if arc_height >= self.high_arc_threshold * 0.5 and ys[0] > min_y and ys[-1] > min_y:
                    has_arc = True

            if (is_high_speed and is_upward_or_lateral) or has_arc or v_mag > 15.0:
                confidence = min(0.98, max(self.min_confidence, 0.7 + (v_mag / 30.0) * 0.25))
                events.append(BehaviourEvent(
                    event_type="product_throwing",
                    object_id=obj.object_id,
                    timestamp=datetime.now().strftime("%H:%M:%S"),
                    frame_idx=frame_idx,
                    confidence=round(confidence, 2),
                    location="loading_bay_1",
                    evidence={
                        "velocity_magnitude": round(v_mag, 2),
                        "velocity": round(v_mag, 2),
                        "vx": round(float(obj.velocity[0]), 2),
                        "vy": round(float(obj.velocity[1]), 2),
                        "arc_height_px": round(float(arc_height), 1),
                        "class_name": obj.class_name
                    }
                ))
                self.reported_tracks.add(obj.object_id)

        return events
