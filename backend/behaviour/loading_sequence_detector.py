from typing import List, Tuple, Dict, Any, Optional
from datetime import datetime
import numpy as np
from backend.behaviour.base_detector import BaseBehaviourDetector, BehaviourEvent
from backend.vision.tracker import TrackedObject

class LoadingSequenceDetector(BaseBehaviourDetector):
    behaviour_type = "unsafe_loading_sequence"

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.behaviour_type = "unsafe_loading_sequence"
        cfg = self.config.get("behaviours", {}).get("unsafe_loading_sequence", self.config)
        self.max_simultaneous_loads = cfg.get("max_simultaneous_loads", 3)
        self.min_clearance = cfg.get("min_clearance", 30.0)
        self.min_confidence = cfg.get("min_confidence", 0.55)
        self.reported_events = set()

    def analyze(self, tracked_objects: List[TrackedObject], frame_idx: int, frame_shape: Tuple[int, int]) -> List[BehaviourEvent]:
        events = []
        target_classes = {"package", "carton", "box", "pallet"}
        packages = [obj for obj in tracked_objects if obj.class_name in target_classes]

        # 1. Check for too many simultaneously moving items in loading area
        moving_items = [
            obj for obj in packages
            if np.hypot(obj.velocity[0], obj.velocity[1]) > 2.0
        ]
        
        if len(moving_items) > self.max_simultaneous_loads:
            event_key = f"simultaneous_loads_{frame_idx // 30}"
            if event_key not in self.reported_events:
                events.append(BehaviourEvent(
                    event_type="unsafe_loading_sequence",
                    object_id=moving_items[0].object_id,
                    timestamp=datetime.now().strftime("%H:%M:%S"),
                    frame_idx=frame_idx,
                    confidence=0.8,
                    location="loading_bay_1",
                    evidence={
                        "issue": "excessive_simultaneous_loads",
                        "moving_count": len(moving_items),
                        "max_allowed": self.max_simultaneous_loads,
                        "object_ids": [o.object_id for o in moving_items[:4]]
                    }
                ))
                self.reported_events.add(event_key)

        # 2. Check for unsafe vertical loading sequence: pallet on top of package or moving item sequence
        seq_pkgs = sorted(packages, key=lambda p: p.bbox[0]) if len(packages) > 60 else packages
        for i, top_item in enumerate(seq_pkgs):
            for j, bottom_item in enumerate(seq_pkgs):
                if i == j:
                    continue
                if len(seq_pkgs) > 60 and abs(top_item.bbox[0] - bottom_item.bbox[0]) > 250:
                    if bottom_item.bbox[0] > top_item.bbox[0] + 250:
                        break
                    continue
                pair_key = f"seq_{top_item.object_id}_{bottom_item.object_id}"
                if pair_key in self.reported_events:
                    continue

                top_w = top_item.bbox[2] - top_item.bbox[0]
                bottom_w = bottom_item.bbox[2] - bottom_item.bbox[0]
                
                is_on_top = (top_item.bbox[3] >= bottom_item.bbox[1] - 20) and (top_item.bbox[1] < bottom_item.bbox[1])
                horizontal_overlap = (top_item.center[0] >= bottom_item.bbox[0] - 10) and (top_item.center[0] <= bottom_item.bbox[2] + 10)

                # Flag pallet placed on package or actively moving load placed on small base
                top_is_moving = np.hypot(top_item.velocity[0], top_item.velocity[1]) > 1.5
                if is_on_top and horizontal_overlap and (top_item.class_name == "pallet" or (top_is_moving and top_w > bottom_w * 1.4)):
                    events.append(BehaviourEvent(
                        event_type="unsafe_loading_sequence",
                        object_id=top_item.object_id,
                        timestamp=datetime.now().strftime("%H:%M:%S"),
                        frame_idx=frame_idx,
                        confidence=0.75,
                        location="loading_bay_1",
                        evidence={
                            "issue": "heavy_on_light_sequence",
                            "top_id": top_item.object_id,
                            "bottom_id": bottom_item.object_id,
                            "top_width": round(top_w, 1),
                            "bottom_width": round(bottom_w, 1),
                            "sequence_violation": "large_item_placed_on_small_base"
                        }
                    ))
                    self.reported_events.add(pair_key)

        # 3. Insufficient clearance between simultaneously moving items
        for i in range(len(moving_items)):
            for j in range(i + 1, len(moving_items)):
                o1, o2 = moving_items[i], moving_items[j]
                dist = np.hypot(o1.center[0] - o2.center[0], o1.center[1] - o2.center[1])
                pair_key = f"clearance_{min(o1.object_id, o2.object_id)}_{max(o1.object_id, o2.object_id)}"
                if dist < self.min_clearance and pair_key not in self.reported_events:
                    events.append(BehaviourEvent(
                        event_type="unsafe_loading_sequence",
                        object_id=o1.object_id,
                        timestamp=datetime.now().strftime("%H:%M:%S"),
                        frame_idx=frame_idx,
                        confidence=0.7,
                        location="loading_bay_1",
                        evidence={
                            "issue": "insufficient_load_clearance",
                            "distance_px": round(float(dist), 1),
                            "min_required_px": self.min_clearance,
                            "object_1": o1.object_id,
                            "object_2": o2.object_id
                        }
                    ))
                    self.reported_events.add(pair_key)

        return events
