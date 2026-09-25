import hashlib
import json
import uuid
from pathlib import Path

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from backend.dashboard.models import ScanRecord
from backend.modules.M09_digital_arrest_impersonation_detection.algorithms.digital_arrest_detector import (
    detect_digital_arrest,
)


def dashboard(request):
    return render(request, "dashboard/index.html")


def _analyze_text(text):
    digital_arrest = detect_digital_arrest(text)
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
            arrest, text_analysis = _analyze_text(content)
            details.update({"digital_arrest": arrest, "text_analysis": text_analysis})
            # Preserve the independent M09 result while fusing general M03 text
            # evidence into the shared risk score.
            score = max(
                float(arrest.get("digital_arrest_probability", 0)),
                float(text_analysis.get("score", 0)),
            )
            verdict = "HIGH" if score >= .6 else "MEDIUM" if score >= .3 else "LOW"
            subject = subject or "Text submission"
    elif kind == "file":
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
        return JsonResponse({"error": "Supported types are text, url, and file."}, status=400)

    record = ScanRecord.objects.create(
        entity_id=str(uuid.uuid4()),
        source=source,
        entity_type=kind,
        subject=subject,
        verdict=verdict,
        risk_score=score,
        details=details,
    )
    return JsonResponse(_serialize(record), status=201)


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
    rows = [_serialize(item) for item in ScanRecord.objects.all()[:100]]
    return JsonResponse({"scans": rows, "total": ScanRecord.objects.count()})
