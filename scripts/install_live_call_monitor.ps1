$ErrorActionPreference = 'Stop'
$Project = Split-Path -Parent $PSScriptRoot
$Python = Join-Path $Project '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $Python)) {
    throw 'Install EvoShield first with scripts\install_evoshield.ps1.'
}
& $Python -m pip install -r (Join-Path $Project 'requirements-live-calls.txt')
if ($LASTEXITCODE -ne 0) { throw 'Could not install live-call monitor dependencies.' }
Write-Host 'Windows call monitoring is ready. Start it from the EvoShield dashboard Calls page and select Voice or Video call.'
Write-Host 'Scam speech detection analyzes audio for either call type; it does not inspect video frames.'
Write-Host 'The first start downloads the speech model. Raw audio is not saved.'
