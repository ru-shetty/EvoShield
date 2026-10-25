"""Opt-in Windows system-audio monitor for live call speech.

Captures the default output device locally, transcribes short windows with
Faster Whisper, and submits only suspicious transcript text to EvoShield.
"""
import argparse
import json
import sys
import time
from collections import deque
from pathlib import Path
from urllib.request import Request, urlopen


INDICATOR_EXPLANATIONS = {
    "government_or_police_impersonation": "The caller claims to be police or another government authority.",
    "threat_language": "The caller threatens arrest or legal action.",
    "urgency": "The caller pressures you to act immediately.",
    "financial_request": "The caller asks for a payment or money transfer.",
    "otp_pin_aadhaar_pan_request": "The caller asks for an OTP, PIN, Aadhaar, PAN, or banking details.",
    "fake_document_indicators": "The caller refers to an official-looking notice or warrant.",
    "call_pressure": "The caller pressures you to stay on the call or keep it secret.",
}


def explain_indicators(indicators):
    explanations = [INDICATOR_EXPLANATIONS[key] for key in indicators if key in INDICATOR_EXPLANATIONS]
    return " ".join(explanations) or "The call contains language commonly used to pressure or frighten people."


def send_alert(endpoint, text, call_type):
    call_label = {"video": "video", "both": "voice and video", "voice": "voice"}[call_type]
    payload = json.dumps({
        "type": "text",
        "source": "windows-live-call",
        "subject": f"Windows {call_label} call warning",
        "call_type": call_type,
        "content": text,
    }).encode("utf-8")
    request = Request(endpoint, data=payload, headers={"Content-Type": "application/json"})
    with urlopen(request, timeout=10) as response:
        return json.loads(response.read().decode("utf-8"))


def notify(title, message):
    try:
        from winotify import Notification
        Notification(app_id="EvoShield", title=title, msg=message, duration="long").show()
    except Exception:
        print(f"\a{title}: {message}", flush=True)


def main():
    parser = argparse.ArgumentParser(description="Monitor call speech from the Windows default audio output")
    parser.add_argument("--model", default="base", help="Faster Whisper model: tiny, base, small, medium, or large-v3")
    parser.add_argument("--language", choices=("auto", "en", "hi"), default="auto", help="Speech language: auto, English (en), or Hindi (hi)")
    parser.add_argument("--call-type", choices=("voice", "video", "both"), default="voice", help="Call type selected in the EvoShield dashboard")
    parser.add_argument("--window-seconds", type=int, default=6)
    parser.add_argument("--endpoint", default="http://127.0.0.1:8000/api/v1/scan/")
    args = parser.parse_args()
    project = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(project))
    try:
        import numpy as np
        import soundcard as sc
        from faster_whisper import WhisperModel
    except ImportError as error:
        parser.error(f"Install optional live-call dependencies with scripts\\install_live_call_monitor.ps1 ({error})")

    speaker = sc.default_speaker()
    if speaker is None:
        parser.error("No default Windows audio output device is available.")
    loopback = sc.get_microphone(id=str(speaker.name), include_loopback=True)
    print(f"Monitoring output audio device: {speaker.name}")
    print(f"Preparing the local speech model ({args.model}, language: {args.language})...")
    model = WhisperModel(args.model, device="cpu", compute_type="int8")
    print("Speech model ready. Monitoring is active while enabled in EvoShield; audio is processed in memory.")
    print("Audio stays in memory; only suspicious transcript text is sent to the local EvoShield API.")
    from backend.modules.M09_digital_arrest_impersonation_detection.algorithms.digital_arrest_detector import detect_digital_arrest

    context = deque(maxlen=10)
    alert_active = False
    normal_since = None
    last_diagnostic = 0.0
    frames = max(16_000, 16_000 * max(3, args.window_seconds))
    try:
        # SoundCard documents corrupted mono loopback on Windows/WASAPI; capture
        # the device's native channels and downmix after retrieval instead.
        with loopback.recorder(samplerate=16_000) as recorder:
            while True:
                audio = recorder.record(numframes=frames)
                if audio is None or not audio.size or float(np.max(np.abs(audio))) < 0.006:
                    continue
                samples = np.asarray(audio, dtype=np.float32)
                mono = samples.mean(axis=1) if samples.ndim > 1 else samples.reshape(-1)
                language = None if args.language == "auto" else args.language
                segments, _info = model.transcribe(mono, language=language, vad_filter=True, beam_size=1)
                recognized = " ".join(segment.text.strip() for segment in segments if segment.text.strip())
                if not recognized:
                    continue
                context.append(recognized)
                rolling_text = " ".join(context)
                result = detect_digital_arrest(rolling_text, call_type=args.call_type)
                probability = result["digital_arrest_probability"]
                now = time.monotonic()
                if now - last_diagnostic >= 30:
                    print(f"CALL_MONITOR_STATE:speech_analyzed risk={probability:.2f} category={result['category']}", flush=True)
                    last_diagnostic = now
                if probability < 0.30:
                    if alert_active:
                        if normal_since is None:
                            normal_since = now
                        elif now - normal_since >= 60:
                            alert_active = False
                            normal_since = None
                            print("CALL_MONITOR_STATE:alert_cleared", flush=True)
                    continue
                normal_since = None
                if alert_active:
                    continue
                alert_active = True
                print(f"CALL_MONITOR_STATE:alert_detected risk={probability:.2f} category={result['category']}", flush=True)
                call_label = {"video": "video call", "both": "voice/video call", "voice": "voice call"}[args.call_type]
                title = f"Possible digital-arrest scam in {call_label}" if result["category"] == "DIGITAL_ARREST" else f"Suspicious {call_label} language"
                reasons = explain_indicators(result["indicators"])
                notify(title, f"{reasons} Do not share one-time codes or transfer money under pressure.")
                print("CALL_MONITOR_STATE:desktop_notification_requested", flush=True)
                try:
                    send_alert(args.endpoint, rolling_text, args.call_type)
                    print("CALL_MONITOR_STATE:alert_saved", flush=True)
                except Exception as error:
                    print(f"Could not save warning to EvoShield history: {error}", flush=True)
    except KeyboardInterrupt:
        print("\nEvoShield call monitoring stopped.")


if __name__ == "__main__":
    main()
