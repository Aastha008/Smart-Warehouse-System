import yaml
from typing import List, Tuple, Dict, Any, Optional
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
    def __init__(self, config: Optional[Dict[str, Any]] = None, config_path: str = "configs/behaviour.yaml"):
        if config is not None and len(config) > 0:
            self.config = config
        else:
            self.config = self._load_config(config_path)
            
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

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        try:
            with open(config_path, "r") as f:
                return yaml.safe_load(f) or {}
        except FileNotFoundError:
            return {}

    def analyze(self, tracked_objects: List[TrackedObject], frame_idx: int, frame_shape: Tuple[int, int]) -> List[BehaviourEvent]:
        all_events = []
        for detector in self.detectors:
            try:
                events = detector.analyze(tracked_objects, frame_idx, frame_shape)
                if events:
                    all_events.extend(events)
            except Exception:
                pass
            
        # Basic deduplication per frame
        deduped = []
        seen = set()
        for e in all_events:
            key = f"{e.event_type}_{e.object_id}_{e.frame_idx}"
            if key not in seen:
                seen.add(key)
                deduped.append(e)
                
        return deduped
