Github repository link: https://github.com/5CCSACCA/coursework-ADI-0519

# SafetyVision – Cloud-Based Workplace Hazard Detection
**5CCSACCA – Cloud Computing for Artificial Intelligence (Coursework Project)**

SafetyVision is a cloud-based AI system that analyses workplace images (e.g. construction or warehouse scenes), detects common objects, identifies potential hazards, and generates short safety summaries using a lightweight language model.

The project focuses on **cloud architecture**, **containerisation**, **service orchestration**, **authentication**, **monitoring**, and **AI inference on CPU**, as required by the coursework specification.

---

## 📌 Project Overview

SafetyVision provides a simple end-to-end pipeline:

1. A user uploads a workplace image.
2. The system runs **YOLO11n** to detect people, vehicles, ladders, and tools.
3. A small **rule-based engine** infers potential hazards (e.g., “person near vehicle”, “cluttered workspace”).
4. **BitNet** generates a short natural-language safety summary.
5. All results are stored in **PostgreSQL** for later retrieval.
6. Access to the API is protected through **Firebase Authentication**.
7. **RabbitMQ** handles asynchronous communication between detection and hazard-analysis services.
8. **Prometheus** exposes basic monitoring metrics.

All components run on **≤ 4 vCPUs and 16 GB RAM**, matching the coursework restrictions.

---

## 🧱 High-Level Architecture

The system is implemented as several lightweight microservices orchestrated using **Docker Compose**:

| Service | Description |
|---------|-------------|
| **API Gateway** | FastAPI service exposed publicly. Handles file uploads, authentication, and DB access. |
| **YOLO Service** | Performs object detection using YOLO11n and publishes results to RabbitMQ. |
| **Safety Service** | Consumes messages, applies hazard rules, calls BitNet, and writes summaries to the DB. |
| **PostgreSQL** | Persists requests, detections, hazards, and generated summaries. |
| **Firebase** | Manages user authentication and optional image storage. |
| **RabbitMQ** | Message broker connecting detection → hazard services. |
| **Prometheus** | Collects metrics from services for monitoring. |

All services run inside a private Docker network.

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
