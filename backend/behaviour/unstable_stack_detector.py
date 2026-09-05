from typing import List, Tuple, Dict, Any, Optional
from datetime import datetime
import numpy as np
from backend.behaviour.base_detector import BaseBehaviourDetector, BehaviourEvent
from backend.vision.tracker import TrackedObject

class UnstableStackDetector(BaseBehaviourDetector):
    behaviour_type = "unstable_stacking"

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.behaviour_type = "unstable_stacking"
        cfg = self.config.get("behaviours", {}).get("unstable_stacking", self.config)
        self.tilt_angle_threshold = cfg.get("tilt_angle_threshold", 10.0)
        self.oscillation_threshold = cfg.get("oscillation_threshold", 4.0)
        self.min_confidence = cfg.get("min_confidence", 0.6)
        self.reported_tracks = set()

    def analyze(self, tracked_objects: List[TrackedObject], frame_idx: int, frame_shape: Tuple[int, int]) -> List[BehaviourEvent]:
        events = []
        target_classes = {"package", "carton", "box"}

        for obj in tracked_objects:
            if obj.class_name not in target_classes:
                continue
            if obj.object_id in self.reported_tracks:
                continue

            w = max(1.0, float(obj.bbox[2] - obj.bbox[0]))
            h = max(1.0, float(obj.bbox[3] - obj.bbox[1]))
            aspect_ratio = h / w

            # Wobble / oscillation across trajectory
            oscillation_std = 0.0
            if len(obj.trajectory) >= 5:
                xs = [pt[0] for pt in obj.trajectory[-10:]]
                oscillation_std = float(np.std(xs))

            # Tall tower aspect ratio (> 2.5) or significant wobble
            if aspect_ratio >= 2.4 or oscillation_std >= self.oscillation_threshold:
                tilt_est = min(45.0, (aspect_ratio - 1.5) * 8.0) if aspect_ratio > 1.5 else 0.0
                confidence = min(0.92, max(self.min_confidence, 0.6 + min(aspect_ratio / 5.0, 0.3)))
                events.append(BehaviourEvent(
                    event_type="unstable_stacking",
                    object_id=obj.object_id,
                    timestamp=datetime.now().strftime("%H:%M:%S"),
                    frame_idx=frame_idx,
                    confidence=round(confidence, 2),
                    location="loading_bay_1",
                    evidence={
                        "aspect_ratio": round(aspect_ratio, 2),
                        "tilt_angle_deg": round(tilt_est, 1),
                        "oscillation_amplitude": round(oscillation_std, 2),
                        "class_name": obj.class_name
                    }
                ))
                self.reported_tracks.add(obj.object_id)

        return events
