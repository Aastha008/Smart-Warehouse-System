try:
    import cv2
except ImportError:
    cv2 = None

from typing import List, Dict, Any
from dataclasses import dataclass
from backend.vision.detector import WarehouseDetector
from backend.vision.tracker import ObjectTracker
from backend.vision.motion import MotionAnalyzer
from backend.behaviour.behaviour_engine import BehaviourEngine
from backend.risk.risk_engine import RiskEngine
from backend.vision.annotator import Annotator

@dataclass
class FrameResult:
    frame_idx: int
    annotated_frame: Any
    events: List[Any]
    assessments: List[Any]

@dataclass
class AnalysisResult:
    total_frames: int
    events: List[Dict[str, Any]]

class VideoPipeline:
    def __init__(
        self,
        skip_frames: int = 2,
        detection_config: str = "configs/detection.yaml",
        behaviour_config: str = "configs/behaviour.yaml",
        risk_config: str = "configs/risk.yaml"
    ):
        self.skip_frames = skip_frames
        self.detector = WarehouseDetector(config_path=detection_config)
        self.tracker = ObjectTracker()
        self.motion = MotionAnalyzer()
        self.behaviour = BehaviourEngine(config_path=behaviour_config)
        self.risk = RiskEngine(config_path=risk_config)
        self.annotator = Annotator()
        
    def process_frame(self, frame, frame_idx: int) -> FrameResult:
        detections = self.detector.detect(frame)
        tracks = self.tracker.update(detections, frame_idx)
        # self.motion.analyze(tracks) # updates internal state if needed, not strictly req for return
        
        events = self.behaviour.analyze(tracks, frame_idx, frame.shape if hasattr(frame, 'shape') else (480, 640))
        assessments = [self.risk.classify_risk(e) for e in events]
        
        annotated_frame = self.annotator.annotate(frame, tracks, events, assessments)
        
        return FrameResult(
            frame_idx=frame_idx,
            annotated_frame=annotated_frame,
            events=events,
            assessments=assessments
        )

    def process_video(self, video_path: str, output_path: str = None) -> AnalysisResult:
        if cv2 is None:
            raise ValueError("OpenCV (cv2) is required for process_video")
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Could not open video {video_path}")
            
        frame_idx = 0
        all_events = []
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret: break
            
            if frame_idx % self.skip_frames == 0:
                result = self.process_frame(frame, frame_idx)
                for e, a in zip(result.events, result.assessments):
                    all_events.append({
                        "event_type": e.event_type,
                        "object_id": e.object_id,
                        "timestamp": e.timestamp,
                        "frame_idx": e.frame_idx,
                        "confidence": e.confidence,
                        "location": e.location,
                        "risk_level": a.level,
                        "evidence": e.evidence,
                        "explanation": a.explanation,
                        "recommendation": a.recommendation
                    })
                    
            frame_idx += 1
            
        cap.release()
        return AnalysisResult(total_frames=frame_idx, events=all_events)
