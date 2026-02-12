# System Health Monitor — Cloud Run

A real-time CPU and memory monitoring dashboard built with Python Flask, containerized with Docker, and deployed on Google Cloud Run.

**Live URL:** https://satyam-gangwar-370498901616.us-central1.run.app/

---

## What It Does

Hitting **Run Analysis** reads live `/proc/stat` and `/proc/meminfo` data from the container, computes a health score out of 100, and renders a dashboard with labeled CPU and memory metrics, color-coded status tags, and alerts when thresholds are exceeded.

The UI also shows a live clock and server uptime that tick in real time without polling.

---

## Project Structure

```
├── app.py                  # Flask app — routes + metric logic
├── requirements.txt
├── Dockerfile
├── sys_check.sh            # Shell script (Task 1)
└── templates/
    ├── home.html           # Landing page
    └── dashboard.html      # Analysis results
```

---

## Stack

| Layer | Technology |
|---|---|
| Language | Python 3 |
| Web framework | Flask + Gunicorn |
| Container | Docker |
| Cloud platform | Google Cloud Run |
| CI/CD | Cloud Build |
| Source control | GitHub |

---

## API Endpoints

| Route | Method | Description |
|---|---|---|
| `/` | GET | Landing page |
| `/dashboard` | GET | Results dashboard |
| `/analyze` | GET | Returns JSON with CPU, memory, health score |
| `/uptime` | GET | Returns server uptime in seconds |

### Sample `/analyze` Response

```json
{
  "timestamp": "2025-06-01T10:22:31Z",
  "uptime_seconds": 3842,
  "health_score": 87.4,
  "status": "EXCELLENT: System running smoothly",
  "alerts": ["System operating normally"],
  "cpu_metrics": {
    "workload_level": { "label": "Low", "value": "4.2%", "meaning": "CPU load level" },
    "responsiveness": { "label": "Fast", "value": "95.8% available", "meaning": "System response speed" },
    "capacity_left":  { "label": "Good", "value": "95.8% idle", "meaning": "Remaining CPU capacity" }
  },
  "memory_metrics": {
    "comfort_level":        { "label": "Comfortable", "value": "61.3% free", "meaning": "Available memory level" },
    "multitasking_ability": { "label": "Smooth",      "value": "0% swap used", "meaning": "Ability to run multiple apps" },
    "stability_risk":       { "label": "Low",         "value": "38.7% used",   "meaning": "Risk of slowdown or freeze" }
  }
}
```

---

## Health Score Formula

```
score = 100 − (cpu_usage × 0.2) − (mem_usage × 0.3)
```

Penalties applied on top:
- CPU > 85% → −5
- Memory > 90% → −10
- Both exceeded → additional overload alert

| Score | Status |
|---|---|
| ≥ 80 | EXCELLENT |
| 60–79 | FAIR |
| 40–59 | POOR |
| < 40 | CRITICAL |

---

## Running Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Run
python app.py
# → http://localhost:8080
```

---

## Docker

```bash
# Build
docker build -t system-monitor .

# Run
docker run -p 8080:8080 system-monitor
```

---

## Deploying to Cloud Run

```bash
# Build and push via Cloud Build
gcloud builds submit --tag gcr.io/PROJECT_ID/system-monitor

# Deploy
gcloud run deploy system-monitor \
  --image gcr.io/PROJECT_ID/system-monitor \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

> Cloud Run scales to zero when idle and scales out automatically under load. No server management required.

---

## Shell Script (Task 1)

`sys_check.sh` runs basic system diagnostics:

- Prints current date and time
- Shows disk usage (`df -h`)
- Logs the current user
- Saves output to `log.txt` and moves it into `deploy_app/`
- Creates `deploy_app/` if it doesn't already exist

```bash
chmod +x sys_check.sh
./sys_check.sh
```

---

## Author

**Satyam Gangwar**
