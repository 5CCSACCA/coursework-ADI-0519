import argparse
from pathlib import Path

from .model import YOLOPredictor


def main():
    parser = argparse.ArgumentParser(description="Run YOLO11n on a single image.")
    parser.add_argument("image", type=str, help="Path to an image file.")
    parser.add_argument(
        "--min-conf",
        type=float,
        default=0.25,
        help="Minimum confidence threshold",
    )

    args = parser.parse_args()

    image_path = Path(args.image)

    predictor = YOLOPredictor(min_conf=args.min_conf)
    detections = predictor.predict(str(image_path))

    print(f"Detections for {image_path}:")
    if not detections:
        print("  (no objects detected)")

    for det in detections:
        label = det.label
        conf = det.confidence
        print(f"  - {label:15s} conf={conf:.2f}")


if __name__ == "__main__":
    main()
