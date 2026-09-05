# Dataset & Synthetic Data Generator Specification

## 1. Dataset Overview

The AI Warehouse Intelligence dataset includes real-world benchmark annotations and procedurally generated synthetic warehouse video streams designed for temporal behavior recognition, multi-object tracking, and risk assessment during loading/unloading operations.

```
Warehouse Data Pipeline:
  [Synthetic Procedural Generator] ──┐
                                     ├─► [Video Ingestion & Tracking] ─► [Temporal FSM Evaluation]
  [Real-World Benchmark Feeds]     ──┘
```

---

## 2. Video Format & Technical Specifications

| Parameter | Specification |
|---|---|
| **File Formats** | MP4 (`mp4v` / H.264), AVI (`XVID`), RTSP (`rtsp://`), Webcam stream (`0`) |
| **Resolutions** | $640 \times 480$ (Standard), $1280 \times 720$ (HD), $1920 \times 1080$ (Full HD) |
| **Framerate** | $15.0 - 30.0\text{ FPS}$ (Nominal $20.0\text{ FPS}$) |
| **Color Space** | BGR / RGB (8-bit per channel, 24-bit depth) |
| **Duration per Clip** | 5 to 60 seconds (or continuous RTSP stream) |

---

## 3. Annotation Scheme & Object Ontology

### Object Classes:
1. `person` (Class 0): Warehouse personnel, forklift drivers, supervisors.
2. `carton` / `package` (Class 1): Corrugated boxes, parcel bags, freight cartons.
3. `pallet` (Class 2): Standard GMA wooden pallets, Euro-pallets, plastic skids.
4. `forklift` / `vehicle` (Class 3): Counterbalanced forklifts, reach trucks, transport trucks.

### Structured Frame Annotation JSON Schema:
```json
{
  "frame_idx": 45,
  "timestamp_sec": 2.25,
  "camera_id": "CAM-02-BAY2",
  "objects": [
    {
      "track_id": 101,
      "class_name": "person",
      "bbox": [80.0, 172.8, 120.0, 305.0],
      "confidence": 0.94,
      "velocity": [2.2, 0.0]
    },
    {
      "track_id": 102,
      "class_name": "carton",
      "bbox": [116.0, 227.8, 164.0, 265.8],
      "confidence": 0.91,
      "velocity": [2.2, 8.4]
    }
  ],
  "temporal_annotations": [
    {
      "behavior_type": "product_drop",
      "associated_track_ids": [101, 102],
      "start_frame": 25,
      "end_frame": 55,
      "evidence": {
        "drop_height_px": 142.0,
        "impact_velocity_mps": 5.4,
        "product_type": "fragile_electronics"
      }
    }
  ]
}
```

---

## 4. Synthetic Video Generator (`scripts/generate_synthetic_video.py`)

The procedural synthetic generator simulates realistic warehouse dynamics using OpenCV and NumPy vector operations.

### Key Simulation Engines:
- **Kinematic Gravity Simulation**: Simulates downward drop acceleration $y(t) = y_0 + v_{0}t + \frac{1}{2}gt^2$ with floor bounce damping.
- **Parabolic Projectile Motion**: Animates horizontal and vertical throwing trajectories between multiple operators.
- **Surface Drag & Friction Particle Simulation**: Models horizontal floor contact with friction trace lines.
- **Rotational & Tilt Geometry**: Evaluates multi-tier stack stability and pallet diagonal misalignment using rotated contour projections.

### CLI Usage:
```bash
# Generate all 10 behaviors in a continuous montage
python scripts/generate_synthetic_video.py --scenario all --duration 10 --fps 20 --output demo/sample_warehouse_feed.mp4

# Generate specific scenarios
python scripts/generate_synthetic_video.py --scenario drop --duration 5 --output demo/sample_drop.mp4
python scripts/generate_synthetic_video.py --scenario throw --duration 5 --output demo/sample_throw.mp4
python scripts/generate_synthetic_video.py --scenario unstable --duration 5 --output demo/sample_unstable.mp4
```

---

## 5. Data Augmentation Strategies

To enhance robustness under varying real-world industrial dock conditions:

1. **Photometric Augmentations**:
   - Brightness jitter: $\pm 25\%$
   - Contrast variation: factor $0.8 \times - 1.3 \times$
   - Additive Gaussian Noise: $\sigma \in [0.01, 0.05]$
   - Motion blur kernels: $3 \times 3$ to $7 \times 7$ simulating fast camera pan.
2. **Geometric Augmentations**:
   - Perspective warping simulating varied dock camera mounting angles ($15^\circ - 45^\circ$).
   - Horizontal flipping.
   - Dynamic scaling ($0.85\times - 1.15\times$).

---

## 6. Privacy & Ethical Data Governance

- **Zero Biometric Collection**: Training and evaluation datasets contain no facial landmark data, retina scans, or individual identity labels.
- **Anonymization**: All operator depictions use safety helmets, high-vis vests, and non-identifying silhouettes.
