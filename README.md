# EvoShield

EvoShield is a local security monitoring prototype based on the 16-module specification. It provides a browser dashboard, a Django API, persistent scan history, message and digital-arrest analysis, URL analysis, static file checks, and an opt-in Windows folder watcher.

The dashboard uses a dark security-console layout with a sidebar, search field, welcome panel, real scan totals, file-scan area, recent results, and risk/trend summaries. Its sidebar opens message, website-link, file, image, call, Today, and History views. Image checks use Tesseract OCR to read visible text and assess phishing/scam wording. Call monitoring is a separate Windows session; only suspicious submitted speech appears in desktop history. The Android app uses a matching compact layout with on-device notification and call history.

## Run on Windows

1. Install Python 3.10 or newer.
2. From the project folder, create and activate a virtual environment, then install dependencies:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   .\scripts\install_image_ocr.ps1
   ```

3. Start the local dashboard. This creates the SQLite tables on first run:

   ```powershell
   .\scripts\start_evoshield.ps1
   ```

4. Open [http://127.0.0.1:8000](http://127.0.0.1:8000).

The server binds to loopback only and scan history is stored in `database/evoshield.sqlite3`.

On Windows, scans rated **High risk**, **Suspicious**, or **Needs review** generate a desktop toast notification for dashboard, browser-extension, and watched-file checks. Keep Windows notifications enabled for EvoShield/Python. Call-monitor alerts already show their own toast. The notification contains a short reason and next step; full details remain in dashboard history.

## Install continuous Windows monitoring

From an **elevated PowerShell window** (Run as administrator) in the project folder, install the dependencies and register EvoShield to start for your Windows account at sign-in. The elevation is required for targeted Microsoft Defender scans:

```powershell
.\scripts\install_evoshield.ps1
```

By default, EvoShield monitors whichever of Downloads and Desktop exist (or OneDrive Desktop if the regular Desktop is redirected) every 10 seconds. Select folders and a polling interval with:

```powershell
.\scripts\install_evoshield.ps1 -WatchFolder "$env:USERPROFILE\Downloads", "$env:USERPROFILE\Documents" -IntervalSeconds 15
```

New files are first copied to `%LOCALAPPDATA%\EvoShield\quarantine\processing` and removed from the watched folder after the copy is verified. EvoShield scans files up to 20 MiB; Microsoft Defender must also be active with recent signatures, the quarantine path must not be excluded, and a targeted scan must complete. Only a `LOW` EvoShield result plus no Defender detection is released back to the original folder. A collision is released with an alternate filename rather than overwriting another file. Suspicious, unsupported, oversized, or incompletely scanned files stay under `%LOCALAPPDATA%\EvoShield\quarantine\held`; each has a `manifest.json` with its original path and reason. Held files are not automatically restored.

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

The agent snapshots files already present at startup and leaves them alone. For a new or changed file, it waits for the size and timestamp to remain stable across two polling rounds, moves it into the quarantine folder, and runs both scans before any release. It never opens or executes a file. The quarantine folder must be outside every watched folder. Remove folders from the command to stop monitoring them.

This is folder monitoring, not an OS-level file-system filter: a file may be visible in its watched folder until the next polling pass stages it. It covers only the folders you configured; it does not intercept every path, protect files before another app opens them, or automatically monitor Android storage. Suspicious/held files remain isolated for review. No scanner can guarantee that an undetected file is safe.

## Automatic browser link checks (Chrome or Edge)

1. Start EvoShield with `scripts\start_evoshield.ps1` and confirm `http://127.0.0.1:8000` opens.
2. In Chrome, open `chrome://extensions`; in Edge, open `edge://extensions`.
3. Turn on **Developer mode**, select **Load unpacked**, and choose the repository's `browser-extension` folder.
4. Visit a normal HTTP or HTTPS page. Automatic checks are enabled by default; the extension also checks HTTP/HTTPS tabs that are already open when installed or enabled. Click the EvoShield toolbar icon to see its latest result or pause/resume checks. Suspicious addresses show a warning badge; all results appear in dashboard **History** with source **browser-extension**.

The extension checks main-frame page navigations. It removes query strings and fragments before submitting a URL because they can contain session tokens or personal data. The URL path and hostname are still sent to the loopback-only EvoShield service. Keep the local service running; if it is stopped, those page checks cannot be recorded. This checks the website address, not page text, scripts, downloads, or WhatsApp Web messages, and it does not block navigation.

## Live-call digital-arrest monitoring

Call monitoring is a separate, opt-in session. It does not start automatically at sign-in.

### Windows: WhatsApp Desktop, Zoom, and Google Meet

Install the optional audio and local speech-recognition components once:

```powershell
.\scripts\install_live_call_monitor.ps1
```

Start the dashboard with `scripts\start_evoshield.ps1`, open **Calls**, select **Voice call**, **Video call**, or **Both voice and video calls**, then allow monitoring before the call. Both mode applies standard call-scam checks and video-call coercion cues while monitoring audio. Stop monitoring from the same button when the call ends.

Scam speech detection analyzes audio for either selected call type; it does not inspect video frames or automatically infer whether the call is voice or video. Windows captures audio from the default playback device, regardless of which listed app is open, including other sounds played there while monitoring is active. Faster Whisper runs locally and downloads its speech model on first start. Raw audio is held in memory only. Suspicious transcript text and the selected call type are sent to the local API for the call-history alert, and a Windows notification is shown.

### Android: WhatsApp calls

Open the `android` folder in Android Studio and follow [android/README.md](android/README.md). The user selects voice or video call, starts monitoring for each session, and grants microphone permission when Android asks. Recognition is on-device and no audio or transcript is sent to the server. Android restricts access to other apps' voice-call audio, so EvoShield listens through the phone microphone; WhatsApp may hold the microphone and speakerphone may be required. The Android screen shows locally saved call-alert summaries only; it does not ingest files, browser URLs, SMS, or notifications. This is best-effort and will not work reliably with every phone or headset.

Both call monitors use the digital-arrest rule detector, which includes common English and Hindi phrases. Selecting **Video call** also enables speech cues involving camera coercion, identity-document display, and screen sharing. The selected call type is an explicit user choice, not automatic camera or app detection. Recognition quality depends on the speech model and language. They provide warning indicators, not guaranteed scam detection, and do not record, block, or end calls. Stop monitoring when the call ends.

## API

- `POST /api/v1/scan/` accepts JSON with `type` (`text`, `url`, or `file`) and `content`; file scans use `content_base64` and `subject` for the filename.
- `GET /api/v1/scans/?limit=25&offset=0` returns a page of scan records, total count, and aggregate counts. `limit` is capped at 100.

URL scans use the trained TF-IDF classifier when its model artifact is installed. On a fresh checkout without that artifact, they use a transparent indicator-based fallback; the result reports `analysis_mode` in its URL feature details. The fallback is a heuristic score, not a calibrated probability.

## Prototype boundaries

The current file module performs static checks only (SHA-256, file size, the EICAR test signature, and executable/script extension). It is not a replacement for Microsoft Defender or commercial endpoint protection, does not detonate files in a sandbox, and should not be described as comprehensive malware detection. Image OCR checks visible text only and can miss stylized, obscured, or text-free threats. Message and URL results are heuristic/model indicators, not guarantees. The full specification's streaming MiniBatchKMeans, independent per-cluster ADWIN drift control, selective trust rollback, authentication, and model-governance lifecycle still need production integration. The Android call monitor is a separate Android Studio app; the browser dashboard cannot monitor a phone by itself. The installed startup flow in this repository targets Windows only.
