
import numpy as np
from typing import List, Dict, Any
from dataclasses import dataclass
from backend.vision.tracker import TrackedObject

@dataclass
class MotionFeatures:
    object_id: int
    avg_velocity: float
    max_velocity: float
    is_dropping: bool
    is_jerky: bool
    horizontal_movement: float
    vertical_movement: float
    total_displacement: float

class MotionAnalyzer:
    def __init__(self):
        pass

    def compute_velocity(self, trajectory: List[Tuple[float, float]]) -> Tuple[float, float]:
        """Compute average (vx, vy) velocity from a trajectory list."""
        if not trajectory or len(trajectory) < 2:
            return (0.0, 0.0)
        dxs = [trajectory[i][0] - trajectory[i-1][0] for i in range(1, len(trajectory))]
        dys = [trajectory[i][1] - trajectory[i-1][1] for i in range(1, len(trajectory))]
        return (float(np.mean(dxs)), float(np.mean(dys)))

    def compute_acceleration(self, trajectory: List[Tuple[float, float]]) -> Tuple[float, float]:
        """Compute average (ax, ay) acceleration from a trajectory list."""
        if not trajectory or len(trajectory) < 3:
            return (0.0, 0.0)
        vels = [(trajectory[i][0] - trajectory[i-1][0], trajectory[i][1] - trajectory[i-1][1]) for i in range(1, len(trajectory))]
        axs = [vels[i][0] - vels[i-1][0] for i in range(1, len(vels))]
        ays = [vels[i][1] - vels[i-1][1] for i in range(1, len(vels))]
        return (float(np.mean(axs)), float(np.mean(ays)))

    def analyze(self, tracks: List[TrackedObject]) -> Dict[int, MotionFeatures]:
        features = {}
        for track in tracks:
            if len(track.trajectory) < 3:
                features[track.object_id] = MotionFeatures(
                    object_id=track.object_id,
                    avg_velocity=0.0, max_velocity=0.0, is_dropping=False,
                    is_jerky=False, horizontal_movement=0.0, vertical_movement=0.0, total_displacement=0.0
                )
                continue
                
            velocities = []
            for i in range(1, len(track.trajectory)):
                dx = track.trajectory[i][0] - track.trajectory[i-1][0]
                dy = track.trajectory[i][1] - track.trajectory[i-1][1]
                velocities.append(np.sqrt(dx**2 + dy**2))
                
            avg_vel = np.mean(velocities)
            max_vel = np.max(velocities)
            
            start_pos = track.trajectory[0]
            end_pos = track.trajectory[-1]
            dx_total = end_pos[0] - start_pos[0]
            dy_total = end_pos[1] - start_pos[1]
            
            # y goes down in images
            is_dropping = dy_total > 20 and avg_vel > 10 
            
            # Acceleration variance for jerkiness
            accels = [velocities[i] - velocities[i-1] for i in range(1, len(velocities))]
            is_jerky = len(accels) > 0 and np.std(accels) > 5.0
            
            features[track.object_id] = MotionFeatures(
                object_id=track.object_id,
                avg_velocity=float(avg_vel),
                max_velocity=float(max_vel),
                is_dropping=bool(is_dropping),
                is_jerky=bool(is_jerky),
                horizontal_movement=float(abs(dx_total)),
                vertical_movement=float(dy_total),
                total_displacement=float(np.sqrt(dx_total**2 + dy_total**2))
            )
        return features
