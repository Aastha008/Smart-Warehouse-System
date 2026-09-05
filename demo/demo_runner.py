"""
AI Warehouse Intelligence - End-to-End Demo Runner
Executes an interactive and automated demonstration of the entire system:
1. Generates synthetic warehouse video scenario (or uses existing feed).
2. Runs VideoPipeline (detection, tracking, temporal behavior recognition, risk scoring).
3. Persists detected incidents into the database.
4. Queries FastAPI backend endpoints (events, statistics, high-risk items, alerts).
5. Exercises Grounded AI Supervisor with telemetry-grounded operational queries.
6. Displays dashboard readiness summary and KPIs.
"""
import os
import sys

# Ensure UTF-8 output on Windows console
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from scripts.generate_synthetic_video import generate_synthetic_video
from backend.vision.pipeline import VideoPipeline
from backend.database.session import SyncSessionLocal, init_sync_db
from backend.database.models import Event, Alert, VideoJob
from backend.assistant.assistant import WarehouseAssistant, AssistantTools
from backend.services.event_service import EventService
from backend.services.dashboard_service import DashboardService


BANNER = r"""
================================================================================
          ___    ____   _       __               __                          
         /   |  /  _/  | |     / /___ _________ / /_  ____  __  __________   
        / /| |  / /    | | /| / / __ `/ ___/ _ \/ __ \/ __ \/ / / / ___/ _ \  
       / ___ |_/ /     | |/ |/ / /_/ / /  /  __/ / / / /_/ / /_/ (__  )  __/  
      /_/  |_/___/     |__/|__/\__,_/_/   \___/_/ /_/\____/\__,_/____/\___/   
                                                                               
                 I N T E L L I G E N C E    P L A T F O R M                    
         End-to-End Edge-to-Cloud Video Analytics & Damage Prevention          
================================================================================
"""


def print_step(step_num: int, title: str):
    print(f"\n[{step_num}/6] >>> {title.upper()} <<<")
    print("-" * 75)


def run_demo(scenario: str = "all", skip_video: bool = False, output_path: str = "demo/demo_run_feed.mp4"):
    print(BANNER)
    start_time = time.time()
    
    # -------------------------------------------------------------
    # Step 1: Initialize Database & Ensure Schemas
    # -------------------------------------------------------------
    print_step(1, "Initializing Database Schemas & Storage Layer")
    init_sync_db()
    print("Database tables verified (events, video_jobs, alert_logs, cameras, metrics).")

    # -------------------------------------------------------------
    # Step 2: Generate / Prepare Synthetic Video
    # -------------------------------------------------------------
    print_step(2, f"Preparing Synthetic Warehouse Video Stream (Scenario: {scenario})")
    if not skip_video or not os.path.exists(output_path):
        video_file = generate_synthetic_video(
            output_path=output_path,
            scenario=scenario,
            duration_sec=6,
            fps=20,
            width=640,
            height=480
        )
    else:
        video_file = output_path
        print(f"Using existing video stream at: {video_file}")

    # -------------------------------------------------------------
    # Step 3: Run Video Ingestion & Vision Behavior Pipeline
    # -------------------------------------------------------------
    print_step(3, "Executing Computer Vision, Tracking & Temporal Behaviour Engine")
    pipeline = VideoPipeline(skip_frames=1)
    print("VideoPipeline initialized:")
    print("  * Detector: WarehouseDetector (YOLOv8 + Heuristic Fallback)")
    print("  * Tracker: ObjectTracker (ByteTrack / Kalman motion estimation)")
    print("  * Behaviour Engine: 10 Active Stateful Detectors")
    print("  * Risk Engine: Multi-Factor Composite Risk Classifier")
    
    print(f"\nProcessing video: {video_file}...")
    pipeline_result = pipeline.process_video(video_file)
    print(f"Processing Complete: {pipeline_result.total_frames} frames evaluated.")
    print(f"Total Behaviour Events Detected: {len(pipeline_result.events)}")

    # -------------------------------------------------------------
    # Step 4: Persist Detected Incidents & Trigger Alerts
    # -------------------------------------------------------------
    print_step(4, "Persisting Incidents & Evaluating Real-Time Alert Triggers")
    persisted_count = 0
    alert_count = 0
    
    with SyncSessionLocal() as session:
        for ev in pipeline_result.events:
            event_obj = Event(
                event_type=ev["event_type"],
                risk_level=ev["risk_level"],
                risk_score=75.0 if ev["risk_level"] in ("HIGH", "CRITICAL") else 40.0,
                confidence=ev.get("confidence", 0.9),
                camera_id="CAM-02-BAY2",
                location="Loading Bay 2",
                object_ids=[ev.get("object_id", 1)],
                video_path=video_file,
                video_start=max(0.0, ev["frame_idx"] / 20.0 - 1.0),
                video_end=ev["frame_idx"] / 20.0 + 1.0,
                evidence=ev.get("evidence", {}),
                explanation=ev.get("explanation", "Detected temporal behavior anomaly."),
                recommendation=ev.get("recommendation", "Review handling procedure.")
            )
            session.add(event_obj)
            session.flush()
            persisted_count += 1
            
            if ev["risk_level"] in ("HIGH", "CRITICAL"):
                alert_obj = Alert(
                    event_id=event_obj.event_id,
                    alert_type="audio_visual",
                    severity=ev["risk_level"],
                    message=f"{ev['risk_level']} Risk: {ev['event_type']} in Loading Bay 2",
                    location="Loading Bay 2",
                    acknowledged=False
                )
                session.add(alert_obj)
                alert_count += 1
                
        session.commit()
    
    print(f"Persisted {persisted_count} incident records to warehouse database.")
    print(f"Triggered {alert_count} high-priority audio/visual supervisor alerts.")

    # -------------------------------------------------------------
    # Step 5: Verify Grounded AI Supervisor Intelligence
    # -------------------------------------------------------------
    print_step(5, "Verifying Grounded AI Supervisor Telemetry & Guardrails")
    assistant = WarehouseAssistant(db_session_factory=SyncSessionLocal)
    
    test_queries = [
        "What high-risk events happened recently?",
        "What are the most common warehouse risks?",
        "What are the safety rules for package stacking?",
        "What is the weather in Hawaii today?"  # Out-of-domain query
    ]
    
    for q in test_queries:
        print(f"\n[USER QUERY]: \"{q}\"")
        resp = assistant.process_query(q)
        print(f"[AI SUPERVISOR]:\n{resp.get('response', '')}")
        print(f"[GROUNDING SOURCES]: {resp.get('sources', [])}")


    # -------------------------------------------------------------
    # Step 6: Platform Summary & Dashboard Metrics
    # -------------------------------------------------------------
    print_step(6, "Enterprise Dashboard Telemetry Summary")
    tools = AssistantTools(SyncSessionLocal)
    stats = tools.get_statistics()
    loc_stats = tools.get_location_stats()
    
    print(f"Total Monitored Events:       {stats.get('total_events', 0)}")
    print(f"High-Risk Incidents:          {stats.get('high_risk', 0)}")
    print(f"Critical Incidents:           {stats.get('critical', 0)}")
    print(f"Incidents Occurred Today:     {stats.get('events_today', 0)}")
    print(f"Location Incident Counts:     {loc_stats}")
    print(f"Behavior Breakdown:           {stats.get('by_behaviour', {})}")
    
    elapsed = time.time() - start_time
    print("\n" + "=" * 75)
    print(f"DEMO COMPLETED SUCCESSFULLY in {elapsed:.2f} seconds.")
    print("=" * 75 + "\n")


def main():
    parser = argparse.ArgumentParser(description="AI Warehouse Intelligence - End-to-End Demo Runner")
    parser.add_argument("--scenario", "-s", type=str, default="all",
                        choices=["all", "drop", "drag", "throw", "rough", "stack", "unstable", "zone", "pallet", "sequence", "equipment"],
                        help="Warehouse scenario to demonstrate")
    parser.add_argument("--skip-video", action="store_true", help="Skip synthetic video generation if file exists")
    parser.add_argument("--output", "-o", type=str, default="demo/demo_run_feed.mp4", help="Video output path")
    
    args = parser.parse_args()
    run_demo(scenario=args.scenario, skip_video=args.skip_video, output_path=args.output)


if __name__ == "__main__":
    main()
