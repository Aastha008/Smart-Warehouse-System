
import numpy as np
from dataclasses import dataclass, field
from typing import List, Tuple, Dict
from backend.vision.detector import Detection
import time

@dataclass
class TrackedObject:
    object_id: int
    class_name: str
    bbox: Tuple[float, float, float, float]
    center: Tuple[float, float]
    velocity: Tuple[float, float] = (0.0, 0.0)
    acceleration: Tuple[float, float] = (0.0, 0.0)
    trajectory: List[Tuple[float, float]] = field(default_factory=list)
    timestamp: float = 0.0
    confidence: float = 0.0
    last_updated: int = 0
    missing_frames: int = 0

    @property
    def track_id(self) -> int:
        return self.object_id

    @track_id.setter
    def track_id(self, val: int):
        self.object_id = val

    @property
    def id(self) -> int:
        return self.object_id

    @id.setter
    def id(self, val: int):
        self.object_id = val

class ObjectTracker:
    def __init__(self, max_missing_frames: int = 5, distance_threshold: float = 50.0):
        self.max_missing_frames = max_missing_frames
        self.distance_threshold = distance_threshold
        self.tracks: Dict[int, TrackedObject] = {}
        self.next_id = 1
    
    def _compute_center(self, bbox: Tuple[float, float, float, float]) -> Tuple[float, float]:
        return ((bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2)
        
    def _compute_distance(self, c1: Tuple[float, float], c2: Tuple[float, float]) -> float:
        return np.sqrt((c1[0] - c2[0])**2 + (c1[1] - c2[1])**2)

    def update(self, detections: List[Detection], frame_idx: int) -> List[TrackedObject]:
        current_centers = [self._compute_center(d.bbox) for d in detections]
        
        # Simple Greedy Matching (Replace with Hungarian algorithm for prod)
        matched_detections = set()
        matched_tracks = set()
        
        for t_id, track in self.tracks.items():
            if track.missing_frames >= self.max_missing_frames:
                continue
                
            best_match_idx = -1
            best_dist = float('inf')
            
            for d_idx, d in enumerate(detections):
                if d_idx in matched_detections: continue
                if d.class_name != track.class_name: continue
                
                dist = self._compute_distance(track.center, current_centers[d_idx])
                if dist < best_dist and dist < self.distance_threshold:
                    best_dist = dist
                    best_match_idx = d_idx
            
            if best_match_idx != -1:
                # Update track
                d = detections[best_match_idx]
                new_center = current_centers[best_match_idx]
                
                # Update velocity/acceleration
                dt = 1.0 # Assuming constant framerate for simple velocity
                vx = new_center[0] - track.center[0]
                vy = new_center[1] - track.center[1]
                
                ax = vx - track.velocity[0]
                ay = vy - track.velocity[1]
                
                track.bbox = d.bbox
                track.center = new_center
                track.velocity = (vx, vy)
                track.acceleration = (ax, ay)
                track.trajectory.append(new_center)
                if len(track.trajectory) > 50:
                    track.trajectory.pop(0)
                track.confidence = d.confidence
                track.last_updated = frame_idx
                track.missing_frames = 0
                track.timestamp = time.time()
                
                matched_detections.add(best_match_idx)
                matched_tracks.add(t_id)
            else:
                track.missing_frames += 1
                
        # Create new tracks
        for d_idx, d in enumerate(detections):
            if d_idx not in matched_detections:
                center = current_centers[d_idx]
                self.tracks[self.next_id] = TrackedObject(
                    object_id=self.next_id,
                    class_name=d.class_name,
                    bbox=d.bbox,
                    center=center,
                    trajectory=[center],
                    confidence=d.confidence,
                    last_updated=frame_idx,
                    timestamp=time.time()
                )
                self.next_id += 1
                
        # Remove old tracks
        self.tracks = {k: v for k, v in self.tracks.items() if v.missing_frames < self.max_missing_frames}
        
        return list(self.tracks.values())
