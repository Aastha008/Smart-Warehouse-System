"""
AI Warehouse Intelligence - Model Validation
Validates model performance on validation/test sets.
"""
import json
import sys
from pathlib import Path
from datetime import datetime


def validate(
    model_path: str = "yolov8s.pt",
    data_yaml: str = None,
    img_size: int = 640,
    split: str = "val",
) -> dict:
    """Validate model and return metrics."""
    try:
        from ultralytics import YOLO

        model = YOLO(model_path)

        if data_yaml and Path(data_yaml).exists():
            results = model.val(data=data_yaml, imgsz=img_size, split=split)
            metrics = {
                "model": model_path,
                "split": split,
                "precision": float(results.results_dict.get("metrics/precision(B)", 0)),
                "recall": float(results.results_dict.get("metrics/recall(B)", 0)),
                "mAP50": float(results.results_dict.get("metrics/mAP50(B)", 0)),
                "mAP50_95": float(results.results_dict.get("metrics/mAP50-95(B)", 0)),
                "f1": 0.0,
            }
            # Calculate F1
            if metrics["precision"] + metrics["recall"] > 0:
                metrics["f1"] = (
                    2 * metrics["precision"] * metrics["recall"]
                    / (metrics["precision"] + metrics["recall"])
                )
        else:
            # Validate pretrained model on COCO val
            print(f"No custom dataset provided. Testing pretrained model info.")
            info = model.info()
            metrics = {
                "model": model_path,
                "split": "pretrained_coco",
                "status": "pretrained_model",
                "note": "Using pretrained COCO weights. No custom validation set available.",
                "model_type": str(type(model)),
                "classes": len(model.names) if hasattr(model, 'names') else "unknown",
            }

        metrics["timestamp"] = datetime.now().isoformat()
        return metrics

    except Exception as e:
        return {
            "model": model_path,
            "error": str(e),
            "status": "failed",
            "timestamp": datetime.now().isoformat(),
        }


def measure_inference_latency(
    model_path: str = "yolov8s.pt",
    img_size: int = 640,
    num_warmup: int = 5,
    num_iterations: int = 50,
) -> dict:
    """Measure inference latency."""
    import time
    import numpy as np

    try:
        from ultralytics import YOLO

        model = YOLO(model_path)

        # Create dummy image
        dummy_img = np.random.randint(0, 255, (img_size, img_size, 3), dtype=np.uint8)

        # Warmup
        for _ in range(num_warmup):
            model(dummy_img, verbose=False)

        # Measure
        latencies = []
        for _ in range(num_iterations):
            start = time.perf_counter()
            model(dummy_img, verbose=False)
            end = time.perf_counter()
            latencies.append((end - start) * 1000)  # ms

        latency_info = {
            "model": model_path,
            "img_size": img_size,
            "num_iterations": num_iterations,
            "mean_latency_ms": round(float(np.mean(latencies)), 2),
            "median_latency_ms": round(float(np.median(latencies)), 2),
            "min_latency_ms": round(float(np.min(latencies)), 2),
            "max_latency_ms": round(float(np.max(latencies)), 2),
            "std_latency_ms": round(float(np.std(latencies)), 2),
            "estimated_fps": round(1000 / float(np.mean(latencies)), 1),
            "timestamp": datetime.now().isoformat(),
        }

        return latency_info

    except Exception as e:
        return {"error": str(e), "status": "failed"}


def main():
    """Run validation."""
    print("=" * 60)
    print("AI Warehouse Intelligence - Model Validation")
    print("=" * 60)

    model_path = sys.argv[1] if len(sys.argv) > 1 else "yolov8s.pt"
    data_yaml = sys.argv[2] if len(sys.argv) > 2 else None

    # Validate
    print(f"\n📊 Validating model: {model_path}")
    metrics = validate(model_path, data_yaml)
    print(json.dumps(metrics, indent=2))

    # Measure latency
    print(f"\n⏱️ Measuring inference latency...")
    latency = measure_inference_latency(model_path)
    print(json.dumps(latency, indent=2))

    # Save report
    report = {
        "validation_metrics": metrics,
        "inference_latency": latency,
    }

    report_path = Path("training/validation_report.json")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)

    print(f"\n✅ Validation report saved: {report_path}")


if __name__ == "__main__":
    main()
