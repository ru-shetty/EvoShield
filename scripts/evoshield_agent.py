"""Opt-in Windows folder monitor for the local EvoShield service.

Usage: python scripts/evoshield_agent.py --watch C:\\Users\\you\\Downloads
It polls the chosen folders and submits newly changed files up to 20 MiB
to the local static-analysis endpoint. It never executes or deletes files.
"""
import argparse
import base64
import hashlib
import json
import time
from pathlib import Path
from urllib.request import Request, urlopen

MAX_BYTES = 20 * 1024 * 1024


def describe_scan(result):
    """Turn the static file result into a short message for the user."""
    details = result.get("details", {}).get("static_file_analysis", {})
    verdict = result.get("verdict", "LOW")
    if details.get("eicar_test_signature"):
        return "Test alert: this file matches the harmless EICAR antivirus test pattern."
    if verdict == "HIGH":
        return "High risk: a known test signature matched. Do not open the file."
    if verdict == "REVIEW":
        return "Needs review: this file type can run a program or script. EvoShield did not open or run it."
    return "No known test signature was found in this basic static check. That does not prove the file is safe."


def send_file(path, endpoint):
    raw = path.read_bytes()
    payload = json.dumps({"type": "file", "source": "desktop-agent", "subject": path.name,
                          "content_base64": base64.b64encode(raw).decode("ascii")}).encode()
    request = Request(endpoint, data=payload, headers={"Content-Type": "application/json"}, method="POST")
    with urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def main():
    parser = argparse.ArgumentParser(description="Monitor selected folders with EvoShield")
    parser.add_argument("--watch", action="append", required=True, help="Folder to monitor; repeat for more folders")
    parser.add_argument("--interval", type=int, default=30, help="Polling interval in seconds (minimum 10)")
    parser.add_argument("--endpoint", default="http://127.0.0.1:8000/api/v1/scan/")
    args = parser.parse_args()
    roots = [Path(value).expanduser().resolve() for value in args.watch]
    for root in roots:
        if not root.is_dir():
            parser.error(f"Watch folder does not exist: {root}")
    interval = max(10, args.interval)
    seen = {}
    pending = {}
    print("EvoShield agent active. Watching only:", ", ".join(map(str, roots)))
    print("Stop with Ctrl+C. Files are analyzed statically and never executed or removed.")
    while True:
        for root in roots:
            try:
                for path in root.rglob("*"):
                    if not path.is_file():
                        continue
                    try:
                        stat = path.stat()
                        marker = (stat.st_size, stat.st_mtime_ns)
                        if seen.get(str(path)) == marker:
                            continue
                        # Require the same size and modification time in two
                        # polling rounds so files still being downloaded are skipped.
                        if pending.get(str(path)) != marker:
                            pending[str(path)] = marker
                            continue
                        if stat.st_size > MAX_BYTES:
                            seen[str(path)] = marker
                            pending.pop(str(path), None)
                            print(f"Skipped over 20 MB: {path}")
                            continue
                        result = send_file(path, args.endpoint)
                        seen[str(path)] = marker
                        pending.pop(str(path), None)
                        print(f"{describe_scan(result)} File: {path}")
                    except (OSError, PermissionError) as error:
                        print(f"Could not inspect {path}: {error}")
                    except Exception as error:
                        print(f"Agent/API error for {path}: {error}")
            except OSError as error:
                print(f"Could not scan {root}: {error}")
        time.sleep(interval)


if __name__ == "__main__":
    main()
