FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y libgl1 libglib2.0-0 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY yolo_service ./yolo_service
COPY tests ./tests
COPY yolo11n.pt ./yolo11n.pt


CMD ["python","-m","yolo_service","tests/data/img1.webp"]
