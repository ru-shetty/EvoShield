# EvoShield

EvoShield is a local security monitoring prototype based on the 16-module specification. It provides a browser dashboard, a Django API, persistent scan history, message and digital-arrest analysis, URL analysis, static file checks, and an opt-in Windows folder watcher.

## Run on Windows

1. Install Python 3.10 or newer.
2. From the project folder, create and activate a virtual environment, then install dependencies:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

3. Start the local dashboard. This creates the SQLite tables on first run:

   ```powershell
   .\scripts\start_evoshield.ps1
   ```

4. Open [http://127.0.0.1:8000](http://127.0.0.1:8000).

The server binds to loopback only and scan history is stored in `database/evoshield.sqlite3`.

## Install continuous Windows monitoring

From PowerShell in the project folder, install the dependencies and register EvoShield to start for your Windows account at sign-in:

```powershell
.\scripts\install_evoshield.ps1
```

By default, EvoShield monitors Downloads and Desktop every 30 seconds. Select folders and a polling interval with:

```powershell
.\scripts\install_evoshield.ps1 -WatchFolder "$env:USERPROFILE\Downloads", "$env:USERPROFILE\Documents" -IntervalSeconds 15
```

The background task starts the local dashboard and folder agent, restarts either if it exits, and writes service logs under `%LOCALAPPDATA%\EvoShield\logs`. The dashboard is at [http://127.0.0.1:8000](http://127.0.0.1:8000). Remove automatic startup with:

```powershell
.\scripts\uninstall_evoshield.ps1
```

Uninstalling keeps scan history and settings. Remove `%LOCALAPPDATA%\EvoShield` and `database/evoshield.sqlite3` separately to delete them.

## Manual continuous folder monitoring

Keep the dashboard server running, open a second PowerShell window in the project folder, and start the agent with folders you want monitored:

```powershell
python scripts/evoshield_agent.py --watch "$env:USERPROFILE\Downloads" --watch "$env:USERPROFILE\Desktop"
```

The agent checks selected folders for newly added or changed executable and script files. It reports static results to the local dashboard. Remove folders from the command to stop monitoring them. The watcher does not monitor browser traffic, memory, system processes, or the whole device.

## Live-call digital-arrest monitoring

Call monitoring is a separate, opt-in session. It does not start automatically at sign-in.

### Windows: WhatsApp Desktop, Zoom, and Google Meet

Install the optional audio and local speech-recognition components once:

```powershell
.\scripts\install_live_call_monitor.ps1
```

Start the dashboard with `scripts\start_evoshield.ps1`, then start monitoring when you join a call:

```powershell
.\.venv\Scripts\python.exe .\scripts\evoshield_call_monitor.py
```

This captures audio from the default Windows playback device, so it can hear call audio routed there, regardless of which listed app is open. It also captures other sounds played by that device while the monitor is active. Keep the terminal open and press Ctrl+C to stop. Faster Whisper runs locally; its speech model downloads on first start. Raw audio is held in memory only. Suspicious transcript text is sent to the local API to create a scan-history record, and a Windows notification is shown.

### Android: WhatsApp calls

Open the `android` folder in Android Studio and follow [android/README.md](android/README.md). The user must start monitoring for each session and grant microphone permission when Android asks. Recognition is on-device and no audio or transcript is sent to the server. Android restricts access to other apps' voice-call audio, so EvoShield listens through the phone microphone; WhatsApp may hold the microphone and speakerphone may be required. This is best-effort and will not work reliably with every phone or headset.

Both call monitors use the digital-arrest rule detector, which includes common English and Hindi phrases. Recognition quality depends on the speech model and language. They provide warning indicators, not guaranteed scam detection, and do not record, block, or end calls. Stop monitoring when the call ends.

## API

- `POST /api/v1/scan/` accepts JSON with `type` (`text`, `url`, or `file`) and `content`; file scans use `content_base64` and `subject` for the filename.
- `GET /api/v1/scans/` returns the latest 100 scan records and the total count.

## Prototype boundaries

The current file module performs static checks only (SHA-256, file size, the EICAR test signature, and executable/script extension). It is not a replacement for Microsoft Defender or commercial endpoint protection, does not detonate files in a sandbox, and should not be described as comprehensive malware detection. Message and URL results are heuristic/model indicators, not guarantees. The full specification's streaming MiniBatchKMeans, independent per-cluster ADWIN drift control, selective trust rollback, OCR/speech pipeline, authentication, and model-governance lifecycle still need production integration. The Android call monitor is a separate Android Studio app; the browser dashboard cannot monitor a phone by itself. The installed startup flow in this repository targets Windows only.
