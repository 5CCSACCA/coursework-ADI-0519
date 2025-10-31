Github repository link: https://github.com/5CCSACCA/coursework-ADI-0519

## Chart2Code - Cloud AI System to convert diagrams to structured blueprints.

**Tech Stack:** 
Fast API · Docker · Docker Compose · PostgreSQL · RabbitMQ · Firebase · Prometheus
ML: YOLO11n (Ultralytics) · EasyOCR · **GraphLayoutNet (Custom PyTorch CNN)** · Bitnet (Microsoft LLM)

---

# Overview

**Chart2Code** is a Software-as-a-Service (SaaS) platform that reads **system or architecture design diagrams** (boxes, arrows, and labels) into structured graph representations, and generate starter backend **templates**.
The platform combines computer vision, OCR, and LLM reasoning to understand diagram layouts and produce executable backend blueprints.

This project demonstrates:
- Cloud-based AI inference on **CPU (≤ 4 vCPU / 16 GB)**,
- **Microservice orchestration** using Docker Compose,
- **Message-based communication** (RabbitMQ),
- **Authentication and persistence** (Firebase + PostgreSQL),
- **Monitoring, testing, and cost analysis** as per coursework stages.

# User Journey:

- User uploads an architecture diagram.
- System detects chart elements (axes, data points, labels)
- Extracts data values and styling information
- Generates Python/JavaScript code to recreate the chart
- Returns code + extracted data + preview image

## Key Features:
- Diagram Understanding: Detect components (boxes), connections (arrows), and labels from uploaded architecture diagrams.
- Structured diagram Extraction: Build a machine-readable JSON representation of system components and their relationships.
- Template Generation: Use an LLM (BitNet) to produce a short FastAPI scaffold or documentation snippet from the extracted diagram.
- End-to-End Pipeline: Runs as a distributed system of Dockerised services connected via RabbitMQ.
- Persistence and Monitoring: Results stored in PostgreSQL; Prometheus tracks latency, throughput, and queue depth.
- Secure SaaS Deployment: Authentication and storage handled by Firebase.

## Service Responsibilities

| Service | Responsibility |
|----------|----------------|
| **API Gateway** | FastAPI service handling uploads, authentication, and API docs. Publishes tasks to RabbitMQ. |
| **YOLO-OCR Worker** | Runs YOLO11n to detect boxes/arrows/text regions, performs OCR on text boxes. |
| **GraphNet Worker** | Uses **GraphLayoutNet** (custom CNN) to infer arrow directions and builds a structured diagram (nodes + edges). |
| **BitNet Worker** | Converts the diagram into FastAPI route templates and README documentation. |
| **PostgreSQL** | Stores project data, diagrams, graph JSON, and scaffold artifacts. |
| **Firebase** | Handles user authentication and stores uploaded images/artifacts. |
| **RabbitMQ** | Message broker for worker communication. |
| **Prometheus** | Exposes metrics from all services. |


## The Custom Model – GraphLayoutNet
Objective
Infer arrow directions (→, ←, ↑, ↓) and connect source/target boxes based on spatial proximity.
Architecture
3 convolutional layers + 2 fully-connected heads
Input: 96×96 grayscale crops of detected arrows
Output: Direction classification (4 classes)
Training Data
Trained on simple synthetic data; accuracy varies depending on arrow thickness and noise.
Synthetic dataset of 3,200 arrow crops generated with Pillow: random angles, thickness, and noise to mimic diagrams.
Augmented with 50 manually labelled examples from real diagrams.
Export
Model exported as TorchScript (graphlayoutnet_v1.pt) for CPU inference.

---

## System Requirements

- OS: Ubuntu 22.04 LTS (or Debian 12)
- CPU/RAM: **4 vCPU / 16 GB RAM**
- Disk: 20 GB+ free
- Network: outbound egress to pull containers (Docker Hub) and optional Firebase
- Packages:
  - Docker Engine >= 24
  - Docker Compose v2 (bundled with Docker Desktop; on server via `docker compose`)
  - `curl`, `ufw` (optional firewall), `git`

## Quickstart (Two Command Deployment)

> Tested on Ubuntu 22.04 with Docker Engine ≥ 24 and Docker Compose v2.

### Build the containers
```bash
docker compose -f docker-compose.yml --profile prod build
```

### Run the SaaS
```bash
docker compose -f docker-compose.yml --profile prod up -d
```

API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)  
RabbitMQ dashboard: [http://localhost:15672](http://localhost:15672)

To stop:
```bash
docker compose down
```

---

## Environment Configuration

Create a `.env` file in the project root:

```env
APP_ENV=prod
APP_PORT=8000
MAX_IMAGE_MB=8

POSTGRES_USER=c2c_user
POSTGRES_PASSWORD=c2c_pass
POSTGRES_DB=chart2code
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

RABBITMQ_HOST=rabbitmq
RABBITMQ_USER=guest
RABBITMQ_PASSWORD=guest

FIREBASE_PROJECT_ID=your-project-id
FIREBASE_CLIENT_EMAIL=service-account@your-project-id.iam.gserviceaccount.com
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
FIREBASE_STORAGE_BUCKET=your-project-id.appspot.com

YOLO_MODEL=/models/yolo11n.pt
GRAPHNET_CHECKPOINT=/models/graphlayoutnet_v1.pt
BITNET_WEIGHTS=/models/bitnet
BITNET_MAX_TOKENS=256

# Optional mocks for demo
MOCK_FIREBASE=1
MOCK_BITNET=1
```

---

## Example Input & Output

### Upload a Diagram
```bash
curl -X POST "http://localhost:8000/projects/demo/diagrams"   -H "Authorization: Bearer demo-token"   -F "file=@samples/diagram_placeholder.jpg"
```

### Example Response
```json
{
  "job_id": "4b6a0d9c",
  "status": "done",
  "graph": {
    "nodes": [
      {"node_id": "Auth", "type": "service"},
      {"node_id": "Orders", "type": "service"}
    ],
    "edges": [
      {"source": "Auth", "target": "Orders", "direction": "right", "label": "POST /login"}
    ]
  },
  "scaffold": {
    "fastapi": "from fastapi import FastAPI\napp=FastAPI()\n@app.post('/login')\nasync def login(): ...",
    "readme": "Services: Auth → Orders"
  },
  "assets": {
    "image_uri": "gs://mock-bucket/demo.jpg",
    "graph_uri": "gs://mock-bucket/graph.json",
    "scaffold_uri": "gs://mock-bucket/scaffold.json"
  }
}
```

---

## Machine Learning Components

| Model | Purpose | Type | Notes |
|--------|----------|------|-------|
| **YOLO11n** | Object detection for boxes, arrows, and text regions. | Pretrained | CPU-friendly; fine-tuning optional. |
| **EasyOCR** | Optical character recognition for text boxes. | Pretrained | Extracts node and edge labels. |
| **GraphLayoutNet** | Custom CNN to classify arrow directions (←, →, ↑, ↓). | **Your custom model** | Trained on synthetic arrow data (≈3k samples). |
| **BitNet (Microsoft)** | LLM for structured code/text generation. | External | Deterministic prompt for scaffold generation. |

---

## Testing 

Run tests:
```bash
pytest -q
```

### Unit Tests
| Test | Description |
|------|--------------|
| `test_yolo_postproc.py` | Bounding box & NMS logic |
| `test_ocr_clean.py` | OCR output sanitisation |
| `test_graphnet_infer.py` | Arrow direction inference |
| `test_graph_builder.py` | Graph consistency from detections |
| `test_bitnet_prompt.py` | Prompt schema validation |
| `test_auth_guard.py` | Firebase token checks |

### Integration Tests
Run with minimal `docker-compose.test.yml` (mock workers).  
Checks end-to-end job creation → processing → storage.

---

## Monitoring 

**Prometheus metrics:**
| Metric | Description |
|---------|--------------|
| `http_request_duration_seconds` | API latency |
| `yolo_infer_ms`, `ocr_infer_ms` | Vision worker performance |
| `graphnet_infer_ms` | Graph processing latency |
| `bitnet_latency_ms`, `bitnet_tokens_total` | LLM usage metrics |
| `queue_depth{queue=...}` | RabbitMQ queue backlog |
| `errors_total{service=...}` | Error tracking |

**Target SLOs:**
- p95 latency: `< 3.0s`  
- Error rate: `< 1%`

Access Prometheus: [http://localhost:9090](http://localhost:9090)

---

## Security 

| Category | Measure |
|-----------|----------|
| **Auth** | Firebase ID token verification |
| **Access Control** | Per-user data filtering |
| **Storage** | Firebase signed URLs; no public paths |
| **Input Validation** | File size cap (8 MB), MIME & magic-byte checks |
| **Secrets Management** | Environment variables only (`.env` not in Git) |
| **Network Isolation** | Private Docker network (no exposed DB/RabbitMQ) |
| **Audit Logging** | DB audit table with timestamps and trace IDs |

---

## Sustainability & Limitations

- **Efficiency:** Runs fully on CPU (no GPU energy cost).  
- **Bias & Limitations:** Dependent on diagram clarity; may fail on overlapping arrows.  
- **Privacy:** User data isolated by Firebase authentication.  
- **Data Retention:** Auto-purge artifacts after 30 days.  
- **Extensibility:** Supports plugin architecture for new shapes/models.

---

## GitFlow Development Process

| Branch | Purpose |
|---------|----------|
| `main` | Stable release (final submission) |
| `develop` | Integration branch |
| `feature/*` | Individual feature development |
| `hotfix/*` | Urgent patches post-release |

PRs merge into `develop` → `main`.  
Use annotated tags for releases.

---

**Owner:** Aditya Ranjan   
**Project:** Chart2Code - From Diagram to production code.
