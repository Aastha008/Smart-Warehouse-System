"""
AI Warehouse Intelligence - Model Export
Export trained models to deployment formats.
"""
import sys
import json
from pathlib import Path
from datetime import datetime


def export_model(
    model_path: str = "yolov8s.pt",
    formats: list[str] = None,
    img_size: int = 640,
) -> dict:
    """Export model to various formats."""
    if formats is None:
        formats = ["onnx"]

    results = {}

    try:
        from ultralytics import YOLO

        model = YOLO(model_path)

        for fmt in formats:
            try:
                print(f"Exporting to {fmt}...")
                export_path = model.export(format=fmt, imgsz=img_size)
                results[fmt] = {
                    "status": "success",
                    "path": str(export_path),
                }
                print(f"  ✅ Exported: {export_path}")
            except Exception as e:
                results[fmt] = {
                    "status": "failed",
                    "error": str(e),
                }
                print(f"  ❌ Failed: {e}")

    except Exception as e:
        results["error"] = str(e)

    results["timestamp"] = datetime.now().isoformat()
    return results


def main():
    """Export model."""
    model_path = sys.argv[1] if len(sys.argv) > 1 else "yolov8s.pt"
    formats = sys.argv[2].split(",") if len(sys.argv) > 2 else ["onnx"]

    print("=" * 60)
    print("AI Warehouse Intelligence - Model Export")
    print("=" * 60)

    results = export_model(model_path, formats)
    print(json.dumps(results, indent=2))

    # Save export report
    report_path = Path("training/export_report.json")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, "w") as f:
        json.dump(results, f, indent=2)


if __name__ == "__main__":
    main()
