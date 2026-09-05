"""
AI Warehouse Intelligence - Demo Database Seeder
Populates database with realistic multi-factor warehouse incidents across all 10 behaviors,
varying risk severities (LOW, MEDIUM, HIGH, CRITICAL), evidence payloads,
video processing jobs, alert logs, camera registry, and operational metrics.
"""
import os
import sys

# Ensure workspace root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import uuid
import random
import argparse
import asyncio
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any

from backend.database.connection import AsyncSessionLocal, engine, Base
from backend.database.models import Event, VideoJob, Alert, Camera, Metric



LOCATIONS = [
    "Loading Bay 1",
    "Loading Bay 2",
    "Loading Bay 3",
    "Loading Bay 4",
    "Unloading Dock East",
    "Staging Area Central",
    "Aisle 7 - High Rack",
]

CAMERAS = [
    {"camera_id": "CAM-01-NORTH", "name": "Loading Bay 1 Overhead", "location": "Loading Bay 1"},
    {"camera_id": "CAM-02-BAY2", "name": "Bay 2 High-Speed PTZ", "location": "Loading Bay 2"},
    {"camera_id": "CAM-03-BAY3", "name": "Bay 3 Dock Overview", "location": "Loading Bay 3"},
    {"camera_id": "CAM-04-EAST", "name": "Dock East Inbound Cam", "location": "Unloading Dock East"},
    {"camera_id": "CAM-05-DOCK", "name": "Central Staging Wide-Angle", "location": "Staging Area Central"},
]

BEHAVIOR_TEMPLATES = [
    {
        "event_type": "product_drop",
        "default_risk": "HIGH",
        "score_range": (70, 88),
        "obs": "Carton slipped from operator handling height, accelerating rapidly to concrete floor impact.",
        "rec": "Inspect package integrity before staging; review ergonomic two-hand lifting posture with shift team.",
        "make_evidence": lambda: {
            "drop_height_m": round(random.uniform(0.75, 1.85), 2),
            "drop_height_px": random.randint(90, 180),
            "impact_velocity_mps": round(random.uniform(3.8, 6.2), 2),
            "acceleration_spike_mps2": round(random.uniform(9.8, 14.5), 2),
            "product_category": random.choice(["consumer_electronics", "glassware", "perishables", "auto_parts"])
        }
    },
    {
        "event_type": "product_dragging",
        "default_risk": "MEDIUM",
        "score_range": (42, 60),
        "obs": "Corrugated carton dragged continuously across warehouse concrete floor without dolly.",
        "rec": "Utilize hand truck, roller cart, or pallet jack for lateral transport to avoid bottom abrasion.",
        "make_evidence": lambda: {
            "drag_distance_m": round(random.uniform(2.5, 8.0), 2),
            "drag_duration_sec": round(random.uniform(2.0, 6.5), 2),
            "surface_friction_index": 0.65,
            "product_category": random.choice(["apparel", "paper_goods", "bulk_hardware"])
        }
    },
    {
        "event_type": "product_throwing",
        "default_risk": "CRITICAL",
        "score_range": (88, 98),
        "obs": "High-velocity airborne trajectory detected between operators across loading aisle.",
        "rec": "Immediate supervisor safety intervention required. Strict zero-tolerance toss policy enforcement.",
        "make_evidence": lambda: {
            "throw_velocity_mps": round(random.uniform(4.5, 8.2), 2),
            "airborne_time_sec": round(random.uniform(0.8, 1.6), 2),
            "trajectory_distance_m": round(random.uniform(2.8, 5.5), 2),
            "product_category": "fragile_electronics"
        }
    },
    {
        "event_type": "rough_handling",
        "default_risk": "HIGH",
        "score_range": (65, 82),
        "obs": "Severe abrupt deceleration and sharp impact spike during box placement.",
        "rec": "Ensure controlled placement onto staging surfaces; conduct safe handling refresher.",
        "make_evidence": lambda: {
            "impact_jerk_mps3": round(random.uniform(15.0, 32.0), 2),
            "deceleration_mps2": round(random.uniform(8.0, 16.5), 2),
            "product_category": random.choice(["cosmetics", "machinery_parts", "ceramics"])
        }
    },
    {
        "event_type": "improper_stacking",
        "default_risk": "MEDIUM",
        "score_range": (48, 68),
        "obs": "Heavy dense carton positioned directly on top of smaller low-burst-strength box.",
        "rec": "Follow strict heavy-to-light pyramid stacking hierarchy to protect lower tiers.",
        "make_evidence": lambda: {
            "top_box_weight_kg": round(random.uniform(22.0, 45.0), 1),
            "bottom_box_weight_kg": round(random.uniform(5.0, 12.0), 1),
            "weight_ratio": round(random.uniform(2.5, 4.5), 2),
            "overhang_pct": random.randint(15, 35)
        }
    },
    {
        "event_type": "unstable_stacking",
        "default_risk": "HIGH",
        "score_range": (75, 90),
        "obs": "Multi-tier pallet stack center of mass tilted > 18 degrees, exceeding stability envelope.",
        "rec": "Secure pallet with stretch-wrap immediately and restack before forklift transit.",
        "make_evidence": lambda: {
            "tilt_angle_deg": round(random.uniform(16.5, 26.0), 1),
            "stack_height_m": round(random.uniform(1.8, 2.6), 2),
            "stack_tiers": random.randint(4, 7),
            "wobble_frequency_hz": round(random.uniform(0.5, 1.8), 2)
        }
    },
    {
        "event_type": "product_outside_zone",
        "default_risk": "LOW",
        "score_range": (20, 38),
        "obs": "Package deposited within red-hatched pedestrian walkway outside designated bay perimeter.",
        "rec": "Clear emergency walkways and pedestrian aisles; relocate freight into yellow loading box.",
        "make_evidence": lambda: {
            "zone_encroachment_px": random.randint(40, 120),
            "aisle_type": "pedestrian_emergency_walkway",
            "obstruction_area_sqm": round(random.uniform(0.5, 1.8), 2)
        }
    },
    {
        "event_type": "incorrect_pallet_position",
        "default_risk": "MEDIUM",
        "score_range": (45, 62),
        "obs": "Wood pallet angled diagonally, protruding 45cm into active forklift transit corridor.",
        "rec": "Re-align pallet square to docking floor guide markers to prevent vehicular collisions.",
        "make_evidence": lambda: {
            "misalignment_angle_deg": round(random.uniform(25.0, 45.0), 1),
            "lane_encroachment_cm": random.randint(30, 65),
            "traffic_density": "high_forklift_transit"
        }
    },
    {
        "event_type": "unsafe_loading_sequence",
        "default_risk": "HIGH",
        "score_range": (72, 86),
        "obs": "Upper rack level loaded prior to securing base foundation support pallets.",
        "rec": "Sequence container and rack loading bottom-up to maintain low center of gravity.",
        "make_evidence": lambda: {
            "rack_level_loaded": 3,
            "base_level_occupancy_pct": 0,
            "structural_risk_rating": "high_top_heavy"
        }
    },
    {
        "event_type": "improper_handling_equipment",
        "default_risk": "HIGH",
        "score_range": (74, 89),
        "obs": "Manual lift attempt on oversized freight exceeding 42kg individual handling limit.",
        "rec": "Mandate mechanical lift assistance (crane/stacker) or mandatory two-person team lift.",
        "make_evidence": lambda: {
            "cargo_weight_est_kg": round(random.uniform(42.0, 78.0), 1),
            "legal_single_lift_limit_kg": 25.0,
            "lift_technique": "single_operator_manual"
        }
    }
]


async def seed_cameras(session):
    for cam_info in CAMERAS:
        cam = Camera(
            camera_id=cam_info["camera_id"],
            name=cam_info["name"],
            location=cam_info["location"],
            rtsp_url=f"rtsp://192.168.1.{random.randint(10, 99)}:554/stream1",
            status="active",
            is_active=True,
            created_at=datetime.now(timezone.utc) - timedelta(days=30)
        )
        await session.merge(cam)


async def seed_video_jobs(session) -> List[str]:
    job_ids = []
    job_specs = [
        {"status": "completed", "progress": 1.0, "frames": 300, "events": 6, "err": None},
        {"status": "completed", "progress": 1.0, "frames": 240, "events": 4, "err": None},
        {"status": "completed", "progress": 1.0, "frames": 180, "events": 3, "err": None},
        {"status": "processing", "progress": 0.65, "frames": 400, "events": 2, "err": None},
        {"status": "pending", "progress": 0.0, "frames": 0, "events": 0, "err": None},
    ]
    for idx, spec in enumerate(job_specs, 1):
        job_id = f"job_seed_{uuid.uuid4().hex[:10]}"
        job_ids.append(job_id)
        job = VideoJob(
            job_id=job_id,
            video_path=f"demo/sample_warehouse_feed_bay{idx}.mp4",
            status=spec["status"],
            progress=spec["progress"],
            total_frames=spec["frames"],
            processed_frames=int(spec["frames"] * spec["progress"]),
            events_count=spec["events"],
            created_at=datetime.now(timezone.utc) - timedelta(hours=random.randint(2, 24)),
            completed_at=datetime.now(timezone.utc) - timedelta(hours=random.randint(1, 2)) if spec["status"] == "completed" else None,
            error_message=spec["err"]
        )
        session.add(job)
    return job_ids


async def seed_database(num_events: int = 50, clear_first: bool = False):
    """Initializes tables and seeds rich operational demo telemetry."""
    print(f"Connecting to database and creating schema tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    async with AsyncSessionLocal() as session:
        if clear_first:
            print("Clearing existing demo records...")
            from sqlalchemy import text
            await session.execute(text("DELETE FROM alert_logs"))
            await session.execute(text("DELETE FROM events"))
            await session.execute(text("DELETE FROM video_jobs"))
            await session.execute(text("DELETE FROM metrics"))
            await session.commit()

        print(f"Seeding camera registry...")
        await seed_cameras(session)

        print(f"Seeding video analysis jobs...")
        await seed_video_jobs(session)

        print(f"Seeding {num_events} multi-factor warehouse events...")
        now = datetime.now(timezone.utc)
        
        # Ensure every behavior type is guaranteed to be seeded at least twice
        guaranteed_templates = BEHAVIOR_TEMPLATES * 2
        remaining_count = max(0, num_events - len(guaranteed_templates))
        chosen_templates = guaranteed_templates + [random.choice(BEHAVIOR_TEMPLATES) for _ in range(remaining_count)]
        random.shuffle(chosen_templates)

        created_events = []
        for i, template in enumerate(chosen_templates):
            cam = random.choice(CAMERAS)
            loc = cam["location"] if random.random() > 0.3 else random.choice(LOCATIONS)
            
            # Spread timestamps over past 48 hours, with higher concentration today
            hours_ago = random.choice([random.uniform(0.1, 8.0), random.uniform(8.0, 24.0), random.uniform(24.0, 48.0)])
            event_ts = now - timedelta(hours=hours_ago)
            
            score_min, score_max = template["score_range"]
            risk_score = float(random.randint(score_min, score_max))
            risk_level = template["default_risk"]
            
            # Evidence dictionary
            evidence_data = template["make_evidence"]()
            evidence_data["scene_confidence"] = round(random.uniform(0.88, 0.99), 2)
            evidence_data["lighting_lux"] = random.randint(450, 750)
            
            obj_id_base = random.randint(10, 80)
            object_ids = [obj_id_base, obj_id_base + 1] if "throw" in template["event_type"] or "stack" in template["event_type"] else [obj_id_base]
            
            vid_start = round(random.uniform(5.0, 95.0), 1)
            vid_end = round(vid_start + random.uniform(2.5, 6.0), 1)
            
            event = Event(
                event_id=f"evt_{uuid.uuid4().hex[:12]}",
                timestamp=event_ts,
                camera_id=cam["camera_id"],
                location=loc,
                event_type=template["event_type"],
                risk_level=risk_level,
                risk_score=risk_score,
                confidence=round(random.uniform(0.85, 0.98), 2),
                object_ids=object_ids,
                video_path="demo/sample_warehouse_feed.mp4",
                video_start=vid_start,
                video_end=vid_end,
                evidence=evidence_data,
                explanation=f"Observed: {template['obs']} Risk Level: {risk_level} (Score: {int(risk_score)}/100). Potential cargo damage or procedural violation.",
                recommendation=template["rec"],
                created_at=event_ts
            )
            session.add(event)
            created_events.append(event)

        await session.flush()

        # Seed high/critical alert logs linked to high/critical events
        print("Seeding real-time alert logs...")
        for ev in created_events:
            if ev.risk_level in ("HIGH", "CRITICAL"):
                is_acknowledged = random.random() > 0.45
                alert = Alert(
                    id=f"alt_{uuid.uuid4().hex[:10]}",
                    event_id=ev.event_id,
                    alert_type="audio_visual",
                    severity=ev.risk_level,
                    message=f"{ev.risk_level} ALERT: {ev.event_type.replace('_', ' ').title()} at {ev.location}",
                    location=ev.location,
                    sent_at=ev.timestamp,
                    acknowledged=is_acknowledged,
                    acknowledged_at=ev.timestamp + timedelta(minutes=random.randint(2, 25)) if is_acknowledged else None,
                    acknowledged_by=random.choice(["Supervisor_Mike", "Lead_Sarah", "Safety_Officer_Chen"]) if is_acknowledged else None
                )
                session.add(alert)

        # Seed hourly warehouse operational metrics
        print("Seeding operational throughput & safety metrics...")
        for h in range(24):
            metric_ts = now - timedelta(hours=h)
            metric1 = Metric(
                id=f"met_{uuid.uuid4().hex[:10]}",
                timestamp=metric_ts,
                metric_name="handling_throughput_cpm",
                metric_value=float(random.randint(45, 95)),
                location="Warehouse Central",
                metadata_json={"cartons_per_minute": random.randint(45, 95)}
            )
            metric2 = Metric(
                id=f"met_{uuid.uuid4().hex[:10]}",
                timestamp=metric_ts,
                metric_name="safety_compliance_pct",
                metric_value=round(random.uniform(91.5, 99.2), 1),
                location="Warehouse Central",
                metadata_json={"target_pct": 98.0}
            )
            session.add(metric1)
            session.add(metric2)

        await session.commit()
        print(f"Successfully seeded database with {len(created_events)} events, alerts, cameras, metrics, and video jobs!")


def main():
    parser = argparse.ArgumentParser(description="AI Warehouse Intelligence - Database Seeder")
    parser.add_argument("--count", "-c", type=int, default=50, help="Number of demo events to generate")
    parser.add_argument("--clear", action="store_true", help="Clear existing data before seeding")
    args = parser.parse_args()

    asyncio.run(seed_database(num_events=args.count, clear_first=args.clear))


if __name__ == "__main__":
    main()
