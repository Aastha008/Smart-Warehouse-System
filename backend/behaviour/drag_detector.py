from typing import List, Tuple, Dict, Any, Optional
from datetime import datetime
from backend.behaviour.base_detector import BaseBehaviourDetector, BehaviourEvent
from backend.vision.tracker import TrackedObject

class DragDetector(BaseBehaviourDetector):
    behaviour_type = "product_dragging"

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.behaviour_type = "product_dragging"
        cfg = self.config.get("behaviours", {}).get("product_dragging", self.config)
        self.min_drag_distance = cfg.get("min_drag_distance", 50.0)
        self.max_lift_height = cfg.get("max_lift_height", 25.0)
        self.min_drag_frames = cfg.get("min_drag_frames", 5)
        self.min_confidence = cfg.get("min_confidence", 0.6)
        self.reported_tracks = set()

    def analyze(self, tracked_objects: List[TrackedObject], frame_idx: int, frame_shape: Tuple[int, int]) -> List[BehaviourEvent]:
        events = []
        target_classes = {"package", "carton", "box"}

        for obj in tracked_objects:
            if obj.class_name not in target_classes:
                continue
            if len(obj.trajectory) < min(self.min_drag_frames, 5):
                continue
            if obj.object_id in self.reported_tracks:
                continue

            # Compute floor displacement over track window (accounting for CCTV perspective angle)
            k = min(len(obj.trajectory), 20)
            start_pt = obj.trajectory[-k]
            end_pt = obj.trajectory[-1]
            
            dx = abs(end_pt[0] - start_pt[0])
            dy = abs(end_pt[1] - start_pt[1])
            drag_distance = (dx ** 2 + dy ** 2) ** 0.5
            
            # Object is in dock floor / transit area and moving continuously across floor plane
            h, w = frame_shape[:2]
            current_y = end_pt[1]
            is_near_floor = current_y >= h * 0.35
            
            # Dragging occurs horizontally, diagonally, or towards camera along dock floor
            if drag_distance >= self.min_drag_distance and is_near_floor:
                confidence = min(0.95, max(self.min_confidence, 0.65 + (drag_distance / 150.0) * 0.3))
                events.append(BehaviourEvent(
                    event_type="product_dragging",
                    object_id=obj.object_id,
                    timestamp=datetime.now().strftime("%H:%M:%S"),
                    frame_idx=frame_idx,
                    confidence=round(confidence, 2),
                    location="loading_bay_1",
                    evidence={
                        "drag_distance_px": round(float(drag_distance), 1),
                        "dx": round(float(dx), 1),
                        "dy": round(float(dy), 1),
                        "class_name": obj.class_name,
                        "motion_type": "floor_drag_perspective"
                    }
                ))
                self.reported_tracks.add(obj.object_id)

        return events
