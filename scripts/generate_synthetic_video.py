"""
AI Warehouse Intelligence - Synthetic Warehouse Video Generator
Generates realistic synthetic video streams and files for warehouse loading/unloading operations.
Supports 10+ temporal behavior scenarios: drop, drag, throw, rough handling, stacking,
unstable stack, zone violation, pallet misalignment, sequence anomaly, equipment misuse,
and multi-scenario warehouse demo montages.
"""
import os
import cv2
import math
import random
import argparse
import numpy as np
from datetime import datetime, timezone


def draw_warehouse_background(frame: np.ndarray, width: int, height: int, bay_name: str = "LOADING BAY 2"):
    """Draws warehouse structural elements: dock walls, concrete floor, safety zones, racking."""
    # Wall (top half) - light industrial blue-gray
    cv2.rectangle(frame, (0, 0), (width, int(height * 0.6)), (215, 218, 222), -1)
    
    # Wall panels / dock door outline
    door_w, door_h = int(width * 0.45), int(height * 0.55)
    door_x = int(width * 0.08)
    cv2.rectangle(frame, (door_x, int(height * 0.05)), (door_x + door_w, int(height * 0.6)), (180, 185, 190), -1)
    cv2.rectangle(frame, (door_x, int(height * 0.05)), (door_x + door_w, int(height * 0.6)), (130, 135, 140), 2)
    # Roll-up door horizontal slats
    for y_slat in range(int(height * 0.08), int(height * 0.6), 25):
        cv2.line(frame, (door_x, y_slat), (door_x + door_w, y_slat), (150, 155, 160), 1)

    # Concrete floor (bottom 40%)
    floor_y = int(height * 0.6)
    cv2.rectangle(frame, (0, floor_y), (width, height), (140, 145, 150), -1)
    # Floor expansion joints / perspective lines
    cv2.line(frame, (0, floor_y), (width, floor_y), (100, 105, 110), 3)
    cv2.line(frame, (int(width * 0.3), floor_y), (0, height), (120, 125, 130), 1)
    cv2.line(frame, (int(width * 0.7), floor_y), (width, height), (120, 125, 130), 1)

    # Industrial storage racking on right side
    rack_x = int(width * 0.78)
    cv2.rectangle(frame, (rack_x, int(height * 0.1)), (rack_x + 8, floor_y), (50, 90, 200), -1) # Blue upright
    cv2.rectangle(frame, (width - 15, int(height * 0.1)), (width - 7, floor_y), (50, 90, 200), -1)
    # Orange shelf beams
    for beam_y in [int(height * 0.25), int(height * 0.42), floor_y - 8]:
        cv2.rectangle(frame, (rack_x, beam_y), (width - 7, beam_y + 8), (30, 130, 240), -1)

    # Yellow safety boundary marking
    zone_x1, zone_y1 = int(width * 0.08), int(height * 0.65)
    zone_x2, zone_y2 = int(width * 0.62), int(height * 0.94)
    cv2.rectangle(frame, (zone_x1, zone_y1), (zone_x2, zone_y2), (0, 215, 255), 2)
    
    # Red-striped pedestrian hazard zone on bottom left
    haz_x1, haz_y1 = int(width * 0.02), int(height * 0.75)
    haz_x2, haz_y2 = int(width * 0.25), int(height * 0.98)
    for hx in range(haz_x1, haz_x2, 20):
        cv2.line(frame, (hx, haz_y1), (hx + 15, haz_y2), (0, 0, 180), 2)
    cv2.rectangle(frame, (haz_x1, haz_y1), (haz_x2, haz_y2), (0, 0, 200), 2)
    cv2.putText(frame, "PEDESTRIAN WALKWAY", (haz_x1 + 4, haz_y1 + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 200), 1)

    # Staging zone label
    cv2.putText(frame, bay_name, (zone_x1 + 10, zone_y1 + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 180, 230), 1)


def draw_pallet(frame: np.ndarray, x: int, y: int, w: int = 110, h: int = 30, angle_deg: float = 0.0):
    """Draws a wooden logistics pallet with top planks, bottom runners, and optional rotation."""
    wood_color = (90, 130, 170)
    wood_dark = (60, 90, 130)
    
    if abs(angle_deg) < 1.0:
        # Top deck planks
        cv2.rectangle(frame, (x, y), (x + w, y + 10), wood_color, -1)
        cv2.rectangle(frame, (x, y), (x + w, y + 10), wood_dark, 1)
        # 3 Stringer blocks
        block_w = 16
        for bx in [x + 5, x + w // 2 - block_w // 2, x + w - block_w - 5]:
            cv2.rectangle(frame, (bx, y + 10), (bx + block_w, y + h - 6), wood_dark, -1)
        # Bottom deck planks
        cv2.rectangle(frame, (x, y + h - 6), (x + w, y + h), wood_color, -1)
        cv2.rectangle(frame, (x, y + h - 6), (x + w, y + h), wood_dark, 1)
        cv2.putText(frame, "PALLET", (x + w // 4, y + h - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255, 255, 255), 1)
    else:
        # Rotated pallet representation
        rect = ((x + w / 2, y + h / 2), (w, h), angle_deg)
        box = cv2.boxPoints(rect)
        box = np.int32(box)
        cv2.drawContours(frame, [box], 0, wood_color, -1)
        cv2.drawContours(frame, [box], 0, wood_dark, 2)
        cv2.putText(frame, "PALLET (MISALIGNED)", (x - 20, y - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 220), 1)


def draw_carton(frame: np.ndarray, x: int, y: int, w: int = 50, h: int = 40, label: str = "CARTON", color=None, tilt_deg: float = 0.0):
    """Draws an industrial cardboard carton box with tape, barcode, and optional tilt."""
    cardboard = color if color is not None else (70, 140, 190)
    border = (40, 90, 140)
    tape = (50, 180, 220)
    
    if abs(tilt_deg) < 1.0:
        cv2.rectangle(frame, (x, y), (x + w, y + h), cardboard, -1)
        cv2.rectangle(frame, (x, y), (x + w, y + h), border, 2)
        # Center packing tape stripe
        cv2.line(frame, (x + w // 2, y), (x + w // 2, y + h), tape, 3)
        # Barcode label patch
        cv2.rectangle(frame, (x + 6, y + 8), (x + 24, y + 20), (250, 250, 250), -1)
        cv2.putText(frame, label, (x + 4, y + h - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.32, (20, 50, 80), 1)
    else:
        rect = ((x + w / 2, y + h / 2), (w, h), tilt_deg)
        box = cv2.boxPoints(rect)
        box = np.int32(box)
        cv2.drawContours(frame, [box], 0, cardboard, -1)
        cv2.drawContours(frame, [box], 0, border, 2)
        cv2.putText(frame, f"{label} (TILT)", (x - 10, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.32, (0, 50, 200), 1)


def draw_worker(frame: np.ndarray, x: int, y: int, action: str = "standing", carrying: bool = False, facing_right: bool = True):
    """Draws a warehouse operator with hard hat, high-vis safety vest, limbs, and movement posture."""
    # Hard hat (Yellow)
    hat_color = (0, 215, 255)
    cv2.ellipse(frame, (x + 20, y + 12), (14, 10), 0, 180, 360, hat_color, -1)
    cv2.rectangle(frame, (x + 4, y + 10), (x + 36, y + 14), hat_color, -1)
    
    # Head (skin tone)
    cv2.circle(frame, (x + 20, y + 22), 10, (160, 190, 225), -1)
    
    # High-vis safety vest torso (Fluorescent Orange / Lime)
    vest_color = (20, 100, 240)
    silver_stripe = (230, 230, 230)
    cv2.rectangle(frame, (x + 8, y + 32), (x + 32, y + 82), vest_color, -1)
    cv2.line(frame, (x + 8, y + 48), (x + 32, y + 48), silver_stripe, 2)
    cv2.line(frame, (x + 8, y + 64), (x + 32, y + 64), silver_stripe, 2)
    
    # Legs (Work trousers - Navy/Dark Gray)
    trouser_color = (80, 60, 40)
    cv2.rectangle(frame, (x + 9, y + 82), (x + 18, y + 125), trouser_color, -1)
    cv2.rectangle(frame, (x + 22, y + 82), (x + 31, y + 125), trouser_color, -1)
    # Steel-toe safety boots (Black)
    cv2.rectangle(frame, (x + 6, y + 125), (x + 19, y + 132), (20, 20, 20), -1)
    cv2.rectangle(frame, (x + 21, y + 125), (x + 34, y + 132), (20, 20, 20), -1)

    # Arms
    arm_color = (160, 190, 225)
    if carrying:
        arm_end_x = x + 42 if facing_right else x - 10
        cv2.line(frame, (x + 24, y + 40), (arm_end_x, y + 58), arm_color, 4)
    elif action == "throwing":
        cv2.line(frame, (x + 24, y + 40), (x + 48, y + 26), arm_color, 4)
    elif action == "dragging":
        cv2.line(frame, (x + 12, y + 45), (x - 18, y + 88), arm_color, 4)
    else:
        cv2.line(frame, (x + 10, y + 36), (x + 6, y + 70), arm_color, 4)
        cv2.line(frame, (x + 30, y + 36), (x + 34, y + 70), arm_color, 4)

    # Label
    cv2.putText(frame, "OPERATOR", (x - 6, y - 4), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (30, 30, 30), 1)


def draw_forklift(frame: np.ndarray, x: int, y: int, w: int = 140, h: int = 90, carrying_load: bool = True):
    """Draws an industrial warehouse forklift truck."""
    chassis_yellow = (20, 180, 240)
    steel_gray = (60, 60, 60)
    
    # Counterweight body
    cv2.rectangle(frame, (x, y + 30), (x + 90, y + h - 15), chassis_yellow, -1)
    cv2.rectangle(frame, (x, y + 30), (x + 90, y + h - 15), (10, 120, 180), 2)
    # Overhead safety cage (ROPS)
    cv2.line(frame, (x + 25, y + 30), (x + 25, y), steel_gray, 3)
    cv2.line(frame, (x + 70, y + 30), (x + 70, y), steel_gray, 3)
    cv2.line(frame, (x + 20, y), (x + 75, y), steel_gray, 4)
    # Mast on front (right side)
    cv2.rectangle(frame, (x + 90, y - 20), (x + 100, y + h - 10), steel_gray, -1)
    # Forks extending forward
    fork_y = y + h - 18
    cv2.line(frame, (x + 98, fork_y), (x + 145, fork_y), steel_gray, 4)
    
    # Wheels
    cv2.circle(frame, (x + 25, y + h - 10), 14, (30, 30, 30), -1)
    cv2.circle(frame, (x + 25, y + h - 10), 6, (120, 120, 120), -1)
    cv2.circle(frame, (x + 80, y + h - 10), 14, (30, 30, 30), -1)
    cv2.circle(frame, (x + 80, y + h - 10), 6, (120, 120, 120), -1)

    if carrying_load:
        draw_pallet(frame, x + 98, fork_y - 20, w=45, h=18)
        draw_carton(frame, x + 102, fork_y - 48, w=36, h=28, label="CARGO")

    cv2.putText(frame, "FORKLIFT #2", (x + 10, y + 55), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (0, 0, 0), 1)


def draw_osd_telemetry(frame: np.ndarray, frame_idx: int, fps: float, scenario_name: str):
    """Overlays real-time camera metadata, timestamp, frame counter, and AI monitoring status."""
    h, w = frame.shape[:2]
    cv2.rectangle(frame, (0, 0), (w, 28), (20, 20, 20), -1)
    
    time_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    sec_elapsed = frame_idx / max(fps, 1.0)
    
    osd_left = f"CAM-02-DOCK | {time_str} | T+{sec_elapsed:05.2f}s | F#{frame_idx:04d}"
    cv2.putText(frame, osd_left, (8, 19), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (0, 255, 200), 1)
    
    osd_right = f"SCENARIO: {scenario_name.upper()} | AI INTEL ACTIVE"
    cv2.putText(frame, osd_right, (w - 310, 19), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (0, 220, 255), 1)


def generate_scenario_frames(scenario: str, total_frames: int, fps: float, width: int, height: int):
    """Generates a stream of frames tailored to a specific warehouse behavior scenario."""
    frames = []
    
    for f in range(total_frames):
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        draw_warehouse_background(frame, width, height, bay_name=f"DOCK BAY 2 [{scenario.upper()}]")
        
        pallet_x, pallet_y = int(width * 0.65), int(height * 0.72)
        draw_pallet(frame, pallet_x, pallet_y)

        if scenario == "drop":
            p_x = 80 + int(f * 2.2)
            p_y = int(height * 0.36)
            box_x = p_x + 36
            if f < 25:
                box_y = p_y + 55
                draw_worker(frame, p_x, p_y, action="walking", carrying=True)
                draw_carton(frame, box_x, box_y, w=48, h=38, label="FRAGILE")
            else:
                draw_worker(frame, p_x, p_y, action="standing", carrying=False)
                t_fall = f - 25
                v_y = 3.5 * t_fall + 0.5 * 1.8 * (t_fall ** 2)
                box_y = min(p_y + 55 + int(v_y), int(height * 0.82))
                draw_carton(frame, box_x, box_y, w=48, h=38, label="DROPPED", color=(50, 50, 220))
                if box_y >= int(height * 0.82):
                    cv2.putText(frame, "! IMPACT DETECTED !", (box_x - 30, box_y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 2)

        elif scenario == "drag":
            p_x = 100 + int(f * 2.8)
            p_y = int(height * 0.36)
            draw_worker(frame, p_x, p_y, action="dragging", carrying=False)
            drag_box_x = p_x - 55
            drag_box_y = int(height * 0.78)
            cv2.line(frame, (p_x + 12, p_y + 45), (drag_box_x + 40, drag_box_y + 10), (30, 30, 30), 2)
            draw_carton(frame, drag_box_x, drag_box_y, w=55, h=36, label="DRAGGED", color=(60, 100, 200))
            for dx in range(drag_box_x - 30, drag_box_x, 8):
                cv2.circle(frame, (dx, drag_box_y + 30), 2, (100, 100, 100), -1)

        elif scenario == "throw":
            p1_x, p1_y = 60, int(height * 0.36)
            p2_x, p2_y = int(width * 0.75), int(height * 0.36)
            draw_worker(frame, p1_x, p1_y, action="throwing" if f < 25 else "standing", carrying=(f < 15))
            draw_worker(frame, p2_x, p2_y, action="standing", carrying=False, facing_right=False)
            if f < 15:
                draw_carton(frame, p1_x + 36, p1_y + 45, w=42, h=34, label="TOSS")
            elif f < 60:
                t_throw = (f - 15) / 45.0
                bx = int(p1_x + 40 + t_throw * (p2_x - p1_x - 20))
                arc_h = 90.0 * math.sin(t_throw * math.pi)
                by = int((p1_y + 45) - arc_h)
                draw_carton(frame, bx, by, w=42, h=34, label="THROW", color=(30, 40, 230))
                cv2.putText(frame, "HIGH VELOCITY TOSS", (bx - 20, by - 12), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)
            else:
                draw_carton(frame, p2_x - 30, p2_y + 55, w=42, h=34, label="RECEIVED")

        elif scenario == "rough":
            p_x = 180
            p_y = int(height * 0.36)
            draw_worker(frame, p_x, p_y, action="standing", carrying=True)
            jerk = int(25 * math.sin(f * 0.8)) if 20 < f < 60 else 0
            draw_carton(frame, p_x + 38 + jerk, p_y + 55 + (jerk // 2), w=50, h=40, label="ROUGH", color=(40, 60, 210))

        elif scenario == "stack":
            draw_carton(frame, pallet_x + 25, pallet_y - 25, w=30, h=25, label="SMALL")
            draw_carton(frame, pallet_x + 10, pallet_y - 75, w=65, h=50, label="HEAVY", color=(40, 50, 200))
            cv2.putText(frame, "OVERHANG / INVERTED WEIGHT", (pallet_x - 35, pallet_y - 85), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)

        elif scenario == "unstable":
            draw_carton(frame, pallet_x + 25, pallet_y - 30, w=48, h=30, label="BASE")
            wobble = 2.0 * math.sin(f * 0.4)
            draw_carton(frame, pallet_x + 28, pallet_y - 68, w=48, h=32, label="BOX-2", tilt_deg=18.0 + wobble)
            draw_carton(frame, pallet_x + 32, pallet_y - 105, w=46, h=32, label="BOX-3", tilt_deg=24.0 + wobble)

        elif scenario == "zone":
            p_x, p_y = 60, int(height * 0.36)
            draw_worker(frame, p_x, p_y, action="standing", carrying=False)
            draw_carton(frame, int(width * 0.08), int(height * 0.82), w=55, h=42, label="PROHIBITED", color=(0, 0, 220))
            cv2.putText(frame, "WALKWAY VIOLATION", (int(width * 0.04), int(height * 0.80) - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (0, 0, 255), 2)

        elif scenario == "pallet":
            draw_pallet(frame, int(width * 0.35), int(height * 0.68), w=120, h=40, angle_deg=35.0)
            draw_forklift(frame, int(width * 0.02) + int(f * 1.5), int(height * 0.58), carrying_load=False)

        elif scenario == "sequence":
            rack_x = int(width * 0.78)
            draw_carton(frame, rack_x + 4, int(height * 0.16), w=44, h=35, label="TOP-HEAVY", color=(50, 70, 210))
            cv2.putText(frame, "BOTTOM RACK EMPTY", (rack_x - 110, int(height * 0.40)), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (0, 100, 240), 1)

        elif scenario == "equipment":
            p_x, p_y = 160, int(height * 0.36)
            draw_worker(frame, p_x, p_y, action="standing", carrying=True)
            draw_carton(frame, p_x + 35, p_y + 40, w=85, h=75, label="120KG OVERWEIGHT", color=(0, 0, 200))

        else:
            p_x = 60 + int((f % 120) * 2.2)
            p_y = int(height * 0.36)
            draw_worker(frame, p_x, p_y, action="walking", carrying=True)
            draw_carton(frame, p_x + 36, p_y + 55, w=44, h=35, label="CARGO")
            fl_x = int(width * 0.02) + int((f % 180) * 1.8)
            draw_forklift(frame, fl_x, int(height * 0.58), carrying_load=True)

        draw_osd_telemetry(frame, f, fps, scenario)
        frames.append(frame)
        
    return frames


def generate_synthetic_video(
    output_path: str = "demo/sample_warehouse_feed.mp4",
    scenario: str = "all",
    duration_sec: int = 10,
    fps: int = 20,
    width: int = 640,
    height: int = 480,
    seed: int = 42
) -> str:
    random.seed(seed)
    np.random.seed(seed)
    
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    writer = cv2.VideoWriter(output_path, fourcc, float(fps), (width, height))
    
    if not writer.isOpened():
        alt_path = os.path.splitext(output_path)[0] + ".avi"
        fourcc_avi = cv2.VideoWriter_fourcc(*'XVID')
        writer = cv2.VideoWriter(alt_path, fourcc_avi, float(fps), (width, height))
        output_path = alt_path

    if scenario == "all":
        sub_scenarios = ["drop", "drag", "throw", "rough", "stack", "unstable", "zone", "pallet", "sequence", "equipment"]
        frames_per_sub = max(int((duration_sec * fps) / len(sub_scenarios)), 15)
        total_written = 0
        for sub in sub_scenarios:
            sub_frames = generate_scenario_frames(sub, frames_per_sub, fps, width, height)
            for fr in sub_frames:
                writer.write(fr)
                total_written += 1
    else:
        total_frames = int(duration_sec * fps)
        frames = generate_scenario_frames(scenario, total_frames, fps, width, height)
        for fr in frames:
            writer.write(fr)
        total_written = len(frames)

    writer.release()
    print(f"Successfully generated synthetic video [{scenario}]: {output_path} ({total_written} frames, {width}x{height} @ {fps}fps)")
    return output_path


def main():
    parser = argparse.ArgumentParser(description="AI Warehouse Intelligence - Synthetic Video Generator")
    parser.add_argument("--output", "-o", type=str, default="demo/sample_warehouse_feed.mp4", help="Output video filepath")
    parser.add_argument("--scenario", "-s", type=str, default="all", 
                        choices=["all", "drop", "drag", "throw", "rough", "stack", "unstable", "zone", "pallet", "sequence", "equipment"],
                        help="Behavior scenario to simulate")
    parser.add_argument("--duration", "-d", type=int, default=10, help="Duration in seconds")
    parser.add_argument("--fps", type=int, default=20, help="Frames per second")
    parser.add_argument("--width", type=int, default=640, help="Frame width in pixels")
    parser.add_argument("--height", type=int, default=480, help="Frame height in pixels")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    
    args = parser.parse_args()
    generate_synthetic_video(
        output_path=args.output,
        scenario=args.scenario,
        duration_sec=args.duration,
        fps=args.fps,
        width=args.width,
        height=args.height,
        seed=args.seed
    )


if __name__ == "__main__":
    main()
