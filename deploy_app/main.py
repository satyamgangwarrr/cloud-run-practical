from flask import Flask, jsonify, request
import psutil
import os
from datetime import datetime
import time

app = Flask(__name__)

#start time
start_time = time.time()
#normal_mode
def calculate_health_score(cpu_usage, memory_usage, uptime):
    health = 0

    if cpu_usage <= 20:
        health += 40
    elif cpu_usage <= 40:
        health += 30
    elif cpu_usage <= 60:
        health += 20
    else:
        health += 10

    if memory_usage <= 40:
        health += 35
    elif memory_usage <= 60:
        health += 25
    elif memory_usage <= 80:
        health += 15
    else:
        health += 5

    if uptime < 300:
        health += 5
    elif uptime < 1800:
        health += 15
    else:
        health += 25

    return health


#gamer_mode
def calculate_gamer_health(cpu_usage, memory_usage, uptime):
    health = 100

    if cpu_usage > 90:
        health -= 10
    elif cpu_usage > 75:
        health -= 5

    if memory_usage > 85:
        health -= 40
    elif memory_usage > 70:
        health -= 25
    elif memory_usage > 55:
        health -= 10

    if uptime > 7200:
        health -= 5

    return max(0, health)


#normal_mode message
def get_normal_status_message(score):
    if score >= 85:
        return "Excellent : System running very fine"
    elif score >= 70:
        return "Good : System performance is good"
    elif score >= 55:
        return "Fair : System under little load"
    elif score >= 40:
        return "Poor : System under Load"
    else:
        return "Critical : Decrease system Load"


#gamer mode message
def get_gamer_status_message(score):
    if score >= 85:
        return "Beast Mode : Ready for high FPS gaming"
    elif score >= 70:
        return "Smooth Play : Stable gaming performance"
    elif score >= 55:
        return "Playable : Minor lag may occur"
    elif score >= 40:
        return "Lag Zone : Reduce graphics settings"
    else:
        return "Game Over : Not suitable for gaming"


@app.route('/')
def hello():
    return "Hello from Satyam!"


@app.route('/analyze', methods=['GET'])
def analyze():
    try:
        mode = request.args.get("mode", "normal")

        timestamp = datetime.utcnow()
        uptime_sec = int(time.time() - start_time)

        cpu_metric = psutil.cpu_percent(interval=1)
        memory_metric = psutil.virtual_memory().percent

        if mode == "gamer":
            health_score = calculate_gamer_health(cpu_metric, memory_metric, uptime_sec)
            message = get_gamer_status_message(health_score)
        else:
            health_score = calculate_health_score(cpu_metric, memory_metric, uptime_sec)
            message = get_normal_status_message(health_score)

        return jsonify({
            "timestamp": timestamp,
            "mode": mode,
            "uptime_seconds": uptime_sec,
            "cpu_metric": round(cpu_metric, 2),
            "memory_metric": round(memory_metric, 2),
            "health_score": health_score,
            "message": message
        })

    except Exception as e:
        return jsonify({
            "error": str(e),
            "timestamp": datetime.utcnow(),
            "message": "Failed to retrieve system metrics"
        }), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)), debug=False)
