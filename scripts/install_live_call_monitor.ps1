$ErrorActionPreference = 'Stop'
$Project = Split-Path -Parent $PSScriptRoot
$Python = Join-Path $Project '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $Python)) {
    throw 'Install EvoShield first with scripts\install_evoshield.ps1.'
}
& $Python -m pip install -r (Join-Path $Project 'requirements-live-calls.txt')
if ($LASTEXITCODE -ne 0) { throw 'Could not install live-call monitor dependencies.' }
Write-Host 'Windows live-call monitoring is ready. Start it manually when you join a call:'
Write-Host '.\.venv\Scripts\python.exe .\scripts\evoshield_call_monitor.py'
Write-Host 'The first run downloads the selected speech model. Raw audio is not saved.'
