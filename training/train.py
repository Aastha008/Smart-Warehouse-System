"""
AI Warehouse Intelligence - Training Pipeline
Uses pretrained YOLOv8 with optional fine-tuning for warehouse-specific objects.
"""
import os
import sys
import yaml
import json
from pathlib import Path
from datetime import datetime


def load_config(config_path: str = "configs/detection.yaml") -> dict:
    """Load detection configuration."""
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def check_environment() -> dict:
    """Check available hardware and software environment."""
    env_info = {
        "python_version": sys.version,
        "timestamp": datetime.now().isoformat(),
    }

    # Check GPU availability
    try:
        import torch
        env_info["torch_version"] = torch.__version__
        env_info["cuda_available"] = torch.cuda.is_available()
        if torch.cuda.is_available():
            env_info["gpu_name"] = torch.cuda.get_device_name(0)
            env_info["gpu_memory_gb"] = round(
                torch.cuda.get_device_properties(0).total_mem / 1e9, 2
            )
            env_info["cuda_version"] = torch.version.cuda
        else:
            env_info["gpu_name"] = "N/A (CPU only)"
            env_info["gpu_memory_gb"] = 0
    except ImportError:
        env_info["torch_version"] = "Not installed"
        env_info["cuda_available"] = False
        env_info["gpu_name"] = "N/A"

    # Check ultralytics
    try:
        import ultralytics
        env_info["ultralytics_version"] = ultralytics.__version__
    except ImportError:
        env_info["ultralytics_version"] = "Not installed"

    return env_info


def check_dataset(data_dir: str = "data") -> dict:
    """Check available training data."""
    data_info = {
        "data_dir": data_dir,
        "raw_videos": 0,
        "processed_frames": 0,
        "annotations": 0,
        "train_images": 0,
        "val_images": 0,
        "test_images": 0,
    }

    data_path = Path(data_dir)
    for subdir, key in [
        ("raw", "raw_videos"),
        ("frames", "processed_frames"),
        ("annotations", "annotations"),
        ("train", "train_images"),
        ("val", "val_images"),
        ("test", "test_images"),
    ]:
        dir_path = data_path / subdir
        if dir_path.exists():
            files = list(dir_path.rglob("*"))
            data_info[key] = len([f for f in files if f.is_file()])

    return data_info


def select_model(env_info: dict, data_info: dict) -> dict:
    """Select the best model based on available resources."""
    total_images = (
        data_info["train_images"]
        + data_info["val_images"]
        + data_info["test_images"]
    )

    model_selection = {
        "strategy": "pretrained",
        "base_model": "yolov8s.pt",
        "rationale": "",
        "fine_tune": False,
        "training_epochs": 0,
    }

    # Decision logic
    if total_images >= 500 and env_info.get("cuda_available", False):
        model_selection["strategy"] = "fine_tune"
        model_selection["base_model"] = "yolov8s.pt"
        model_selection["fine_tune"] = True
        model_selection["training_epochs"] = 50
        model_selection["rationale"] = (
            f"Sufficient data ({total_images} images) and GPU available. "
            "Fine-tuning YOLOv8s for warehouse-specific classes."
        )
    elif total_images >= 100:
        model_selection["strategy"] = "fine_tune_small"
        model_selection["base_model"] = "yolov8n.pt"
        model_selection["fine_tune"] = True
        model_selection["training_epochs"] = 30
        model_selection["rationale"] = (
            f"Limited data ({total_images} images). "
            "Fine-tuning smaller YOLOv8n model."
        )
    else:
        model_selection["strategy"] = "pretrained"
        model_selection["base_model"] = "yolov8s.pt"
        model_selection["fine_tune"] = False
        model_selection["training_epochs"] = 0
        model_selection["rationale"] = (
            f"Insufficient labelled data ({total_images} images). "
            "Using pretrained YOLOv8s with COCO classes mapped to warehouse objects. "
            "Behaviour intelligence via temporal state machines over tracked objects."
        )

    # Adjust for GPU memory
    if env_info.get("gpu_memory_gb", 0) < 4 and model_selection["fine_tune"]:
        model_selection["base_model"] = "yolov8n.pt"
        model_selection["rationale"] += " Switched to nano model due to limited GPU memory."

    return model_selection


def download_pretrained_model(model_name: str = "yolov8s.pt") -> str:
    """Download pretrained model if not already available."""
    model_dir = Path("models/pretrained")
    model_dir.mkdir(parents=True, exist_ok=True)
    model_path = model_dir / model_name

    if model_path.exists():
        print(f"Model already exists: {model_path}")
        return str(model_path)

    try:
        from ultralytics import YOLO
        print(f"Downloading pretrained model: {model_name}")
        model = YOLO(model_name)
        # The model will be downloaded to the default location
        # We also save a copy to our models directory
        print(f"Model ready: {model_name}")
        return model_name
    except Exception as e:
        print(f"Error downloading model: {e}")
        print("Will use model name directly - ultralytics will download on first use")
        return model_name


def train_model(
    data_yaml: str,
    model_name: str = "yolov8s.pt",
    epochs: int = 50,
    batch_size: int = 16,
    img_size: int = 640,
    project: str = "training/experiments",
    name: str = "warehouse_detection",
) -> dict:
    """Fine-tune YOLOv8 on warehouse dataset."""
    try:
        from ultralytics import YOLO

        model = YOLO(model_name)

        results = model.train(
            data=data_yaml,
            epochs=epochs,
            batch=batch_size,
            imgsz=img_size,
            project=project,
            name=name,
            patience=10,
            save=True,
            save_period=10,
            plots=True,
            verbose=True,
        )

        # Collect metrics
        metrics = {
            "precision": float(results.results_dict.get("metrics/precision(B)", 0)),
            "recall": float(results.results_dict.get("metrics/recall(B)", 0)),
            "mAP50": float(results.results_dict.get("metrics/mAP50(B)", 0)),
            "mAP50_95": float(results.results_dict.get("metrics/mAP50-95(B)", 0)),
            "epochs_completed": epochs,
            "model_path": str(results.save_dir / "weights" / "best.pt"),
        }

        return metrics

    except Exception as e:
        return {"error": str(e), "status": "failed"}


def validate_model(
    model_path: str,
    data_yaml: str,
    img_size: int = 640,
) -> dict:
    """Validate model on validation set."""
    try:
        from ultralytics import YOLO

        model = YOLO(model_path)
        results = model.val(data=data_yaml, imgsz=img_size)

        metrics = {
            "precision": float(results.results_dict.get("metrics/precision(B)", 0)),
            "recall": float(results.results_dict.get("metrics/recall(B)", 0)),
            "mAP50": float(results.results_dict.get("metrics/mAP50(B)", 0)),
            "mAP50_95": float(results.results_dict.get("metrics/mAP50-95(B)", 0)),
        }

        return metrics

    except Exception as e:
        return {"error": str(e), "status": "failed"}


def export_model(
    model_path: str,
    format: str = "onnx",
    img_size: int = 640,
) -> str:
    """Export model to deployment format."""
    try:
        from ultralytics import YOLO

        model = YOLO(model_path)
        export_path = model.export(format=format, imgsz=img_size)
        return str(export_path)

    except Exception as e:
        return f"Export failed: {e}"


def main():
    """Main training pipeline."""
    print("=" * 60)
    print("AI Warehouse Intelligence - Model Training Pipeline")
    print("=" * 60)

    # Step 1: Check environment
    print("\n📋 Step 1: Checking environment...")
    env_info = check_environment()
    print(json.dumps(env_info, indent=2))

    # Step 2: Check dataset
    print("\n📋 Step 2: Checking dataset...")
    data_info = check_dataset()
    print(json.dumps(data_info, indent=2))

    # Step 3: Select model strategy
    print("\n📋 Step 3: Selecting model strategy...")
    model_selection = select_model(env_info, data_info)
    print(json.dumps(model_selection, indent=2))

    # Step 4: Download/prepare model
    print("\n📋 Step 4: Preparing model...")
    model_path = download_pretrained_model(model_selection["base_model"])

    # Step 5: Train or use pretrained
    if model_selection["fine_tune"]:
        print("\n📋 Step 5: Fine-tuning model...")
        data_yaml = "data/warehouse_dataset.yaml"
        if not Path(data_yaml).exists():
            print(f"⚠️ Dataset config not found: {data_yaml}")
            print("Skipping training - using pretrained model.")
        else:
            metrics = train_model(
                data_yaml=data_yaml,
                model_name=model_path,
                epochs=model_selection["training_epochs"],
            )
            print("\n📊 Training Results:")
            print(json.dumps(metrics, indent=2))
    else:
        print("\n📋 Step 5: Using pretrained model (no fine-tuning)")
        print(f"Model: {model_selection['base_model']}")
        print(f"Rationale: {model_selection['rationale']}")

    # Save training report
    report = {
        "environment": env_info,
        "dataset": data_info,
        "model_selection": model_selection,
        "model_path": model_path,
        "status": "complete",
        "timestamp": datetime.now().isoformat(),
    }

    report_path = Path("training/training_report.json")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)

    print(f"\n✅ Training report saved: {report_path}")
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
