from flask import Flask, jsonify, render_template_string
import time
import os
from datetime import datetime

app = Flask(__name__)

start_time = time.time()

# HTML TEMPLATES

HOME_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>System Monitor</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Sora:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --ink: #0f0f0f;
            --paper: #f4f1eb;
            --accent: #c8401a;
            --muted: #8a8578;
            --border: #d6d0c4;
            --card: #fdfbf7;
        }

        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            font-family: 'Sora', sans-serif;
            background: var(--paper);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 40px 20px;
            position: relative;
            overflow: hidden;
        }

        /* Grid texture */
        body::before {
            content: '';
            position: fixed;
            inset: 0;
            background-image:
                linear-gradient(var(--border) 1px, transparent 1px),
                linear-gradient(90deg, var(--border) 1px, transparent 1px);
            background-size: 60px 60px;
            opacity: 0.35;
            pointer-events: none;
        }

        .corner-label {
            position: fixed;
            font-family: 'DM Mono', monospace;
            font-size: 0.65rem;
            color: var(--muted);
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }
        .corner-label.tl { top: 24px; left: 28px; }
        .corner-label.tr { top: 24px; right: 28px; text-align: right; }
        .corner-label.bl { bottom: 24px; left: 28px; }
        .corner-label.br { bottom: 24px; right: 28px; text-align: right; }

        .live-clock {
            font-family: 'DM Mono', monospace;
            font-size: 0.75rem;
            color: var(--muted);
            letter-spacing: 0.05em;
        }

        .container {
            position: relative;
            z-index: 1;
            text-align: center;
            max-width: 480px;
            width: 100%;
        }

        .eyebrow {
            font-family: 'DM Mono', monospace;
            font-size: 0.7rem;
            letter-spacing: 0.15em;
            text-transform: uppercase;
            color: var(--accent);
            margin-bottom: 28px;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 12px;
        }

        .eyebrow::before,
        .eyebrow::after {
            content: '';
            display: block;
            width: 32px;
            height: 1px;
            background: var(--accent);
        }

        h1 {
            font-size: 2.6rem;
            font-weight: 700;
            color: var(--ink);
            line-height: 1.15;
            letter-spacing: -0.04em;
            margin-bottom: 14px;
        }

        h1 span {
            color: var(--accent);
        }

        .subtitle {
            font-size: 0.9rem;
            color: var(--muted);
            font-weight: 300;
            margin-bottom: 52px;
            line-height: 1.6;
        }

        .btn-wrap {
            display: inline-block;
            position: relative;
        }

        .btn-shadow {
            position: absolute;
            inset: 0;
            background: var(--ink);
            border-radius: 6px;
            transform: translate(4px, 4px);
        }

        .btn {
            position: relative;
            z-index: 1;
            background: var(--accent);
            color: #fff;
            border: 2px solid var(--ink);
            padding: 15px 52px;
            font-size: 0.9rem;
            border-radius: 6px;
            cursor: pointer;
            font-family: 'Sora', sans-serif;
            font-weight: 600;
            letter-spacing: 0.04em;
            text-transform: uppercase;
            transition: transform 0.15s ease, box-shadow 0.15s ease;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .btn:hover {
            transform: translate(-2px, -2px);
        }

        .btn:active {
            transform: translate(2px, 2px);
        }

        .btn .spinner {
            display: none;
            width: 14px;
            height: 14px;
            border: 2px solid rgba(255,255,255,0.4);
            border-top-color: #fff;
            border-radius: 50%;
            animation: spin 0.6s linear infinite;
        }

        @keyframes spin { to { transform: rotate(360deg); } }

        .btn.loading .spinner { display: block; }
        .btn.loading .btn-text { opacity: 0.7; }

        .status-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #22c55e;
            display: inline-block;
            box-shadow: 0 0 0 2px rgba(34,197,94,0.25);
            animation: pulse-dot 2s ease infinite;
        }

        @keyframes pulse-dot {
            0%, 100% { box-shadow: 0 0 0 2px rgba(34,197,94,0.25); }
            50% { box-shadow: 0 0 0 6px rgba(34,197,94,0.1); }
        }

        .meta-row {
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 20px;
            margin-top: 40px;
            font-family: 'DM Mono', monospace;
            font-size: 0.7rem;
            color: var(--muted);
        }

        .meta-row span {
            display: flex;
            align-items: center;
            gap: 6px;
        }
    </style>
</head>
<body>
    <div class="corner-label tl">SYS-MON</div>
    <div class="corner-label tr live-clock" id="corner-clock"></div>
    <div class="corner-label bl">CLOUD RUN by Satyam</div>
    <div class="corner-label br">Copyright @ SATYAM</div>

    <div class="container">
        <div class="eyebrow">Satyam says Hello from Cloud Run </div>
        <h1>System <span>Health</span><br>Monitor</h1>
        <p class="subtitle">Real-time CPU &amp; memory diagnostics<br>deployed on Google Cloud Run</p>

        <div class="btn-wrap">
            <div class="btn-shadow"></div>
            <button class="btn" id="analyzeBtn" onclick="analyze()">
                <span class="btn-text">Run Analysis</span>
                <div class="spinner"></div>
            </button>
        </div>

        <div class="meta-row">
            <span><span class="status-dot"></span> System Online</span>
            <span>/ <span id="live-uptime">--</span></span>
            <span>/ <span id="live-date">--</span></span>
        </div>
    </div>

    <script>
        // Live clock — updates every second
        function updateClock() {
            const now = new Date();
            const timeStr = now.toLocaleTimeString('en-US', { hour12: false });
            const dateStr = now.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
            document.getElementById('corner-clock').textContent = timeStr;
            document.getElementById('live-date').textContent = dateStr;
        }
        updateClock();
        setInterval(updateClock, 1000);

        // Uptime from server
        function updateUptime(sec) {
            const h = Math.floor(sec / 3600);
            const m = Math.floor((sec % 3600) / 60);
            const s = sec % 60;
            document.getElementById('live-uptime').textContent =
                `${String(h).padStart(2,'0')}:${String(m).padStart(2,'0')}:${String(s).padStart(2,'0')} uptime`;
        }

        // Fetch uptime tick every second
        let cachedUptime = 0;
        fetch('/uptime').then(r => r.json()).then(d => {
            cachedUptime = d.uptime_seconds;
            updateUptime(cachedUptime);
            setInterval(() => { cachedUptime++; updateUptime(cachedUptime); }, 1000);
        });

        function analyze() {
            const btn = document.getElementById('analyzeBtn');
            btn.classList.add('loading');
            btn.disabled = true;
            fetch('/analyze')
                .then(res => res.json())
                .then(data => {
                    localStorage.setItem('data', JSON.stringify(data));
                    window.location.href = '/dashboard';
                })
                .catch(e => {
                    btn.classList.remove('loading');
                    btn.disabled = false;
                    alert('Error: ' + e);
                });
        }
    </script>
</body>
</html>
"""

DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>System Analysis</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Sora:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --ink: #0f0f0f;
            --paper: #f4f1eb;
            --accent: #c8401a;
            --muted: #8a8578;
            --border: #d6d0c4;
            --card: #fdfbf7;
            --green: #1a7a3c;
            --yellow: #b07d1a;
            --red: #c8401a;
        }

        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            font-family: 'Sora', sans-serif;
            background: var(--paper);
            min-height: 100vh;
            padding: 0;
            color: var(--ink);
            position: relative;
        }

        body::before {
            content: '';
            position: fixed;
            inset: 0;
            background-image:
                linear-gradient(var(--border) 1px, transparent 1px),
                linear-gradient(90deg, var(--border) 1px, transparent 1px);
            background-size: 60px 60px;
            opacity: 0.3;
            pointer-events: none;
            z-index: 0;
        }

        /* Top bar */
        .topbar {
            position: sticky;
            top: 0;
            z-index: 100;
            background: var(--ink);
            color: #fff;
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 36px;
            height: 52px;
            border-bottom: 2px solid var(--accent);
        }

        .topbar-left {
            font-family: 'DM Mono', monospace;
            font-size: 0.7rem;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            display: flex;
            align-items: center;
            gap: 16px;
        }

        .topbar-left .dot {
            width: 7px; height: 7px;
            border-radius: 50%;
            background: #22c55e;
            animation: pulse-dot 2s ease infinite;
        }

        @keyframes pulse-dot {
            0%, 100% { box-shadow: 0 0 0 2px rgba(34,197,94,0.2); }
            50% { box-shadow: 0 0 0 6px rgba(34,197,94,0.08); }
        }

        .topbar-right {
            font-family: 'DM Mono', monospace;
            font-size: 0.7rem;
            color: rgba(255,255,255,0.55);
            letter-spacing: 0.08em;
            display: flex;
            align-items: center;
            gap: 20px;
        }

        .live-time {
            color: rgba(255,255,255,0.9);
            font-size: 0.75rem;
        }

        /* Main layout */
        .page {
            position: relative;
            z-index: 1;
            max-width: 1200px;
            margin: 0 auto;
            padding: 48px 32px 64px;
        }

        /* Score banner */
        .score-banner {
            display: grid;
            grid-template-columns: auto 1fr auto;
            align-items: center;
            gap: 32px;
            background: var(--ink);
            border-radius: 12px;
            padding: 32px 40px;
            margin-bottom: 36px;
            position: relative;
            overflow: hidden;
        }

        .score-banner::after {
            content: '';
            position: absolute;
            right: -40px; top: -40px;
            width: 200px; height: 200px;
            border-radius: 50%;
            background: var(--accent);
            opacity: 0.08;
        }

        .score-num {
            font-family: 'DM Mono', monospace;
            font-size: 4.5rem;
            font-weight: 500;
            line-height: 1;
            color: #fff;
        }

        .score-num span {
            font-size: 1.8rem;
            color: rgba(255,255,255,0.4);
        }

        .score-meta h2 {
            font-size: 1.4rem;
            font-weight: 600;
            color: #fff;
            margin-bottom: 8px;
            letter-spacing: -0.02em;
        }

        .score-meta .status-badge {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            font-family: 'DM Mono', monospace;
            font-size: 0.72rem;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            padding: 6px 14px;
            border-radius: 4px;
            border: 1px solid rgba(255,255,255,0.15);
            color: rgba(255,255,255,0.7);
        }

        .score-timestamp {
            text-align: right;
            font-family: 'DM Mono', monospace;
            font-size: 0.68rem;
            color: rgba(255,255,255,0.35);
            line-height: 1.9;
        }

        .score-timestamp strong {
            color: rgba(255,255,255,0.6);
            font-weight: 500;
        }

        /* Section label */
        .section-label {
            font-family: 'DM Mono', monospace;
            font-size: 0.65rem;
            letter-spacing: 0.16em;
            text-transform: uppercase;
            color: var(--muted);
            margin-bottom: 16px;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .section-label::after {
            content: '';
            flex: 1;
            height: 1px;
            background: var(--border);
        }

        /* Cards */
        .cards-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(340px, 1fr));
            gap: 24px;
            margin-bottom: 36px;
        }

        .card {
            background: var(--card);
            border-radius: 10px;
            border: 1.5px solid var(--border);
            overflow: hidden;
        }

        .card-header {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 20px 24px 18px;
            border-bottom: 1px solid var(--border);
        }

        .card-icon {
            width: 36px; height: 36px;
            border-radius: 8px;
            background: var(--ink);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1rem;
        }

        .card-title {
            font-size: 0.95rem;
            font-weight: 600;
            color: var(--ink);
            letter-spacing: -0.01em;
        }

        .card-body {
            padding: 20px 24px;
            display: flex;
            flex-direction: column;
            gap: 14px;
        }

        .metric-row {
            display: grid;
            grid-template-columns: 1fr auto;
            align-items: start;
            gap: 12px;
            padding: 14px 16px;
            background: var(--paper);
            border-radius: 8px;
            border: 1px solid var(--border);
            position: relative;
            overflow: hidden;
        }

        .metric-bar {
            position: absolute;
            bottom: 0; left: 0;
            height: 2px;
            background: var(--accent);
            opacity: 0.6;
            transition: width 1s ease;
        }

        .metric-label {
            font-size: 0.72rem;
            font-family: 'DM Mono', monospace;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: var(--muted);
            margin-bottom: 5px;
        }

        .metric-meaning {
            font-size: 0.78rem;
            color: var(--muted);
            font-weight: 300;
            margin-top: 3px;
        }

        .metric-value {
            font-family: 'DM Mono', monospace;
            font-size: 0.85rem;
            font-weight: 500;
            text-align: right;
        }

        .metric-tag {
            font-family: 'DM Mono', monospace;
            font-size: 0.65rem;
            letter-spacing: 0.06em;
            padding: 3px 8px;
            border-radius: 3px;
            text-align: right;
            margin-top: 4px;
            text-transform: uppercase;
        }

        .tag-good { background: rgba(26,122,60,0.1); color: var(--green); }
        .tag-warn { background: rgba(176,125,26,0.1); color: var(--yellow); }
        .tag-bad  { background: rgba(200,64,26,0.1);  color: var(--red);   }

        /* Alerts */
        .alerts-card {
            background: var(--card);
            border-radius: 10px;
            border: 1.5px solid var(--border);
            padding: 24px;
            margin-bottom: 36px;
        }

        .alert-item {
            display: flex;
            align-items: flex-start;
            gap: 12px;
            padding: 12px 14px;
            border-radius: 6px;
            background: var(--paper);
            border: 1px solid var(--border);
            margin-top: 12px;
            font-size: 0.85rem;
            color: var(--ink);
            line-height: 1.5;
        }

        .alert-item .alert-dot {
            width: 6px; height: 6px;
            border-radius: 50%;
            background: var(--accent);
            margin-top: 6px;
            flex-shrink: 0;
        }

        /* Footer */
        .footer-row {
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 16px;
        }

        .footer-meta {
            font-family: 'DM Mono', monospace;
            font-size: 0.68rem;
            color: var(--muted);
            line-height: 1.9;
        }

        .footer-meta strong {
            color: var(--ink);
            font-weight: 500;
        }

        .btn-back {
            background: transparent;
            color: var(--ink);
            border: 1.5px solid var(--ink);
            padding: 10px 28px;
            border-radius: 6px;
            cursor: pointer;
            font-family: 'Sora', sans-serif;
            font-size: 0.82rem;
            font-weight: 600;
            letter-spacing: 0.04em;
            text-transform: uppercase;
            transition: background 0.15s, color 0.15s;
        }

        .btn-back:hover {
            background: var(--ink);
            color: #fff;
        }

        @media (max-width: 700px) {
            .topbar { padding: 0 20px; }
            .page { padding: 28px 16px 48px; }
            .score-banner {
                grid-template-columns: 1fr;
                gap: 16px;
                padding: 24px 24px;
            }
            .score-num { font-size: 3.2rem; }
            .score-timestamp { text-align: left; }
            .cards-grid { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>

    <div class="topbar">
        <div class="topbar-left">
            <span class="dot"></span>
            SYS-MON &mdash; Analysis Report
        </div>
        <div class="topbar-right">
            <span>Cloud Run</span>
            <span class="live-time" id="live-clock-top">--:--:--</span>
        </div>
    </div>

    <div class="page">

        <!-- Score Banner -->
        <div class="score-banner">
            <div class="score-num" id="healthScore">--<span>/100</span></div>
            <div class="score-meta">
                <h2>Health Score</h2>
                <div class="status-badge">
                    <span class="dot" style="background:#22c55e; width:6px; height:6px;"></span>
                    <span id="statusText">Loading&hellip;</span>
                </div>
            </div>
            <div class="score-timestamp" id="scoreTimestamp">
                &mdash;
            </div>
        </div>

        <!-- Alerts -->
        <div id="alertsSection" style="display:none;" class="alerts-card">
            <div class="section-label">Alerts</div>
            <div id="alertsList"></div>
        </div>

        <!-- Metrics -->
        <div class="section-label">Metrics</div>
        <div class="cards-grid">
            <div class="card">
                <div class="card-header">
                    <div class="card-icon">⚙️</div>
                    <div class="card-title">CPU</div>
                </div>
                <div class="card-body" id="cpuCard"></div>
            </div>
            <div class="card">
                <div class="card-header">
                    <div class="card-icon">🧠</div>
                    <div class="card-title">Memory</div>
                </div>
                <div class="card-body" id="memCard"></div>
            </div>
        </div>

        <!-- Footer -->
        <div class="footer-row">
            <div class="footer-meta" id="footerMeta">&mdash;</div>
            <button class="btn-back" onclick="window.location.href='/'">← Back</button>
        </div>

    </div>

    <script>
        // Live clock — updates every second
        function updateClock() {
            const now = new Date();
            document.getElementById('live-clock-top').textContent =
                now.toLocaleTimeString('en-US', { hour12: false });
        }
        updateClock();
        setInterval(updateClock, 1000);

        // Determine tag class from label
        function tagClass(label) {
            const good = ['Low','Fast','Good','Comfortable','Smooth','Excellent'];
            const warn = ['Medium','Slightly Slow','Limited','Tight'];
            for (const w of warn) if (label.includes(w)) return 'tag-warn';
            for (const g of good) if (label.includes(g)) return 'tag-good';
            return 'tag-bad';
        }

        // Extract numeric % from value string for bar width
        function barWidth(value) {
            const m = value.match(/([\d.]+)%/);
            return m ? Math.min(parseFloat(m[1]), 100) : 30;
        }

        function createMetricRow(label, value, meaning, tag) {
            const cls = tagClass(tag);
            const bw = barWidth(value);
            return `
                <div class="metric-row">
                    <div>
                        <div class="metric-label">${label}</div>
                        <div class="metric-meaning">${meaning}</div>
                    </div>
                    <div>
                        <div class="metric-value">${value}</div>
                        <div class="metric-tag ${cls}">${tag}</div>
                    </div>
                    <div class="metric-bar" style="width:${bw}%"></div>
                </div>
            `;
        }

        const data = JSON.parse(localStorage.getItem('data'));

        if (!data) {
            document.querySelector('.page').innerHTML =
                '<div style="text-align:center;padding:80px 20px;color:var(--muted);font-family:DM Mono,monospace;font-size:0.85rem;">No data. <a href="/" style="color:var(--ink)">Go back →</a></div>';
        } else {
            // Health score
            document.getElementById('healthScore').innerHTML =
                `${data.health_score.toFixed(1)}<span>/100</span>`;
            document.getElementById('statusText').textContent = data.status;

            // Timestamp block — this uses the server-captured time at analysis
            const analysisTime = new Date(data.timestamp);
            const uptimeH = Math.floor(data.uptime_seconds / 3600);
            const uptimeM = Math.floor((data.uptime_seconds % 3600) / 60);
            const uptimeS = data.uptime_seconds % 60;

            document.getElementById('scoreTimestamp').innerHTML =
                `<strong>Captured</strong><br>${analysisTime.toLocaleString('en-US', {
                    month: 'short', day: 'numeric', year: 'numeric',
                    hour: '2-digit', minute: '2-digit', second: '2-digit'
                })}<br><strong>Uptime</strong><br>${String(uptimeH).padStart(2,'0')}:${String(uptimeM).padStart(2,'0')}:${String(uptimeS).padStart(2,'0')}`;

            // Footer
            document.getElementById('footerMeta').innerHTML =
                `<strong>Analysis captured:</strong> ${analysisTime.toLocaleString()}<br>` +
                `<strong>Server uptime:</strong> ${uptimeH}h ${uptimeM}m ${uptimeS}s`;

            // Alerts
            if (data.alerts && data.alerts.length > 0) {
                document.getElementById('alertsList').innerHTML =
                    data.alerts.map(a => `
                        <div class="alert-item">
                            <div class="alert-dot"></div>
                            ${a}
                        </div>`).join('');
                document.getElementById('alertsSection').style.display = 'block';
            }

            // CPU
            const cpu = data.cpu_metrics;
            document.getElementById('cpuCard').innerHTML =
                createMetricRow('Workload Level',    cpu.workload_level.value,    cpu.workload_level.meaning,    cpu.workload_level.label) +
                createMetricRow('Responsiveness',    cpu.responsiveness.value,    cpu.responsiveness.meaning,    cpu.responsiveness.label) +
                createMetricRow('Capacity Left',     cpu.capacity_left.value,     cpu.capacity_left.meaning,     cpu.capacity_left.label);

            // Memory
            const mem = data.memory_metrics;
            document.getElementById('memCard').innerHTML =
                createMetricRow('Comfort Level',       mem.comfort_level.value,       mem.comfort_level.meaning,       mem.comfort_level.label) +
                createMetricRow('Multitasking Ability', mem.multitasking_ability.value, mem.multitasking_ability.meaning, mem.multitasking_ability.label) +
                createMetricRow('Stability Risk',      mem.stability_risk.value,      mem.stability_risk.meaning,      mem.stability_risk.label);
        }
    </script>
</body>
</html>
"""

# PYTHON CODE

def get_cpu_metrics():
    try:
        with open("/proc/stat") as f:
            for line in f:
                if line.startswith("cpu "):
                    parts = line.split()
                    user   = int(parts[1])
                    nice   = int(parts[2])
                    system = int(parts[3])
                    idle   = int(parts[4])
                    iowait = int(parts[5])
                    total  = user + nice + system + idle + iowait
                    usage  = round((user + system) / total * 100, 2) if total > 0 else 0
                    usage  = max(usage, 0.1)

                    workload     = "Low"    if usage < 40 else "Medium"        if usage < 70 else "High"
                    responsiveness = "Fast" if usage < 30 else "Slightly Slow" if usage < 60 else "Slow"
                    capacity     = "Good"   if usage < 60 else "Limited"       if usage < 80 else "Critical"

                    return {
                        "workload_level": {"label": workload,       "value": f"{usage}%",       "meaning": "CPU load level"},
                        "responsiveness": {"label": responsiveness, "value": f"{100-usage}% available", "meaning": "System response speed"},
                        "capacity_left":  {"label": capacity,       "value": f"{100-usage}% idle", "meaning": "Remaining CPU capacity"},
                        "usage_percent": usage
                    }
    except Exception:
        pass
    return {k: {"label": "Error", "value": "N/A", "meaning": "Failed to read"} for k in
            ["workload_level", "responsiveness", "capacity_left"]} | {"usage_percent": 0}


def get_memory_metrics():
    try:
        meminfo = {}
        with open("/proc/meminfo") as f:
            for line in f:
                parts = line.split(":")
                if len(parts) == 2:
                    meminfo[parts[0].strip()] = int(parts[1].strip().split()[0])

        total     = meminfo.get("MemTotal", 1)
        available = meminfo.get("MemAvailable", meminfo.get("MemFree", 0))
        used      = total - available
        swap_total = meminfo.get("SwapTotal", 0)
        swap_free  = meminfo.get("SwapFree", 0)
        swap_pct   = round(((swap_total - swap_free) / swap_total) * 100, 2) if swap_total > 0 else 0
        used_pct   = round((used / total) * 100, 2)
        avail_pct  = round((available / total) * 100, 2)

        comfort   = "Comfortable" if avail_pct > 30 else "Tight"   if avail_pct > 15 else "Critical"
        multitask = "Smooth"      if swap_pct < 10  else "Limited" if swap_pct < 30  else "Poor"
        risk      = "Low"         if used_pct < 80  else "Medium"  if used_pct < 90  else "High"

        return {
            "comfort_level":       {"label": comfort,    "value": f"{avail_pct}% free",    "meaning": "Available memory level"},
            "multitasking_ability":{"label": multitask,  "value": f"{swap_pct}% swap used","meaning": "Ability to run multiple apps"},
            "stability_risk":      {"label": risk,       "value": f"{used_pct}% used",     "meaning": "Risk of slowdown or freeze"},
            "usage_percent": used_pct
        }
    except Exception:
        return {k: {"label": "Error", "value": "N/A", "meaning": "Failed to read"} for k in
                ["comfort_level", "multitasking_ability", "stability_risk"]} | {"usage_percent": 0}


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
    if not messages:   messages.append("System operating normally")
    return health, status, messages


# ROUTES

@app.route("/")
def home():
    return render_template_string(HOME_HTML)

@app.route("/dashboard")
def dashboard():
    return render_template_string(DASHBOARD_HTML)

@app.route("/uptime")
def uptime():
    return jsonify({"uptime_seconds": int(time.time() - start_time)})

@app.route("/analyze")
def analyze():
    try:
        cpu = get_cpu_metrics()
        mem = get_memory_metrics()
        health, status, alerts = calculate_health(cpu["usage_percent"], mem["usage_percent"])
        return jsonify({
            "timestamp":       datetime.utcnow().isoformat() + "Z",
            "uptime_seconds":  int(time.time() - start_time),
            "cpu_metrics":     cpu,
            "memory_metrics":  mem,
            "health_score":    health,
            "status":          status,
            "alerts":          alerts
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
