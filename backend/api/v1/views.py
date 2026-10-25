import hashlib
import json
import os
import subprocess
import sys
import threading
import uuid
from datetime import timedelta
from pathlib import Path

from django.http import JsonResponse
from django.utils import timezone
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from backend.dashboard.models import ScanRecord
from backend.api.v1.notifications import notify_scan_result
from backend.modules.M09_digital_arrest_impersonation_detection.algorithms.digital_arrest_detector import (
    detect_digital_arrest,
)


_call_monitor_process = None
_call_monitor_log = None
_call_monitor_lock = threading.Lock()


def dashboard(request):
    return render(request, "dashboard/index.html")


def _analyze_text(text, call_type=None):
    digital_arrest = detect_digital_arrest(text, call_type=call_type)
    try:
        from backend.modules.M03_textual_threat_analysis.services.service import (
            TextualThreatAnalysisService,
        )

        text_analysis = TextualThreatAnalysisService().analyze_text_to_dict(text)
    except (ImportError, FileNotFoundError, ValueError):
        text_analysis = {"category": "UNAVAILABLE", "note": "Text model unavailable; rule-based analysis used."}
    return digital_arrest, text_analysis


@csrf_exempt
@require_POST
def scan(request):
    """Analyze user-submitted text, URL, or a file using static inspection only."""
    try:
        data = json.loads(request.body or b"{}")
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"error": "Request must contain valid JSON."}, status=400)
    if not isinstance(data, dict):
        return JsonResponse({"error": "Request JSON must be an object."}, status=400)
    kind = str(data.get("type", "text")).lower()
    source = str(data.get("source", "web"))[:32]
    subject = str(data.get("subject", ""))[:500]
    details = {}
    score = 0.0
    verdict = "LOW"
    if kind in {"text", "url"}:
        content = str(data.get("content", ""))[:100_000]
        if not content.strip():
            return JsonResponse({"error": "Provide content to analyze."}, status=400)
        if kind == "url":
            from backend.modules.M02_malicious_url_analysis.algorithms.url_analyzer import (
                MaliciousURLAnalyzer,
            )
            url_result = MaliciousURLAnalyzer().analyze(content)
            details["url_analysis"] = url_result
            score = float(url_result.get("score", 0))
            verdict = "HIGH" if score >= .75 else "MEDIUM" if score >= .4 else "LOW"
            subject = subject or content[:200]
        else:
            call_type = None
            if source == "windows-live-call":
                requested_type = str(data.get("call_type", "voice")).lower()
                call_type = requested_type if requested_type in {"voice", "video", "both"} else "voice"
            arrest, text_analysis = _analyze_text(content, call_type=call_type)
            details.update({"digital_arrest": arrest, "text_analysis": text_analysis})
            if source == "windows-live-call":
                details["call_details"] = {
                    "transcript": content[:12_000],
                    "indicators": arrest.get("indicators", []),
                    "category": arrest.get("category", "NORMAL"),
                    "confidence": arrest.get("confidence", 0),
                    "call_type": call_type,
                }
                subject = subject or f"Windows {call_type} call warning"
            # Preserve the independent M09 result while fusing general M03 text
            # evidence into the shared risk score.
            score = max(
                float(arrest.get("digital_arrest_probability", 0)),
                float(text_analysis.get("score", 0)),
            )
            verdict = "HIGH" if score >= .6 else "MEDIUM" if score >= .3 else "LOW"
            subject = subject or "Text submission"
    elif kind in {"file", "image"}:
        # The server never executes submitted files. This endpoint accepts bounded
        # base64 content for static signature/hash/metadata checks only.
        import base64
        try:
            raw = base64.b64decode(data.get("content_base64", ""), validate=True)
        except (ValueError, TypeError):
            return JsonResponse({"error": "File content must be base64 encoded."}, status=400)
        if len(raw) > 20 * 1024 * 1024:
            return JsonResponse({"error": "Maximum file size is 20 MB."}, status=413)
        digest = hashlib.sha256(raw).hexdigest()
        if kind == "image":
            try:
                from io import BytesIO
                from PIL import Image, ImageOps
                import pytesseract
                from pytesseract import Output
                import shutil
            except ImportError:
                return JsonResponse({"error": "Image scanning needs Pillow, pytesseract, and the Tesseract OCR engine. Run scripts\\install_image_ocr.ps1, then restart EvoShield."}, status=503)
            try:
                if not shutil.which("tesseract"):
                    system_tesseract = Path(os.environ.get("ProgramFiles", r"C:\Program Files")) / "Tesseract-OCR" / "tesseract.exe"
                    if system_tesseract.is_file():
                        pytesseract.pytesseract.tesseract_cmd = str(system_tesseract)
                with Image.open(BytesIO(raw)) as source_image:
                    if source_image.format not in {"PNG", "JPEG", "WEBP", "BMP", "TIFF", "GIF"}:
                        return JsonResponse({"error": "Supported image formats are PNG, JPEG, WEBP, BMP, TIFF, and GIF."}, status=400)
                    if source_image.width < 1 or source_image.height < 1 or source_image.width > 10000 or source_image.height > 10000:
                        return JsonResponse({"error": "Image dimensions must be between 1 and 10,000 pixels per side."}, status=400)
                    image = ImageOps.exif_transpose(source_image).convert("RGB")
                    ocr = pytesseract.image_to_data(image, output_type=Output.DICT, timeout=20)
            except pytesseract.TesseractNotFoundError:
                return JsonResponse({"error": "Tesseract OCR is not installed or not on PATH. Run scripts\\install_image_ocr.ps1, then restart EvoShield."}, status=503)
            except Exception as error:
                return JsonResponse({"error": f"Could not read this image: {error}"}, status=400)
            words = []
            confidences = []
            for token, confidence in zip(ocr.get("text", []), ocr.get("conf", [])):
                token = token.strip()
                try:
                    confidence = float(confidence)
                except (TypeError, ValueError):
                    continue
                if token and confidence >= 0:
                    words.append(token)
                    confidences.append(confidence / 100)
            extracted_text = " ".join(words)[:100_000]
            confidence = sum(confidences) / len(confidences) if confidences else 1.0
            image_analysis = {"characters_read": len(extracted_text), "ocr_confidence": round(confidence, 3)}
            if extracted_text:
                from backend.modules.M04_visual_content_ocr_analysis.algorithms.ocr_analyzer import VisualContentOCRAnalyzer
                ocr_result = VisualContentOCRAnalyzer().analyze(extracted_text, confidence)
                arrest, text_analysis = _analyze_text(extracted_text)
                score = max(float(ocr_result.get("score", 0)), float(arrest.get("digital_arrest_probability", 0)), float(text_analysis.get("score", 0)))
                verdict = "HIGH" if score >= .7 else "MEDIUM" if score >= .3 else "LOW"
                image_analysis.update({"indicators": ocr_result.get("indicators", []), "digital_arrest_category": arrest.get("category", "NORMAL"), "text_indicators": text_analysis.get("indicators", [])})
            else:
                score = 0.0
                verdict = "LOW"
                image_analysis["indicators"] = []
            details["image_ocr_analysis"] = image_analysis
            details["static_file_analysis"] = {"sha256": digest, "size_bytes": len(raw), "execution_performed": False}
            subject = subject or "Uploaded image"
        else:
            eicar = b"EICAR-STANDARD-ANTIVIRUS-TEST-FILE"
            suspicious_ext = Path(subject).suffix.lower() in {
                ".exe", ".dll", ".scr", ".js", ".vbs", ".ps1", ".bat", ".apk"
            }
            flagged = eicar in raw
            score = 1.0 if flagged else .35 if suspicious_ext else 0
            verdict = "HIGH" if flagged else "REVIEW" if suspicious_ext else "LOW"
            details["static_file_analysis"] = {
                "sha256": digest,
                "size_bytes": len(raw),
                "eicar_test_signature": flagged,
                "executable_or_script_extension": suspicious_ext,
                "execution_performed": False,
            }
            subject = subject or "Uploaded file"
    else:
        return JsonResponse({"error": "Supported types are text, url, file, and image."}, status=400)

    record = ScanRecord.objects.create(
        entity_id=str(uuid.uuid4()),
        source=source,
        entity_type=kind,
        subject=subject,
        verdict=verdict,
        risk_score=score,
        details=details,
    )
    notify_scan_result(record)
    return JsonResponse(_serialize(record), status=201)


@csrf_exempt
@require_POST
def finalize_agent_scan(request, entity_id):
    """Attach the Windows Defender result to a desktop-agent scan record."""
    try:
        data = json.loads(request.body or b"{}")
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"error": "Request must contain valid JSON."}, status=400)
    if not isinstance(data, dict):
        return JsonResponse({"error": "Request JSON must be an object."}, status=400)
    try:
        record = ScanRecord.objects.get(entity_id=entity_id, source="desktop-agent")
    except ScanRecord.DoesNotExist:
        return JsonResponse({"error": "Desktop scan record was not found."}, status=404)
    status = str(data.get("defender_status", ""))
    if status not in {"clean", "detected", "unavailable", "not_run"}:
        return JsonResponse({"error": "Invalid Defender scan status."}, status=400)
    reason = str(data.get("reason", ""))[:1000]
    record.details["combined_file_scan"] = {
        "windows_defender": status,
        "reason": reason,
        "release_rule": "EvoShield LOW and Windows Defender clean",
    }
    should_notify = False
    if status == "detected":
        record.verdict = "HIGH"
        record.risk_score = max(float(record.risk_score), 0.95)
        should_notify = True
    elif status == "unavailable" and record.verdict == "LOW":
        record.verdict = "REVIEW"
        record.risk_score = max(float(record.risk_score), 0.35)
        should_notify = True
    record.save(update_fields=("details", "verdict", "risk_score"))
    if should_notify:
        notify_scan_result(record)
    return JsonResponse(_serialize(record))


def _serialize(record):
    return {
        "entity_id": record.entity_id,
        "source": record.source,
        "type": record.entity_type,
        "subject": record.subject,
        "verdict": record.verdict,
        "risk_score": record.risk_score,
        "details": record.details,
        "created_at": record.created_at.isoformat(),
    }


@require_GET
def scan_history(request):
    try:
        limit = int(request.GET.get("limit", 25))
        offset = int(request.GET.get("offset", 0))
    except (TypeError, ValueError):
        return JsonResponse({"error": "Page limit and offset must be whole numbers."}, status=400)

    limit = min(max(limit, 1), 100)
    offset = max(offset, 0)
    records = ScanRecord.objects.all()
    if request.GET.get("day") == "today":
        records = records.filter(created_at__date=timezone.localdate())
    kind = request.GET.get("kind", "all")
    if kind == "call":
        records = records.filter(source__in=("windows-live-call", "android-call"))
    elif kind in {"text", "url", "file", "image"}:
        records = records.filter(entity_type=kind)
    total = records.count()
    all_records = ScanRecord.objects.all()
    stats = {
        "total": all_records.count(),
        "low": all_records.filter(verdict="LOW").count(),
        "review": all_records.filter(verdict__in=("MEDIUM", "REVIEW")).count(),
        "high": all_records.filter(verdict="HIGH").count(),
    }
    today = timezone.localdate()
    trend = []
    for days_ago in reversed(range(7)):
        day = today - timedelta(days=days_ago)
        trend.append({
            "day": day.isoformat(),
            "count": all_records.filter(created_at__date=day).count(),
        })
    rows = [_serialize(item) for item in records[offset:offset + limit]]
    return JsonResponse({
        "scans": rows,
        "total": total,
        "offset": offset,
        "limit": limit,
        "high_total": records.filter(verdict="HIGH").count(),
        "message_total": records.filter(entity_type="text").count(),
        "stats": stats,
        "trend": trend,
    })


@require_GET
def call_monitor_status(request):
    process = _call_monitor_process
    if process is None:
        return JsonResponse({"status": "off", "message": "Call monitoring is off."})
    exit_code = process.poll()
    if exit_code is not None:
        message = "Call monitor stopped unexpectedly. Check that the live-call packages and audio device are available."
        if _call_monitor_log and _call_monitor_log.exists():
            try:
                tail = _call_monitor_log.read_text(encoding="utf-8", errors="replace")[-1600:]
                lines = [line.strip() for line in tail.splitlines() if line.strip()]
                if lines:
                    message = lines[-1][:300]
            except OSError:
                pass
        return JsonResponse({"status": "error", "message": message})

    status = "starting"
    message = "Starting local speech model. The first start may take a few minutes while it downloads."
    if _call_monitor_log and _call_monitor_log.exists():
        try:
            log = _call_monitor_log.read_text(encoding="utf-8", errors="replace")[-8000:]
            if "Speech model ready." in log:
                status = "running"
                states = {
                    marker: log.rfind(marker)
                    for marker in (
                        "CALL_MONITOR_STATE:alert_saved",
                        "CALL_MONITOR_STATE:alert_detected",
                        "CALL_MONITOR_STATE:speech_analyzed",
                    )
                }
                latest_state = max(states, key=states.get) if max(states.values()) >= 0 else ""
                if latest_state == "CALL_MONITOR_STATE:alert_saved":
                    message = "Suspicious call speech was detected and saved to call history."
                elif latest_state == "CALL_MONITOR_STATE:alert_detected":
                    message = "Suspicious speech was detected, but the alert could not be confirmed in call history. Check the monitor log."
                elif latest_state == "CALL_MONITOR_STATE:speech_analyzed":
                    message = "Speech is being analyzed; the recent audio did not meet the suspicious-call alert threshold."
                else:
                    message = "Monitoring system playback and waiting for audible speech. Audio is processed in memory only."
        except OSError:
            pass
    return JsonResponse({"status": status, "message": message})


@require_POST
def call_monitor_start(request):
    """Start the opt-in Windows live-call speech monitor from the dashboard."""
    global _call_monitor_process, _call_monitor_log
    with _call_monitor_lock:
        if _call_monitor_process is not None and _call_monitor_process.poll() is None:
            return JsonResponse({"status": "running", "message": "Call monitoring is already on."}, status=200)

        try:
            import importlib.util

            missing = [name for name in ("soundcard", "faster_whisper", "numpy") if importlib.util.find_spec(name) is None]
        except (ImportError, ValueError):
            missing = ["soundcard", "faster_whisper", "numpy"]
        if missing:
            return JsonResponse({
                "status": "error",
                "message": "Call monitoring components are missing. Install them once with scripts\\install_live_call_monitor.ps1.",
            }, status=503)

        project = Path(__file__).resolve().parents[3]
        monitor_script = project / "scripts" / "evoshield_call_monitor.py"
        if not monitor_script.exists():
            return JsonResponse({"status": "error", "message": "The Windows call monitor is missing from this installation."}, status=500)

        app_data = Path(os.environ.get("LOCALAPPDATA", project)) / "EvoShield" / "logs"
        app_data.mkdir(parents=True, exist_ok=True)
        _call_monitor_log = app_data / "call_monitor.log"
        try:
            data = json.loads(request.body or b"{}")
        except (json.JSONDecodeError, UnicodeDecodeError):
            data = {}
        requested_type = str(data.get("call_type", "voice")).lower() if isinstance(data, dict) else "voice"
        call_type = requested_type if requested_type in {"voice", "video", "both"} else "voice"
        try:
            with _call_monitor_log.open("w", encoding="utf-8") as output:
                _call_monitor_process = subprocess.Popen(
                    [sys.executable, str(monitor_script), "--model", "base", "--call-type", call_type],
                    cwd=project,
                    stdin=subprocess.DEVNULL,
                    stdout=output,
                    stderr=subprocess.STDOUT,
                    creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
                )
        except OSError as error:
            _call_monitor_process = None
            return JsonResponse({"status": "error", "message": f"Could not start call monitoring: {error}"}, status=500)

        return JsonResponse({"status": "starting", "message": "Starting local call speech analysis."}, status=202)


@require_POST
def call_monitor_stop(request):
    """Stop the call monitor started from this EvoShield server process."""
    global _call_monitor_process
    with _call_monitor_lock:
        process = _call_monitor_process
        if process is None or process.poll() is not None:
            _call_monitor_process = None
            return JsonResponse({"status": "off", "message": "Call monitoring is already off."})
        process.terminate()
        try:
            process.wait(timeout=8)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)
        _call_monitor_process = None
        return JsonResponse({"status": "off", "message": "Call monitoring is off."})
