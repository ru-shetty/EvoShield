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

## Optional continuous folder monitoring

Keep the dashboard server running, open a second PowerShell window in the project folder, and start the agent with folders you want monitored:

```powershell
python scripts/evoshield_agent.py --watch "$env:USERPROFILE\Downloads" --watch "$env:USERPROFILE\Desktop"
```

The agent checks selected folders every 30 seconds for newly added or changed executable and script files. It reports static results to the local dashboard. To start it automatically at sign-in, create a Windows Task Scheduler task that runs the command above after the EvoShield server is available. Remove folders from the command to stop monitoring them. The watcher does not monitor browser traffic, memory, system processes, or the whole device.

## API

- `POST /api/v1/scan/` accepts JSON with `type` (`text`, `url`, or `file`) and `content`; file scans use `content_base64` and `subject` for the filename.
- `GET /api/v1/scans/` returns the latest 100 scan records and the total count.

## Prototype boundaries

The current file module performs static checks only (SHA-256, file size, the EICAR test signature, and executable/script extension). It is not a replacement for Microsoft Defender or commercial endpoint protection, does not detonate files in a sandbox, and should not be described as comprehensive malware detection. Message and URL results are heuristic/model indicators, not guarantees. The full specification's streaming MiniBatchKMeans, independent per-cluster ADWIN drift control, selective trust rollback, OCR/speech pipeline, authentication, and model-governance lifecycle still need production integration. Android background scanning requires a native Android app and Android-specific permissions; this repository's dashboard cannot scan the phone while running as a web page.
