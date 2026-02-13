from flask import Flask, jsonify, render_template
import time
import os
from datetime import datetime

app = Flask(__name__)

start_time = time.time()



def get_cpu_metrics():
    try:
        with open("/proc/stat") as f:
            for line in f:
                if line.startswith("cpu "):
                    parts  = line.split()
                    user   = int(parts[1])
                    nice   = int(parts[2])
                    system = int(parts[3])
                    idle   = int(parts[4])
                    iowait = int(parts[5])
                    total  = user + nice + system + idle + iowait
                    usage  = round((user + system) / total * 100, 2) if total > 0 else 0
                    usage  = max(usage, 0.1)

                    workload       = "Low"    if usage < 40 else "Medium"        if usage < 70 else "High"
                    responsiveness = "Fast"   if usage < 30 else "Slightly Slow" if usage < 60 else "Slow"
                    capacity       = "Good"   if usage < 60 else "Limited"       if usage < 80 else "Critical"

                    return {
                        "workload_level": {"label": workload,       "value": f"{usage}%",              "meaning": "CPU load level"},
                        "responsiveness": {"label": responsiveness, "value": f"{100-usage}% available","meaning": "System response speed"},
                        "capacity_left":  {"label": capacity,       "value": f"{100-usage}% idle",     "meaning": "Remaining CPU capacity"},
                        "usage_percent": usage
                    }
    except Exception:
        pass
    return {k: {"label": "Error", "value": "N/A", "meaning": "Failed to read"}
            for k in ["workload_level", "responsiveness", "capacity_left"]} | {"usage_percent": 0}


def get_memory_metrics():
    try:
        meminfo = {}
        with open("/proc/meminfo") as f:
            for line in f:
                parts = line.split(":")
                if len(parts) == 2:
                    meminfo[parts[0].strip()] = int(parts[1].strip().split()[0])

        total      = meminfo.get("MemTotal", 1)
        available  = meminfo.get("MemAvailable", meminfo.get("MemFree", 0))
        used       = total - available
        swap_total = meminfo.get("SwapTotal", 0)
        swap_free  = meminfo.get("SwapFree", 0)
        swap_pct   = round(((swap_total - swap_free) / swap_total) * 100, 2) if swap_total > 0 else 0
        used_pct   = round((used / total) * 100, 2)
        avail_pct  = round((available / total) * 100, 2)

        comfort   = "Comfortable" if avail_pct > 30 else "Tight"   if avail_pct > 15 else "Critical"
        multitask = "Smooth"      if swap_pct < 10  else "Limited" if swap_pct < 30  else "Poor"
        risk      = "Low"         if used_pct < 80  else "Medium"  if used_pct < 90  else "High"

        return {
            "comfort_level":        {"label": comfort,    "value": f"{avail_pct}% free",    "meaning": "Available memory level"},
            "multitasking_ability": {"label": multitask,  "value": f"{swap_pct}% swap used","meaning": "Ability to run multiple apps"},
            "stability_risk":       {"label": risk,       "value": f"{used_pct}% used",     "meaning": "Risk of slowdown or freeze"},
            "usage_percent": used_pct
        }
    except Exception:
        return {k: {"label": "Error", "value": "N/A", "meaning": "Failed to read"}
                for k in ["comfort_level", "multitasking_ability", "stability_risk"]} | {"usage_percent": 0}


def calculate_health(cpu_usage, mem_usage):
    health   = 100 - cpu_usage * 0.2 - mem_usage * 0.3
    messages = []
    if cpu_usage > 85: health -= 5;  messages.append("CPU saturation risk detected")
    if mem_usage > 90: health -= 10; messages.append("Memory exhaustion risk detected")
    if cpu_usage > 85 and mem_usage > 90: messages.append("System overload condition")
    health = max(0, round(health, 2))

    if health >= 80:   status = "EXCELLENT: System running smoothly"
    elif health >= 60: status = "FAIR: Moderate resource usage"
    elif health >= 40: status = "POOR: Performance degradation detected"
    else:              status = "CRITICAL: System stability at risk"

    if not messages: messages.append("System operating normally")
    return health, status, messages



@app.route("/")
def home():
    return render_template("home.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@app.route("/analyze")
def analyze():
    try:
        cpu = get_cpu_metrics()
        mem = get_memory_metrics()
        health, status, alerts = calculate_health(cpu["usage_percent"], mem["usage_percent"])
        return jsonify({
            "timestamp":      datetime.utcnow().isoformat() + "Z",
            "uptime_seconds": int(time.time() - start_time),
            "cpu_metrics":    cpu,
            "memory_metrics": mem,
            "health_score":   health,
            "status":         status,
            "alerts":         alerts
        }), 200
    except Exception as e:
        return jsonify({
            "error":     "Internal server error",
            "message":   str(e),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }), 500


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8080)),
        debug=False
    )
