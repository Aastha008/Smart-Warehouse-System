import yaml
from typing import List, Tuple, Dict, Any, Optional
from datetime import datetime
from backend.behaviour.base_detector import BaseBehaviourDetector, BehaviourEvent
from backend.vision.tracker import TrackedObject

class ZoneDetector(BaseBehaviourDetector):
    behaviour_type = "product_outside_zone"

    def __init__(self, config: Optional[Dict[str, Any]] = None, zones_config_path: str = "configs/zones.yaml"):
        super().__init__(config)
        self.behaviour_type = "product_outside_zone"
        self.zones_config_path = zones_config_path
        self.zones = self._load_zones()
        cfg = self.config.get("behaviours", {}).get("product_outside_zone", self.config)
        self.zone_margin = cfg.get("zone_margin", 0.05)
        self.min_confidence = cfg.get("min_confidence", 0.7)
        self.reported_tracks = set()

    def _load_zones(self) -> Dict[str, Any]:
        # Check if zones exist in passed config or file
        if "zones" in self.config:
            return self.config["zones"]
        try:
            with open(self.zones_config_path, "r") as f:
                data = yaml.safe_load(f) or {}
                return data.get("zones", {})
        except FileNotFoundError:
            return {
                "designated_area": {
                    "coordinates": {"x_min": 0.1, "y_min": 0.1, "x_max": 0.9, "y_max": 0.9}
                }
            }

    def _is_inside_zone(self, norm_x: float, norm_y: float, zone_coords: Dict[str, float]) -> bool:
        return (
            zone_coords.get("x_min", 0.0) - self.zone_margin <= norm_x <= zone_coords.get("x_max", 1.0) + self.zone_margin and
            zone_coords.get("y_min", 0.0) - self.zone_margin <= norm_y <= zone_coords.get("y_max", 1.0) + self.zone_margin
        )

    def analyze(self, tracked_objects: List[TrackedObject], frame_idx: int, frame_shape: Tuple[int, int]) -> List[BehaviourEvent]:
        events = []
        target_classes = {"package", "carton", "pallet", "box", "trolley", "forklift"}
        h, w = frame_shape[:2]
        if h == 0 or w == 0:
            return []

        for obj in tracked_objects:
            if obj.class_name not in target_classes:
                continue
            if obj.object_id in self.reported_tracks:
                continue

            # Normalized center coordinates
            norm_x = obj.center[0] / float(w)
            norm_y = obj.center[1] / float(h)

            # Check if object is inside designated zones
            in_designated = False
            designated_zone = self.zones.get("designated_area", {})
            if designated_zone and "coordinates" in designated_zone:
                in_designated = self._is_inside_zone(norm_x, norm_y, designated_zone["coordinates"])
            else:
                # Fallback: check if inside any configured operational zone
                for z_name, z_data in self.zones.items():
                    coords = z_data.get("coordinates", z_data) if isinstance(z_data, dict) else {}
                    if coords and self._is_inside_zone(norm_x, norm_y, coords):
                        in_designated = True
                        break

            # If outside designated zone boundaries (e.g. out of operational perimeter or in buffer)
            if not in_designated or norm_x < 0.08 or norm_x > 0.92 or norm_y < 0.08 or norm_y > 0.92:
                confidence = round(self.min_confidence, 2)
                events.append(BehaviourEvent(
                    event_type="product_outside_zone",
                    object_id=obj.object_id,
                    timestamp=datetime.now().strftime("%H:%M:%S"),
                    frame_idx=frame_idx,
                    confidence=confidence,
                    location="restricted_zone",
                    evidence={
                        "norm_x": round(norm_x, 3),
                        "norm_y": round(norm_y, 3),
                        "class_name": obj.class_name,
                        "bbox": [round(c, 1) for c in obj.bbox]
                    }
                ))
                self.reported_tracks.add(obj.object_id)

        return events
