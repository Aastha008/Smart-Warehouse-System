"""
DockGuard - Custom Video Analysis CLI
Analyze any real warehouse video file (e.g. from Godrej Hackathon Google Drive).

Usage:
    python scripts/analyze_custom_video.py --video path/to/video.mp4
    python scripts/analyze_custom_video.py --video path/to/video.mp4 --skip-frames 2 --save-annotated
"""
import os
import sys
import argparse
import time

# Ensure project root is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

import cv2
from backend.vision.pipeline import VideoPipeline

def main():
    parser = argparse.ArgumentParser(description="Analyze a warehouse video with DockGuard AI.")
    parser.add_argument("--video", "-v", required=True, help="Path to the video file (.mp4, .avi, .mov, etc.)")
    parser.add_argument("--skip-frames", "-s", type=int, default=2, help="Frame skipping step (default: 2)")
    parser.add_argument("--save-annotated", "-o", action="store_true", help="Save annotated video with bounding boxes")
    parser.add_argument("--output", default="uploads/annotated_output.mp4", help="Output annotated video path")
    args = parser.parse_args()

    video_path = args.video
    if not os.path.exists(video_path):
        print(f"\n❌ Error: Video file not found at: {video_path}")
        print("Please check the path and try again.")
        sys.exit(1)

    print("\n" + "="*70)
    print(" 🚀 DOCKGUARD: AI VIDEO INTELLIGENCE PIPELINE")
    print("="*70)
    print(f"📁 Input Video : {video_path}")
    print(f"⚙️ Skip Frames : {args.skip_frames} (analyzing every {args.skip_frames}nd frame)")

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"❌ Could not open video: {video_path}")
        sys.exit(1)

    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    duration_sec = total_frames / fps if fps > 0 else 0
    cap.release()

    print(f"📊 Video Info  : {width}x{height} @ {fps:.1f} FPS | Total Frames: {total_frames} (~{duration_sec:.1f}s)")
    print("🔄 Initializing YOLOv8 Object Detector, ByteTrack & 10 Temporal FSMs...")

    start_time = time.time()
    pipeline = VideoPipeline(skip_frames=args.skip_frames)
    
    print("▶️ Processing frames and tracking warehouse kinematics...")
    result = pipeline.process_video(video_path)
    elapsed = time.time() - start_time

    print(f"\n✅ Processing Completed in {elapsed:.2f}s ({result.total_frames / max(elapsed, 0.01):.1f} FPS)")
    print("="*70)
    print(f"🎯 SUMMARY OF DETECTED BEHAVIOUR INCIDENTS: {len(result.events)}")
    print("="*70)

    if not result.events:
        print("\n✨ Safe Handling Observed: No high-risk anomalies or severe violations detected.")
        print("All actions complied with warehouse safety standards.\n")
        return

    # Count by risk level
    risk_counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
    for ev in result.events:
        lvl = ev.get("risk_level", "MEDIUM")
        risk_counts[lvl] = risk_counts.get(lvl, 0) + 1

    print(f"\n📊 Risk Breakdown:")
    print(f"   🔴 CRITICAL : {risk_counts.get('CRITICAL', 0)}")
    print(f"   🟠 HIGH     : {risk_counts.get('HIGH', 0)}")
    print(f"   🟡 MEDIUM   : {risk_counts.get('MEDIUM', 0)}")
    print(f"   🟢 LOW      : {risk_counts.get('LOW', 0)}")
    print("-" * 70)

    print("\n📋 Incident Log Table:")
    for idx, ev in enumerate(result.events, 1):
        raw_ts = ev.get("timestamp", 0)
        try:
            ts = float(raw_ts)
            time_str = f"{int(ts//60):02d}:{int(ts%60):02d}.{int((ts%1)*10):01d}s"
        except (ValueError, TypeError):
            time_str = str(raw_ts)
        print(f"\n[{idx}] ⚠️  {ev.get('event_type', '').upper()} (Risk: {ev.get('risk_level', '')})")
        print(f"    ⏱️ Time in Video  : {time_str} (Frame #{ev.get('frame_idx')})")
        print(f"    📦 Object ID      : #{ev.get('object_id')} | Confidence: {ev.get('confidence', 0):.2f}")
        print(f"    💡 Explanation    : {ev.get('explanation')}")
        print(f"    🛡️ Action to Take : {ev.get('recommendation')}")

    print("\n" + "="*70)
    print("💡 TIP: You can also drag-and-drop this video in the Web UI:")
    print("   Open http://localhost:5173 ➔ Go to 'Video Analysis' ➔ Click 'Upload Warehouse Video'")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()
