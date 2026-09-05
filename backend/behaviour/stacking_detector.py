from typing import List, Tuple, Dict, Any, Optional
from datetime import datetime
from backend.behaviour.base_detector import BaseBehaviourDetector, BehaviourEvent
from backend.vision.tracker import TrackedObject

class StackingDetector(BaseBehaviourDetector):
    behaviour_type = "improper_stacking"

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.behaviour_type = "improper_stacking"
        cfg = self.config.get("behaviours", {}).get("improper_stacking", self.config)
        self.heavy_on_light_ratio = cfg.get("heavy_on_light_ratio", 1.2)
        self.max_overhang = cfg.get("max_overhang", 0.2)
        self.min_confidence = cfg.get("min_confidence", 0.6)
        self.reported_pairs = set()

    def analyze(self, tracked_objects: List[TrackedObject], frame_idx: int, frame_shape: Tuple[int, int]) -> List[BehaviourEvent]:
        events = []
        target_classes = {"package", "carton", "box"}
        packages = [obj for obj in tracked_objects if obj.class_name in target_classes]
        if len(packages) > 60:
            packages = sorted(packages, key=lambda p: p.bbox[0])

        for i, p1 in enumerate(packages):
            for j, p2 in enumerate(packages):
                if i == j:
                    continue
                # If sorted and horizontal distance is far, break or continue
                if len(packages) > 60 and abs(p1.bbox[0] - p2.bbox[0]) > 300:
                    if p2.bbox[0] > p1.bbox[0] + 300:
                        break
                    continue

                pair_key = (p1.object_id, p2.object_id)
                if pair_key in self.reported_pairs:
                    continue

                p1_w = max(1.0, float(p1.bbox[2] - p1.bbox[0]))
                p1_h = max(1.0, float(p1.bbox[3] - p1.bbox[1]))
                p2_w = max(1.0, float(p2.bbox[2] - p2.bbox[0]))
                p2_h = max(1.0, float(p2.bbox[3] - p2.bbox[1]))

                p1_area = p1_w * p1_h
                p2_area = p2_w * p2_h

                # Check if p1 is stacked above p2 (bottom of p1 near top of p2)
                is_above = (p1.bbox[3] >= p2.bbox[1] - 25) and (p1.bbox[1] < p2.bbox[1])
                
                # Check horizontal overlap
                overlap_x1 = max(p1.bbox[0], p2.bbox[0])
                overlap_x2 = min(p1.bbox[2], p2.bbox[2])
                overlap_w = max(0.0, overlap_x2 - overlap_x1)

                if is_above and overlap_w > 0:
                    overhang_left = max(0.0, float(p2.bbox[0] - p1.bbox[0]))
                    overhang_right = max(0.0, float(p1.bbox[2] - p2.bbox[2]))
                    overhang_ratio = (overhang_left + overhang_right) / p1_w
                    size_ratio = p1_w / p2_w
                    area_ratio = p1_area / p2_area

                    is_heavy_on_light = size_ratio >= self.heavy_on_light_ratio or area_ratio >= self.heavy_on_light_ratio
                    is_overhanging = overhang_ratio >= self.max_overhang

                    if is_heavy_on_light or is_overhanging:
                        confidence = min(0.95, max(self.min_confidence, 0.65 + max(size_ratio - 1.0, overhang_ratio) * 0.3))
                        events.append(BehaviourEvent(
                            event_type="improper_stacking",
                            object_id=p1.object_id,
                            timestamp=datetime.now().strftime("%H:%M:%S"),
                            frame_idx=frame_idx,
                            confidence=round(confidence, 2),
                            location="loading_bay_1",
                            evidence={
                                "top_width": round(p1_w, 1),
                                "bottom_width": round(p2_w, 1),
                                "size_ratio": round(size_ratio, 2),
                                "area_ratio": round(area_ratio, 2),
                                "overhang_ratio": round(overhang_ratio, 2),
                                "top_id": p1.object_id,
                                "bottom_id": p2.object_id
                            }
                        ))
                        self.reported_pairs.add(pair_key)

        return events
