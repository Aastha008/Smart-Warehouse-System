from typing import List, Tuple, Dict, Any, Optional
from datetime import datetime
import numpy as np
from backend.behaviour.base_detector import BaseBehaviourDetector, BehaviourEvent
from backend.vision.tracker import TrackedObject

class EquipmentDetector(BaseBehaviourDetector):
    behaviour_type = "improper_handling_equipment"

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.behaviour_type = "improper_handling_equipment"
        cfg = self.config.get("behaviours", {}).get("improper_handling_equipment", self.config)
        self.min_product_size_for_equipment = cfg.get("min_product_size_for_equipment", 130.0)
        self.equipment_proximity_threshold = cfg.get("equipment_proximity_threshold", 120.0)
        self.min_confidence = cfg.get("min_confidence", 0.55)
        self.reported_events = set()

    def analyze(self, tracked_objects: List[TrackedObject], frame_idx: int, frame_shape: Tuple[int, int]) -> List[BehaviourEvent]:
        events = []
        equipment = [obj for obj in tracked_objects if obj.class_name in {"forklift", "trolley", "vehicle"}]
        persons = [obj for obj in tracked_objects if obj.class_name == "person"]
        packages = [obj for obj in tracked_objects if obj.class_name in {"package", "carton", "box", "pallet"}]

        # 1. Heavy / oversized load moving without equipment nearby
        for pkg in packages:
            event_key = f"no_equip_{pkg.object_id}"
            if event_key in self.reported_events:
                continue

            w = float(pkg.bbox[2] - pkg.bbox[0])
            h = float(pkg.bbox[3] - pkg.bbox[1])
            size = max(w, h)
            v_mag = np.hypot(pkg.velocity[0], pkg.velocity[1])

            # If load is large and moving (actively being handled/relocated)
            if size >= self.min_product_size_for_equipment and (v_mag > 1.5 or len(pkg.trajectory) >= 4):
                # Check distance to any equipment
                closest_equip_dist = float("inf")
                for eq in equipment:
                    d = np.hypot(pkg.center[0] - eq.center[0], pkg.center[1] - eq.center[1])
                    if d < closest_equip_dist:
                        closest_equip_dist = d

                if closest_equip_dist > self.equipment_proximity_threshold:
                    events.append(BehaviourEvent(
                        event_type="improper_handling_equipment",
                        object_id=pkg.object_id,
                        timestamp=datetime.now().strftime("%H:%M:%S"),
                        frame_idx=frame_idx,
                        confidence=round(self.min_confidence, 2),
                        location="loading_bay_1",
                        evidence={
                            "issue": "heavy_load_handled_without_equipment",
                            "package_size_px": round(size, 1),
                            "min_required_size": self.min_product_size_for_equipment,
                            "closest_equipment_dist": round(closest_equip_dist, 1) if closest_equip_dist != float("inf") else -1,
                            "class_name": pkg.class_name
                        }
                    ))
                    self.reported_events.add(event_key)

        # 2. Moving equipment too close to pedestrian / unauthorized lane
        for eq in equipment:
            eq_v = np.hypot(eq.velocity[0], eq.velocity[1])
            for p in persons:
                pair_key = f"proximity_{eq.object_id}_{p.object_id}"
                if pair_key in self.reported_events:
                    continue

                dist = np.hypot(eq.center[0] - p.center[0], eq.center[1] - p.center[1])
                if dist < 60.0 and eq_v > 2.0:
                    events.append(BehaviourEvent(
                        event_type="improper_handling_equipment",
                        object_id=eq.object_id,
                        timestamp=datetime.now().strftime("%H:%M:%S"),
                        frame_idx=frame_idx,
                        confidence=0.85,
                        location="loading_bay_1",
                        evidence={
                            "issue": "equipment_pedestrian_hazard",
                            "equipment_id": eq.object_id,
                            "person_id": p.object_id,
                            "distance_px": round(float(dist), 1),
                            "equipment_velocity": round(float(eq_v), 2)
                        }
                    ))
                    self.reported_events.add(pair_key)

        return events
