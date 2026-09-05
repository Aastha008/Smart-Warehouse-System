from typing import List, Tuple, Dict, Any, Optional
from datetime import datetime
from backend.behaviour.base_detector import BaseBehaviourDetector, BehaviourEvent
from backend.vision.tracker import TrackedObject

class PalletDetector(BaseBehaviourDetector):
    behaviour_type = "incorrect_pallet_position"

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.behaviour_type = "incorrect_pallet_position"
        cfg = self.config.get("behaviours", {}).get("incorrect_pallet_position", self.config)
        self.pallet_alignment_threshold = cfg.get("pallet_alignment_threshold", 15.0)
        self.overhang_threshold = cfg.get("overhang_threshold", 0.15)
        self.min_confidence = cfg.get("min_confidence", 0.6)
        self.reported_events = set()

    def analyze(self, tracked_objects: List[TrackedObject], frame_idx: int, frame_shape: Tuple[int, int]) -> List[BehaviourEvent]:
        events = []
        pallets = [obj for obj in tracked_objects if obj.class_name == "pallet"]
        packages = [obj for obj in tracked_objects if obj.class_name in {"package", "carton", "box"}]

        # 1. Check packages resting on pallets for overhang
        for pallet in pallets:
            pal_w = max(1.0, float(pallet.bbox[2] - pallet.bbox[0]))
            
            # Check package overhang
            for pkg in packages:
                event_key = f"overhang_{pallet.object_id}_{pkg.object_id}"
                if event_key in self.reported_events:
                    continue

                # Is package on or directly above pallet?
                is_on_pallet = (pkg.bbox[3] >= pallet.bbox[1] - 25) and (pkg.bbox[1] < pallet.bbox[3])
                if not is_on_pallet:
                    continue

                pkg_w = max(1.0, float(pkg.bbox[2] - pkg.bbox[0]))
                overhang_left = max(0.0, float(pallet.bbox[0] - pkg.bbox[0]))
                overhang_right = max(0.0, float(pkg.bbox[2] - pallet.bbox[2]))
                overhang_frac = (overhang_left + overhang_right) / pkg_w

                if overhang_frac >= self.overhang_threshold:
                    confidence = min(0.95, max(self.min_confidence, 0.65 + overhang_frac * 0.3))
                    events.append(BehaviourEvent(
                        event_type="incorrect_pallet_position",
                        object_id=pallet.object_id,
                        timestamp=datetime.now().strftime("%H:%M:%S"),
                        frame_idx=frame_idx,
                        confidence=round(confidence, 2),
                        location="loading_bay_1",
                        evidence={
                            "issue": "product_overhang",
                            "pallet_id": pallet.object_id,
                            "package_id": pkg.object_id,
                            "overhang_fraction": round(overhang_frac, 2),
                            "pallet_width": round(pal_w, 1),
                            "package_width": round(pkg_w, 1)
                        }
                    ))
                    self.reported_events.add(event_key)

            # 2. Check pallet misalignment or positioning in transit/aisle
            pal_event_key = f"pos_{pallet.object_id}"
            if pal_event_key not in self.reported_events:
                norm_x = pallet.center[0] / max(1.0, float(frame_shape[1]))
                # If pallet is positioned outside designated boundaries or shifted
                if norm_x < 0.12 or norm_x > 0.88 or abs(pallet.velocity[0]) > 5.0:
                    events.append(BehaviourEvent(
                        event_type="incorrect_pallet_position",
                        object_id=pallet.object_id,
                        timestamp=datetime.now().strftime("%H:%M:%S"),
                        frame_idx=frame_idx,
                        confidence=round(self.min_confidence, 2),
                        location="transit_zone",
                        evidence={
                            "issue": "pallet_misalignment",
                            "pallet_id": pallet.object_id,
                            "norm_x": round(norm_x, 3),
                            "misalignment_px": round(abs(pallet.center[0] - frame_shape[1] * 0.5), 1)
                        }
                    ))
                    self.reported_events.add(pal_event_key)

        return events
