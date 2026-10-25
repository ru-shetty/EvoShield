"""Monitor selected Windows folders and hold new files until both scanners clear them.

Files are copied into %LOCALAPPDATA%\\EvoShield\\quarantine before analysis.
The agent never executes a file. Held items and their JSON manifests remain in
the quarantine folder for manual review.
"""
import argparse
import base64
import hashlib
import json
import mimetypes
import os
import shutil
import subprocess
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

MAX_API_BYTES = 20 * 1024 * 1024
DEFENDER_TIMEOUT_SECONDS = 30 * 60


class DefenderThreatDetected(RuntimeError):
    """Defender identified or removed the staged file."""


def _sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _api_scan(path, endpoint, original_name):
    raw = path.read_bytes()
    kind = "image" if (mimetypes.guess_type(original_name)[0] or "").startswith("image/") else "file"
    payload = json.dumps({
        "type": kind,
        "source": "desktop-agent",
        "subject": original_name,
        "content_base64": base64.b64encode(raw).decode("ascii"),
    }).encode()
    request = Request(endpoint, data=payload, headers={"Content-Type": "application/json"}, method="POST")
    with urlopen(request, timeout=90) as response:
        result = json.loads(response.read().decode("utf-8"))
    if (not isinstance(result, dict)
            or result.get("verdict") not in {"LOW", "MEDIUM", "HIGH", "REVIEW"}
            or not result.get("entity_id")):
        raise RuntimeError("EvoShield returned an incomplete scan result")
    return result


def _defender_executable():
    program_data = Path(os.environ.get("ProgramData", r"C:\ProgramData"))
    platforms = program_data / "Microsoft" / "Windows Defender" / "Platform"
    candidates = list(platforms.glob("*/MpCmdRun.exe")) if platforms.is_dir() else []
    fallback = Path(os.environ.get("ProgramFiles", r"C:\Program Files")) / "Windows Defender" / "MpCmdRun.exe"
    if fallback.is_file():
        candidates.append(fallback)
    if not candidates:
        raise RuntimeError("Microsoft Defender command-line scanner was not found")
    # Version folders sort lexically; numeric components make that ordering reliable.
    def version_key(path):
        parent = path.parent.name
        return tuple(int(part) if part.isdigit() else -1 for part in parent.replace("-", ".").split("."))
    return max(candidates, key=version_key)


def _powershell_json(script, scan_path=None, timeout=30):
    powershell = shutil.which("powershell.exe") or shutil.which("powershell")
    if not powershell:
        raise RuntimeError("Windows PowerShell is unavailable")
    env = os.environ.copy()
    if scan_path is not None:
        env["EVOSHIELD_SCAN_PATH"] = str(scan_path)
    completed = subprocess.run(
        [powershell, "-NoProfile", "-NonInteractive", "-Command", script],
        capture_output=True, text=True, timeout=timeout, env=env, check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError((completed.stderr or completed.stdout or "PowerShell scan helper failed").strip()[-1000:])
    try:
        return json.loads(completed.stdout.strip().splitlines()[-1])
    except (json.JSONDecodeError, IndexError) as error:
        raise RuntimeError("Windows Defender did not return a readable status") from error


def _defender_scan(path):
    """Return clean only if Defender is active, recent, successful, and reports no hit."""
    if os.name != "nt":
        raise RuntimeError("Automatic release is supported only on Windows")
    status_script = (
        "$ErrorActionPreference='Stop'; Import-Module Defender; "
        "$s=Get-MpComputerStatus; "
        "[pscustomobject]@{active=([bool]$s.AMServiceEnabled -and [bool]$s.AntivirusEnabled -and [bool]$s.RealTimeProtectionEnabled); "
        "signatureUpdated=$s.AntivirusSignatureLastUpdated} | ConvertTo-Json -Compress"
    )
    status = _powershell_json(status_script)
    try:
        updated = datetime.fromisoformat(str(status["signatureUpdated"]).replace("Z", "+00:00"))
        if updated.tzinfo is None:
            updated = updated.replace(tzinfo=timezone.utc)
    except (KeyError, TypeError, ValueError) as error:
        raise RuntimeError("Could not verify Microsoft Defender security-intelligence age") from error
    if not status.get("active"):
        raise RuntimeError("Microsoft Defender real-time antivirus is not active")
    if (datetime.now(timezone.utc) - updated.astimezone(timezone.utc)).total_seconds() > 7 * 86400:
        raise RuntimeError("Microsoft Defender security intelligence is more than seven days old")

    scanner = _defender_executable()
    exclusion_check = subprocess.run(
        [str(scanner), "-CheckExclusion", "-Path", str(path)],
        capture_output=True, text=True, timeout=60, check=False,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )
    if exclusion_check.returncode == 0:
        raise RuntimeError("Microsoft Defender excludes the EvoShield quarantine path")
    if exclusion_check.returncode != 1:
        raise RuntimeError("Could not verify that Microsoft Defender scans the quarantine path")
    completed = subprocess.run(
        [str(scanner), "-Scan", "-ScanType", "3", "-File", str(path)],
        capture_output=True, text=True, timeout=DEFENDER_TIMEOUT_SECONDS, check=False,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )
    if completed.returncode != 0:
        output = (completed.stdout + "\n" + completed.stderr).strip()
        raise RuntimeError(f"Microsoft Defender scan did not complete cleanly (code {completed.returncode}): {output[-500:]}")

    # A zero exit code can also mean a threat was successfully remediated. Look up
    # Defender's active and past detections for this uniquely named quarantine path.
    detection_script = r'''
$ErrorActionPreference='Stop'; Import-Module Defender
$target=[IO.Path]::GetFullPath($env:EVOSHIELD_SCAN_PATH)
$found=$false
foreach($d in @(Get-MpThreatDetection)) {
  foreach($r in @($d.Resources)) {
    $candidate=[string]$r
    if($candidate.StartsWith('file:',[StringComparison]::OrdinalIgnoreCase)) { $candidate=$candidate.Substring(5).TrimStart('_') }
    if([string]::Equals($candidate,$target,[StringComparison]::OrdinalIgnoreCase)) { $found=$true }
  }
}
[pscustomobject]@{detected=$found} | ConvertTo-Json -Compress
'''
    detection = _powershell_json(detection_script, scan_path=path)
    if not path.is_file():
        raise DefenderThreatDetected("Microsoft Defender removed or quarantined the item")
    if detection.get("detected"):
        raise DefenderThreatDetected("Microsoft Defender reported a detection for this item")
    return {"engine": "Microsoft Defender Antivirus", "result": "clean", "return_code": completed.returncode}


def _finalize_api_record(endpoint, entity_id, defender_status, reason=""):
    api_base = endpoint.rstrip("/").rsplit("/", 1)[0]
    url = f"{api_base}/scans/{entity_id}/finalize/"
    body = json.dumps({"defender_status": defender_status, "reason": reason}).encode()
    request = Request(url, data=body, headers={"Content-Type": "application/json"}, method="POST")
    with urlopen(request, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


def _stage_file(source, processing_dir, expected_marker):
    """Copy to private staging, verify the copy, and only then remove the source."""
    source_stat = source.stat()
    if (source_stat.st_size, source_stat.st_mtime_ns) != expected_marker:
        raise RuntimeError("The incoming file changed while it was being staged")
    processing_dir.mkdir(parents=True, exist_ok=False)
    payload = processing_dir / ("payload" + source.suffix.lower()[:20])
    partial = payload.with_name(payload.name + ".partial")
    shutil.copy2(source, partial)
    with partial.open("rb") as stream:
        os.fsync(stream.fileno())
    copied_stat = source.stat()
    if (copied_stat.st_size, copied_stat.st_mtime_ns) != expected_marker:
        raise RuntimeError("The incoming file changed during the copy; the original was retained")
    digest = _sha256(partial)
    if partial.stat().st_size != expected_marker[0]:
        raise RuntimeError("The quarantine copy has a different size; the original was retained")
    os.replace(partial, payload)
    source.unlink()
    return payload, digest


def _write_manifest(folder, manifest):
    temp = folder / "manifest.json.tmp"
    temp.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    os.replace(temp, folder / "manifest.json")


def _notify(title, message):
    try:
        from winotify import Notification
        Notification(app_id="EvoShield", title=title, msg=message).show()
    except Exception:
        # The persistent agent log remains available when Windows toasts are disabled.
        pass


def _unused_destination(original):
    if not original.exists():
        return original
    for number in range(1, 10000):
        candidate = original.with_name(f"{original.stem} (EvoShield released {number}){original.suffix}")
        if not candidate.exists():
            return candidate
    raise RuntimeError("Could not find a free filename beside the original")


def _release(payload, destination, expected_digest):
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination = _unused_destination(destination)
    temp = destination.with_name(destination.name + ".evoshield-partial")
    try:
        shutil.copy2(payload, temp)
        if _sha256(temp) != expected_digest:
            raise RuntimeError("Released copy did not match the quarantined file")
        os.replace(temp, destination)
        payload.unlink()
    finally:
        try:
            temp.unlink(missing_ok=True)
        except OSError:
            pass
    return destination


def _process(source, expected_marker, folders, endpoint):
    item_id = uuid.uuid4().hex
    processing_dir = folders["processing"] / item_id
    held_dir = folders["held"] / item_id
    original = source.absolute()
    payload = None
    try:
        payload, digest = _stage_file(source, processing_dir, expected_marker)
        manifest = {
            "id": item_id,
            "original_path": str(original),
            "quarantined_at": datetime.now(timezone.utc).isoformat(),
            "sha256": digest,
            "size_bytes": payload.stat().st_size,
            "status": "Scanning",
        }
        _write_manifest(processing_dir, manifest)

        if manifest["size_bytes"] > MAX_API_BYTES:
            raise RuntimeError("Over 20 MiB: the EvoShield file-analysis endpoint cannot inspect this size")
        result = _api_scan(payload, endpoint, original.name)
        manifest["evoshield"] = {
            "verdict": result["verdict"],
            "risk_score": result.get("risk_score"),
            "entity_id": result.get("entity_id"),
        }
        if result["verdict"] != "LOW":
            if result.get("entity_id"):
                _finalize_api_record(endpoint, result["entity_id"], "not_run", "EvoShield did not clear this file.")
            raise RuntimeError(f"EvoShield marked this item {result['verdict']} risk")

        try:
            manifest["defender"] = _defender_scan(payload)
        except DefenderThreatDetected as error:
            if result.get("entity_id"):
                _finalize_api_record(endpoint, result["entity_id"], "detected", str(error))
            raise
        except Exception as error:
            if result.get("entity_id"):
                _finalize_api_record(endpoint, result["entity_id"], "unavailable", str(error))
            raise
        if result.get("entity_id"):
            _finalize_api_record(endpoint, result["entity_id"], "clean")
        released = _release(payload, original, digest)
        manifest.update({"status": "Released after both scans were clear", "released_path": str(released)})
        _write_manifest(processing_dir, manifest)
        (folders["released"] / f"{item_id}.json").write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        shutil.rmtree(processing_dir, ignore_errors=True)
        print(f"SAFE: Both scans were clear; released to {released}")
        return released
    except Exception as error:
        # If the source still exists, staging failed before it could be held.
        # Remove any incomplete copy and let the next poll retry it.
        if source.exists():
            shutil.rmtree(processing_dir, ignore_errors=True)
            print(f"Could not quarantine {original}; original file remains in place: {error}")
            return False
        held_dir.parent.mkdir(parents=True, exist_ok=True)
        if processing_dir.exists():
            manifest = locals().get("manifest", {
                "id": item_id,
                "original_path": str(original),
                "quarantined_at": datetime.now(timezone.utc).isoformat(),
                "status": "Held; scan not completed",
            })
            manifest["status"] = "Held in quarantine; not cleared for release"
            manifest["reason"] = str(error)[:1000]
            try:
                _write_manifest(processing_dir, manifest)
                if held_dir.exists():
                    held_dir = folders["held"] / f"{item_id}-{uuid.uuid4().hex[:8]}"
                os.replace(processing_dir, held_dir)
            except OSError as move_error:
                print(f"QUARANTINE ERROR: {move_error}; item remains at {processing_dir}")
        elif payload is None:
            # Staging failed before the source could be removed. Do not move or alter it.
            print(f"Could not quarantine {original}; original file remains in place: {error}")
            return
        print(f"HELD: {original.name} remains in quarantine ({error})")
        _notify("EvoShield held an incoming file", f"{original.name}: {str(error)[:180]}")
        return None


def _recover_interrupted(folders):
    for item in folders["processing"].iterdir():
        if not item.is_dir():
            continue
        manifest_path = item / "manifest.json"
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {}
        except (OSError, json.JSONDecodeError):
            manifest = {}
        manifest.setdefault("id", item.name)
        manifest.setdefault("status", "Held after an interrupted scan; manual review required")
        manifest["reason"] = "The agent stopped before both scanners cleared this file."
        _write_manifest(item, manifest)
        destination = folders["held"] / item.name
        if destination.exists():
            destination = folders["held"] / f"{item.name}-{uuid.uuid4().hex[:8]}"
        os.replace(item, destination)
        print(f"Recovered interrupted item into quarantine: {destination}")


def _baseline_existing(roots):
    """Treat files present at startup as pre-existing, not newly arriving items."""
    baseline = {}
    for root in roots:
        try:
            for path in root.rglob("*"):
                try:
                    if path.is_file() and path.suffix.lower() not in {".crdownload", ".part", ".download", ".partial"}:
                        stat = path.stat()
                        baseline[str(path.resolve())] = (stat.st_size, stat.st_mtime_ns)
                except OSError:
                    continue
        except OSError as error:
            print(f"Could not snapshot existing files in {root}: {error}")
    return baseline


def main():
    parser = argparse.ArgumentParser(description="Quarantine and scan incoming files in selected Windows folders")
    parser.add_argument("--watch", action="append", required=True, help="Folder to monitor; repeat for more folders")
    parser.add_argument("--interval", type=int, default=10, help="Polling interval in seconds (minimum 5)")
    parser.add_argument("--endpoint", default="http://127.0.0.1:8000/api/v1/scan/")
    parser.add_argument("--quarantine", help="Override quarantine folder; default is %LOCALAPPDATA%\\EvoShield\\quarantine")
    args = parser.parse_args()
    roots = [Path(value).expanduser().resolve() for value in args.watch]
    for root in roots:
        if not root.is_dir():
            parser.error(f"Watch folder does not exist: {root}")
    local_app_data = Path(os.environ.get("LOCALAPPDATA", Path.home()))
    quarantine = Path(args.quarantine).expanduser().resolve() if args.quarantine else local_app_data / "EvoShield" / "quarantine"
    folders = {name: quarantine / name for name in ("processing", "held", "released")}
    for folder in folders.values():
        folder.mkdir(parents=True, exist_ok=True)
    _recover_interrupted(folders)
    interval = max(5, args.interval)
    pending = {}
    seen = _baseline_existing(roots)
    root_strings = [str(root).casefold() for root in roots]
    if any(str(quarantine).casefold() == root or str(quarantine).casefold().startswith(root + os.sep.casefold()) for root in root_strings):
        parser.error("The quarantine folder must be outside every monitored folder")
    print("EvoShield incoming-file protection is active. Watching:", ", ".join(map(str, roots)))
    print(f"Quarantine: {quarantine}")
    print("Stable files are held before scanning. Only EvoShield LOW plus a clean Microsoft Defender scan is released.")
    print(f"Existing files were left in place. New or changed files are checked every {interval} seconds.")
    while True:
        for root in roots:
            try:
                for source in root.rglob("*"):
                    if not source.is_file():
                        continue
                    try:
                        if source.suffix.lower() in {".crdownload", ".part", ".download", ".partial"}:
                            continue
                        stat = source.stat()
                        marker = (stat.st_size, stat.st_mtime_ns)
                        key = str(source.resolve())
                        if seen.get(key) == marker:
                            continue
                        if pending.get(key) != marker:
                            pending[key] = marker
                            continue
                        # Remove from the debounce table before processing; a file
                        # recreated at the same path will be observed as a new item.
                        pending.pop(key, None)
                        outcome = _process(source, marker, folders, args.endpoint)
                        if outcome is not False:
                            seen[key] = marker
                            if isinstance(outcome, Path):
                                released_stat = outcome.stat()
                                seen[str(outcome.resolve())] = (released_stat.st_size, released_stat.st_mtime_ns)
                    except (OSError, PermissionError) as error:
                        print(f"Could not inspect incoming item {source}: {error}")
                    except Exception as error:
                        print(f"Agent error for {source}: {error}")
            except OSError as error:
                print(f"Could not scan {root}: {error}")
        time.sleep(interval)


if __name__ == "__main__":
    main()
