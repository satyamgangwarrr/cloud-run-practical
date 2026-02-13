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

## Health Score Algorithm

### Pipeline Overview

```
/proc/stat          /proc/meminfo
     │                    │
     ▼                    ▼
 cpu_usage%          mem_usage%
     │                    │
     └────────┬───────────┘
              ▼
   base_score = 100 − (cpu × 0.2) − (mem × 0.3)
              │
              ▼
   penalty check (hard thresholds)
              │
              ▼
   final_score  +  status label  +  alerts[]
```

---

### Step 1 — Raw Metric Collection

**CPU** is read from the first line of `/proc/stat`:

```
cpu  user  nice  system  idle  iowait  ...
```

```
total = user + nice + system + idle + iowait
usage = (user + system) / total × 100
```

Only `user` and `system` time count toward load. `iowait` is excluded because on Cloud Run, I/O wait reflects infrastructure latency outside the app's control.

**Memory** is read from `/proc/meminfo`:

```
used     = MemTotal − MemAvailable
used_pct = used / MemTotal × 100
avail_pct = MemAvailable / MemTotal × 100
swap_pct  = (SwapTotal − SwapFree) / SwapTotal × 100
```

`MemAvailable` is preferred over `MemFree` because it accounts for reclaimable cache — a more accurate picture of what the kernel can actually hand to a new process.

---

### Step 2 — Human Label Mapping

Raw percentages are bucketed into labels for readability.

**CPU labels:**

| Metric | Range | Label |
|---|---|---|
| Workload Level | usage < 40% | Low |
| | 40% ≤ usage < 70% | Medium |
| | usage ≥ 70% | High |
| Responsiveness | usage < 30% | Fast |
| | 30% ≤ usage < 60% | Slightly Slow |
| | usage ≥ 60% | Slow |
| Capacity Left | usage < 60% | Good |
| | 60% ≤ usage < 80% | Limited |
| | usage ≥ 80% | Critical |

**Memory labels:**

| Metric | Range | Label |
|---|---|---|
| Comfort Level | avail > 30% | Comfortable |
| | 15% < avail ≤ 30% | Tight |
| | avail ≤ 15% | Critical |
| Multitasking Ability | swap < 10% | Smooth |
| | 10% ≤ swap < 30% | Limited |
| | swap ≥ 30% | Poor |
| Stability Risk | used < 80% | Low |
| | 80% ≤ used < 90% | Medium |
| | used ≥ 90% | High |

---

### Step 3 — Base Score Calculation

```
base_score = 100 − (cpu_usage × 0.2) − (mem_usage × 0.3)
```

**Why different weights?**

- **CPU (×0.2):** CPU spikes are transient. The kernel scheduler recovers quickly, and a busy CPU rarely leads to a crash. At 100% CPU, the penalty is 20 points — significant but not catastrophic.
- **Memory (×0.3):** Memory exhaustion is harder to recover from. When available memory runs out, the kernel invokes the OOM killer, terminating processes. At 100% memory usage, the penalty is 30 points — reflecting a more serious risk.

---

### Step 4 — Penalty Conditions

On top of the base score, hard penalties apply when usage crosses critical thresholds:

| Condition | Penalty | Alert Added |
|---|---|---|
| CPU > 85% | −5 | "CPU saturation risk detected" |
| Memory > 90% | −10 | "Memory exhaustion risk detected" |
| Both CPU > 85% and Memory > 90% | 0 (additional) | "System overload condition" |

The combined condition adds an alert but no extra point penalty — the individual penalties already capture the severity.

Final score is clamped to a minimum of 0.

---

### Step 5 — Status Classification

```
score ≥ 80  →  EXCELLENT: System running smoothly
score ≥ 60  →  FAIR: Moderate resource usage
score ≥ 40  →  POOR: Performance degradation detected
score  < 40  →  CRITICAL: System stability at risk
```

---

### Worked Example

Suppose at analysis time: **CPU at 55%, memory at 72%.**

```
base_score = 100 − (55 × 0.2) − (72 × 0.3)
           = 100 − 11 − 21.6
           = 67.4

Penalty check:
  CPU 55% → not > 85%, no penalty
  Mem 72% → not > 90%, no penalty

final_score = 67.4  →  FAIR: Moderate resource usage

Labels:
  CPU workload:    Medium  (40% ≤ 55% < 70%)
  CPU response:    Slightly Slow  (30% ≤ 55% < 60%)
  CPU capacity:    Limited  (60% ≤ 55%... wait, 55% < 60% → Good)
  Mem comfort:     Comfortable  (avail = 28% > ... Tight if avail ≤ 30%)
  Mem multitask:   Smooth  (swap assumed 0%)
  Mem stability:   Low  (72% < 80%)

Alert: "System operating normally"
```

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
