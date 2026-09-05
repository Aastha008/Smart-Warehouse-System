try:
    import cv2
except ImportError:
    cv2 = None

import numpy as np
from typing import List
from backend.vision.tracker import TrackedObject
from backend.behaviour.base_detector import BehaviourEvent
from backend.risk.risk_engine import RiskAssessment

class Annotator:
    def __init__(self):
        self.colors = {
            "LOW": (0, 255, 0),
            "MEDIUM": (0, 165, 255),  # Orange
            "HIGH": (0, 0, 255),      # Red
            "CRITICAL": (0, 0, 220)   # Dark Red / Crimson
        }
        
    def annotate(self, frame: np.ndarray, tracks: List[TrackedObject], events: List[BehaviourEvent], assessments: List[RiskAssessment]) -> np.ndarray:
        if frame is None:
            return None
        out_frame = frame.copy() if hasattr(frame, "copy") else frame
        
        if cv2 is None:
            return out_frame
            
        # Draw tracks
        for t in tracks:
            x1, y1, x2, y2 = map(int, t.bbox)
            cv2.rectangle(out_frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
            cv2.putText(out_frame, f"ID:{t.object_id} {t.class_name}", (x1, max(10, y1 - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
            
            # Draw trajectory
            if len(t.trajectory) > 1:
                pts = np.array(t.trajectory, np.int32)
                pts = pts.reshape((-1, 1, 2))
                cv2.polylines(out_frame, [pts], False, (255, 255, 0), 1)
                
        # Draw events
        event_dict = {e.object_id: (e, a) for e, a in zip(events, assessments)}
        for t in tracks:
            if t.object_id in event_dict:
                e, a = event_dict[t.object_id]
                x1, y1, x2, y2 = map(int, t.bbox)
                color = self.colors.get(a.level, (255, 255, 255))
                cv2.rectangle(out_frame, (x1, y1), (x2, y2), color, 4)
                cv2.putText(out_frame, f"ALERT: {e.event_type}", (x1, min(out_frame.shape[0] - 10, y2 + 20)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                
        return out_frame
