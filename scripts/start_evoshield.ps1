$ErrorActionPreference = "Stop"
$project = Split-Path -Parent $PSScriptRoot
Set-Location $project
$python = Join-Path $project '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $python -PathType Leaf)) {
    throw "EvoShield virtual environment was not found at $python. Run scripts\install_evoshield.ps1 first."
}
& $python manage.py migrate --run-syncdb
if ($LASTEXITCODE -ne 0) { throw 'EvoShield database setup failed. Check the error above.' }
& $python manage.py runserver 127.0.0.1:8000
