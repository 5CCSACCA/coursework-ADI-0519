import tempfile
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile

from yolo_service.model import YOLOPredictor

app = FastAPI(
    title="YOLO11n Inference API",
    version="0.1.0",
    description="Simple API for running YOLO11n on an uploaded image.",
)
predictor = YOLOPredictor()


@app.post("/detect")
async def detect_image(image: UploadFile = File(...), min_conf=0.25):

    if not image.content_type or not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    contents = await image.read()
    if not contents:
        raise HTTPException(status_code=400, detail="Empty file")

    suffix = Path(image.filename).suffix or ".jpg"
    with tempfile.NamedTemporaryFile(suffix=suffix) as tmp:
        tmp.write(contents)
        tmp.flush()

        predictor.min_conf = min_conf
        detections = predictor.predict(tmp.name)

    detection_dicts = [d.__dict__ for d in detections]

    return {
        "filename": image.filename,
        "num_detections": len(detection_dicts),
        "detections": detection_dicts,
    }
