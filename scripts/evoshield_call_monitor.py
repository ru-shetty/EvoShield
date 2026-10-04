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


def send_alert(endpoint, text):
    payload = json.dumps({
        "type": "text",
        "source": "windows-live-call",
        "subject": "Live call speech warning",
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
    print("EvoShield is listening only while this window is open. Press Ctrl+C to stop.")
    print("Audio stays in memory; only suspicious transcript text is sent to the local EvoShield API.")
    model = WhisperModel(args.model, device="cpu", compute_type="int8")
    from backend.modules.M09_digital_arrest_impersonation_detection.algorithms.digital_arrest_detector import detect_digital_arrest

    context = deque(maxlen=10)
    last_alert = 0.0
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
                segments, _info = model.transcribe(mono, language=None, vad_filter=True, beam_size=1)
                recognized = " ".join(segment.text.strip() for segment in segments if segment.text.strip())
                if not recognized:
                    continue
                print(f"Heard: {recognized}", flush=True)
                context.append(recognized)
                rolling_text = " ".join(context)
                result = detect_digital_arrest(rolling_text)
                probability = result["digital_arrest_probability"]
                if probability < 0.30 or time.monotonic() - last_alert < 30:
                    continue
                last_alert = time.monotonic()
                title = "Possible digital-arrest scam" if result["category"] == "DIGITAL_ARREST" else "Suspicious call language"
                labels = ", ".join(result["indicators"].keys())
                notify(title, f"Indicators: {labels}. Do not share OTPs or send money.")
                try:
                    send_alert(args.endpoint, rolling_text)
                except Exception as error:
                    print(f"Could not save warning to EvoShield history: {error}", flush=True)
    except KeyboardInterrupt:
        print("\nEvoShield call monitoring stopped.")


if __name__ == "__main__":
    main()
