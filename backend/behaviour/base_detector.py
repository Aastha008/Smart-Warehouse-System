from abc import ABC, abstractmethod
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass, field
from datetime import datetime
from backend.vision.tracker import TrackedObject

@dataclass
class BehaviourEvent:
    event_type: str
    object_id: int
    timestamp: str = ""
    frame_idx: int = 0
    confidence: float = 1.0
    location: str = "loading_bay_1"
    evidence: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().strftime("%H:%M:%S")
        if not self.location:
            self.location = "loading_bay_1"
    
class BaseBehaviourDetector(ABC):
    behaviour_type: str = ""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        if not hasattr(self, "behaviour_type") or not self.behaviour_type:
            self.behaviour_type = ""

    @abstractmethod
    def analyze(self, tracked_objects: List[TrackedObject], frame_idx: int, frame_shape: Tuple[int, int]) -> List[BehaviourEvent]:
        pass
