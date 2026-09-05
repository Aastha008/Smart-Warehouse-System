from typing import List, Tuple, Dict, Any, Optional
from datetime import datetime
from backend.behaviour.base_detector import BaseBehaviourDetector, BehaviourEvent
from backend.vision.tracker import TrackedObject

class DropDetector(BaseBehaviourDetector):
    behaviour_type = "product_drop"

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.behaviour_type = "product_drop"
        cfg = self.config.get("behaviours", {}).get("product_drop", self.config)
        self.min_fall_velocity = cfg.get("min_fall_velocity", 2.0)
        self.min_fall_distance = cfg.get("min_fall_distance", 40.0)
        self.max_stationary_velocity = cfg.get("max_stationary_velocity", 1.5)
        self.stationary_frames = cfg.get("stationary_frames", 3)
        self.min_confidence = cfg.get("min_confidence", 0.6)
        
        # State machine per track
        self.track_states: Dict[int, Dict[str, Any]] = {}
        self.state_machines = self.track_states

    def analyze(self, tracked_objects: List[TrackedObject], frame_idx: int, frame_shape: Tuple[int, int]) -> List[BehaviourEvent]:
        events = []
        target_classes = {"package", "carton", "bottle", "laptop", "cell phone", "box"}
        active_ids = set()

        for obj in tracked_objects:
            if obj.class_name not in target_classes:
                continue
            active_ids.add(obj.object_id)
            
            if obj.object_id not in self.track_states:
                self.track_states[obj.object_id] = {
                    "state": "TRACKING",
                    "highest_y": obj.center[1],
                    "fall_start_idx": frame_idx,
                    "stationary_count": 0,
                    "last_y": obj.center[1],
                    "reported": False
                }

            state = self.track_states[obj.object_id]
            curr_y = obj.center[1]
            vy = obj.velocity[1]

            # Trajectory analysis if available
            traj_drop = 0.0
            if len(obj.trajectory) >= 3:
                window = min(len(obj.trajectory), 8)
                traj_drop = obj.trajectory[-1][1] - obj.trajectory[-window][1]

            # Update highest point when object is above
            if curr_y < state["highest_y"]:
                state["highest_y"] = curr_y

            total_drop = curr_y - state["highest_y"]
            effective_drop = max(total_drop, traj_drop)

            # Check if falling rapidly
            if (vy >= self.min_fall_velocity or traj_drop >= 20.0) and effective_drop >= self.min_fall_distance * 0.5:
                state["state"] = "FALLING"

            # Check for impact / stationary after fall or completed downward trajectory
            is_stopped = abs(vy) <= self.max_stationary_velocity
            has_completed_traj_drop = traj_drop >= self.min_fall_distance and len(obj.trajectory) >= 3
            if state["state"] == "FALLING" and (is_stopped or has_completed_traj_drop):
                state["stationary_count"] += 1
                if not state["reported"]:
                    confidence = min(0.98, max(self.min_confidence, 0.6 + (effective_drop / 200.0) * 0.35))
                    events.append(BehaviourEvent(
                        event_type="product_drop",
                        object_id=obj.object_id,
                        timestamp=datetime.now().strftime("%H:%M:%S"),
                        frame_idx=frame_idx,
                        confidence=round(confidence, 2),
                        location="loading_bay_1",
                        evidence={
                            "drop_height_px": round(float(effective_drop), 1),
                            "velocity": round(float(vy), 2),
                            "class_name": obj.class_name
                        }
                    ))
                    state["reported"] = True
                    state["state"] = "COMPLETED"

            state["last_y"] = curr_y

        # Cleanup disappeared tracks
        stale_ids = [tid for tid in self.track_states if tid not in active_ids]
        for tid in stale_ids:
            # retain for a few frames or purge
            del self.track_states[tid]

        return events
