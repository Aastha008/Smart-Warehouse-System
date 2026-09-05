from typing import List, Tuple, Dict, Any, Optional
from datetime import datetime
import numpy as np
from backend.behaviour.base_detector import BaseBehaviourDetector, BehaviourEvent
from backend.vision.tracker import TrackedObject

class RoughHandlingDetector(BaseBehaviourDetector):
    behaviour_type = "rough_handling"

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.behaviour_type = "rough_handling"
        cfg = self.config.get("behaviours", {}).get("rough_handling", self.config)
        self.acceleration_threshold = cfg.get("acceleration_threshold", 3.0)
        self.min_confidence = cfg.get("min_confidence", 0.55)
        self.reported_tracks = set()

    def analyze(self, tracked_objects: List[TrackedObject], frame_idx: int, frame_shape: Tuple[int, int]) -> List[BehaviourEvent]:
        events = []
        target_classes = {"package", "carton", "box", "bottle"}

        for obj in tracked_objects:
            if obj.class_name not in target_classes:
                continue
            if obj.object_id in self.reported_tracks:
                continue

            accel_mag = float(np.sqrt(obj.acceleration[0]**2 + obj.acceleration[1]**2))
            
            # Jerk and direction change calculation on recent trajectory window
            direction_changes = 0
            if len(obj.trajectory) >= 4:
                start_idx = max(2, len(obj.trajectory) - 20)
                for i in range(start_idx, len(obj.trajectory)):
                    v1 = (obj.trajectory[i-1][0] - obj.trajectory[i-2][0], obj.trajectory[i-1][1] - obj.trajectory[i-2][1])
                    v2 = (obj.trajectory[i][0] - obj.trajectory[i-1][0], obj.trajectory[i][1] - obj.trajectory[i-1][1])
                    m1 = np.hypot(v1[0], v1[1])
                    m2 = np.hypot(v2[0], v2[1])
                    if m1 > 1.0 and m2 > 1.0:
                        cos_angle = np.clip((v1[0]*v2[0] + v1[1]*v2[1]) / (m1 * m2), -1.0, 1.0)
                        angle_deg = np.degrees(np.arccos(cos_angle))
                        if angle_deg > 40:
                            direction_changes += 1

            if accel_mag >= self.acceleration_threshold or direction_changes >= 2 or accel_mag > 10.0:
                confidence = min(0.95, max(self.min_confidence, 0.6 + (accel_mag / 20.0) * 0.3))
                events.append(BehaviourEvent(
                    event_type="rough_handling",
                    object_id=obj.object_id,
                    timestamp=datetime.now().strftime("%H:%M:%S"),
                    frame_idx=frame_idx,
                    confidence=round(confidence, 2),
                    location="loading_bay_1",
                    evidence={
                        "acceleration": round(accel_mag, 2),
                        "direction_changes": direction_changes,
                        "ax": round(float(obj.acceleration[0]), 2),
                        "ay": round(float(obj.acceleration[1]), 2),
                        "class_name": obj.class_name
                    }
                ))
                self.reported_tracks.add(obj.object_id)

        return events
