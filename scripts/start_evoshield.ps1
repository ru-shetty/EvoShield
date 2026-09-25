$ErrorActionPreference = "Stop"
$project = Split-Path -Parent $PSScriptRoot
Set-Location $project
python manage.py migrate --run-syncdb
python manage.py runserver 127.0.0.1:8000
