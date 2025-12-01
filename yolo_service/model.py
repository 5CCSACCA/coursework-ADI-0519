from pathlib import Path

from ultralytics import YOLO

from .detections import Detection


class YOLOPredictor:
    def __init__(self, weights="yolo11n.pt", min_conf=0.25):
        self.model = YOLO(weights)
        self.min_conf = min_conf

    def predict(self, img_path):
        path = Path(img_path)
        if not path.is_file():
            raise FileNotFoundError("Image not found")

        results = self.model(str(path))

        detections = []

        for result in results:
            for box in result.boxes:
                conf = float(box.conf[0])
                if conf < self.min_conf:
                    continue

                cls_id = int(box.cls[0])
                label = self.model.names[cls_id]
                x1, y1, x2, y2 = box.xyxy[0].tolist()

                detections.append(
                    Detection(
                        label=label,
                        confidence=conf,
                        x1=x1,
                        y1=y1,
                        x2=x2,
                        y2=y2,
                    )
                )

        return detections
