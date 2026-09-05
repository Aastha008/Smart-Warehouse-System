"""
AI Warehouse Intelligence - Synthetic Scenario Generator & Pipeline Runner
Creates a synthetic warehouse video scenario (moving person, package drop/throw motion),
feeds it to VideoPipeline, and outputs the detected incidents.
"""
import os
import cv2
import numpy as np
import json
from backend.vision.pipeline import VideoPipeline

def generate_synthetic_demo_video(filename="demo/sample_warehouse_feed.mp4", duration_sec=5, fps=20):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    width, height = 640, 480
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(filename, fourcc, fps, (width, height))
    
    total_frames = duration_sec * fps
    
    # State variables for simulation
    box_x, box_y = 200, 150
    box_vy = 0
    box_dropping = False
    
    for f in range(total_frames):
        # Create warehouse background (concrete floor + wall dock)
        frame = np.full((height, width, 3), (220, 220, 220), dtype=np.uint8)
        
        # Floor line and dock zone
        cv2.rectangle(frame, (0, 300), (width, height), (160, 160, 160), -1)
        cv2.rectangle(frame, (50, 320), (250, 440), (0, 200, 255), 2) # Yellow zone
        cv2.putText(frame, "BAY 2 - LOADING ZONE", (60, 340), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 150, 200), 1)
        
        # Pallet on the right
        cv2.rectangle(frame, (400, 320), (560, 420), (100, 130, 160), -1)
        cv2.putText(frame, "PALLET #4", (430, 370), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Simulated person (moving right)
        person_x = 120 + int(f * 2.5)
        person_y = 180
        # Draw torso / head (person representation)
        cv2.circle(frame, (person_x + 30, person_y + 20), 20, (50, 50, 200), -1)
        cv2.rectangle(frame, (person_x + 10, person_y + 40), (person_x + 50, person_y + 140), (200, 80, 50), -1)
        cv2.putText(frame, "OPERATOR", (person_x, person_y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1)
        
        # Box handling and drop simulation
        if f > 30 and f < 70:
            box_dropping = True
        
        if not box_dropping:
            box_x = person_x + 40
            box_y = person_y + 60
        else:
            box_vy += 1.8 # Gravity acceleration
            box_y += int(box_vy)
            if box_y > 350: # Floor impact
                box_y = 350
                box_vy = 0
                
        # Draw package/carton
        cv2.rectangle(frame, (box_x, box_y), (box_x + 50, box_y + 45), (40, 120, 180), -1)
        cv2.rectangle(frame, (box_x, box_y), (box_x + 50, box_y + 45), (20, 60, 100), 2)
        cv2.putText(frame, "CARTON", (box_x, box_y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (20, 60, 100), 1)
        
        # Timestamp overlay
        sec = f / fps
        cv2.putText(frame, f"CAM-02-BAY2 | Time: 00:00:{sec:04.1f} | Frame: {f}", (15, 25), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
        
        out.write(frame)
        
    out.release()
    print(f"Generated synthetic video at: {filename} ({total_frames} frames)")
    return filename

def run_demo():
    print("=== AI Warehouse Intelligence: Video Pipeline Demo ===")
    video_file = generate_synthetic_demo_video()
    
    print("\nInitializing Video Pipeline...")
    pipeline = VideoPipeline(skip_frames=1)
    
    print(f"Processing {video_file}...")
    result = pipeline.process_video(video_file)
    
    print(f"\nProcessing Complete!")
    print(f"Total Frames Processed: {result.total_frames}")
    print(f"Total Behaviour Events Detected: {len(result.events)}")
    
    if result.events:
        print("\n--- Detected Incident Highlights ---")
        for idx, ev in enumerate(result.events[:5], 1):
            print(f"[{idx}] {ev['event_type'].upper()} | Risk: {ev['risk_level']} | Frame: {ev['frame_idx']} | Time: {ev['timestamp']}")
            print(f"    Explanation: {ev['explanation']}")
            print(f"    Recommendation: {ev['recommendation']}\n")

if __name__ == "__main__":
    run_demo()

