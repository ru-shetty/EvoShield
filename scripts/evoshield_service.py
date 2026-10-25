"""Per-user Windows supervisor for the local EvoShield dashboard and agent."""
import argparse
import os
import signal
import subprocess
import sys
import time
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen


def endpoint_ready(url):
    try:
        with urlopen(url, timeout=2):
            return True
    except (OSError, URLError):
        return False


def main():
    parser = argparse.ArgumentParser(description="Run the EvoShield local protection service")
    parser.add_argument("--watch", action="append", required=True)
    parser.add_argument("--interval", type=int, default=10)
    args = parser.parse_args()
    project = Path(__file__).resolve().parents[1]
    python = Path(sys.executable)
    env = os.environ.copy()
    env.setdefault("PYTHONUNBUFFERED", "1")
    logs = Path(os.environ.get("LOCALAPPDATA", Path.home())) / "EvoShield" / "logs"
    logs.mkdir(parents=True, exist_ok=True)
    children = {}
    stopping = False

    def launch(name, command):
        stream = open(logs / f"{name}.log", "a", encoding="utf-8")
        children[name] = subprocess.Popen(
            command, cwd=project, env=env, stdin=subprocess.DEVNULL,
            stdout=stream, stderr=subprocess.STDOUT,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )

    def stop(_signum=None, _frame=None):
        nonlocal stopping
        stopping = True

    signal.signal(signal.SIGINT, stop)
    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, stop)
    agent_command = [str(python), str(project / "scripts" / "evoshield_agent.py")]
    for root in args.watch:
        agent_command.extend(["--watch", root])
    agent_command.extend(["--interval", str(max(5, args.interval))])

    while not stopping:
        server = children.get("server")
        if server is None or server.poll() is not None:
            launch("server", [str(python), "manage.py", "runserver", "127.0.0.1:8000", "--noreload"])
            time.sleep(2)
        if endpoint_ready("http://127.0.0.1:8000/api/v1/scans/"):
            agent = children.get("agent")
            if agent is None or agent.poll() is not None:
                launch("agent", agent_command)
        time.sleep(3)

    for process in children.values():
        if process.poll() is None:
            process.terminate()
    for process in children.values():
        try:
            process.wait(timeout=8)
        except subprocess.TimeoutExpired:
            process.kill()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
