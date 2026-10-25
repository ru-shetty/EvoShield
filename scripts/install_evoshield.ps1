param(
    [string[]]$WatchFolder = @((Join-Path $env:USERPROFILE 'Downloads'), (Join-Path $env:USERPROFILE 'Desktop')),
    [int]$IntervalSeconds = 10
)
$ErrorActionPreference = 'Stop'
$currentIdentity = [System.Security.Principal.WindowsIdentity]::GetCurrent()
$currentPrincipal = [System.Security.Principal.WindowsPrincipal]::new($currentIdentity)
if (-not $currentPrincipal.IsInRole([System.Security.Principal.WindowsBuiltInRole]::Administrator)) {
    throw 'Run this installer from an elevated PowerShell window (Run as administrator). The background Defender scan needs the elevated task.'
}
$Project = Split-Path -Parent $PSScriptRoot
$Python = Join-Path $Project '.venv\Scripts\python.exe'
$AppData = Join-Path $env:LOCALAPPDATA 'EvoShield'
$TaskName = 'EvoShield Protection'
$WatchFolderWasSpecified = $PSBoundParameters.ContainsKey('WatchFolder')

if (-not $WatchFolderWasSpecified) {
    $WatchFolder = @($WatchFolder | Where-Object { Test-Path -LiteralPath $_ -PathType Container })
    if ($env:OneDrive) {
        $OneDriveDesktop = Join-Path $env:OneDrive 'Desktop'
        if ((Test-Path -LiteralPath $OneDriveDesktop -PathType Container) -and ($WatchFolder -notcontains $OneDriveDesktop)) {
            $WatchFolder += $OneDriveDesktop
        }
    }
    if ($WatchFolder.Count -eq 0) {
        throw 'None of the default watch folders exist. Re-run with -WatchFolder followed by an existing folder path.'
    }
}

foreach ($folder in $WatchFolder) {
    if (-not (Test-Path -LiteralPath $folder -PathType Container)) {
        throw "Watch folder does not exist: $folder"
    }
}

if (-not (Test-Path -LiteralPath $Python)) {
    python -m venv (Join-Path $Project '.venv')
}
& $Python -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) { throw 'Could not prepare Python packages.' }
& $Python -m pip install -r (Join-Path $Project 'requirements.txt')
if ($LASTEXITCODE -ne 0) { throw 'Could not install EvoShield dependencies.' }
& (Join-Path $PSScriptRoot 'install_image_ocr.ps1')
& $Python (Join-Path $Project 'manage.py') migrate --run-syncdb
if ($LASTEXITCODE -ne 0) { throw 'Could not initialize the local scan database.' }

New-Item -ItemType Directory -Path $AppData -Force | Out-Null
$config = @{ watch_folders = @($WatchFolder | ForEach-Object { (Resolve-Path -LiteralPath $_).Path }); interval_seconds = [Math]::Max(5, $IntervalSeconds) }
$config | ConvertTo-Json -Depth 3 | Set-Content -LiteralPath (Join-Path $AppData 'settings.json') -Encoding UTF8
$action = New-ScheduledTaskAction -Execute $Python -Argument ('"' + (Join-Path $Project 'scripts\evoshield_service.py') + '" --watch ' + (($config.watch_folders | ForEach-Object { '"' + $_ + '"' }) -join ' --watch ') + ' --interval ' + $config.interval_seconds) -WorkingDirectory $Project
$trigger = New-ScheduledTaskTrigger -AtLogOn -User ([System.Security.Principal.WindowsIdentity]::GetCurrent().Name)
$taskPrincipal = New-ScheduledTaskPrincipal -UserId ([System.Security.Principal.WindowsIdentity]::GetCurrent().Name) -LogonType Interactive -RunLevel Highest
$settings = New-ScheduledTaskSettingsSet -ExecutionTimeLimit ([TimeSpan]::Zero) -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1)
if (Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue) {
    Stop-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
}
Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Principal $taskPrincipal -Settings $settings -Description 'Runs EvoShield for this Windows user and monitors selected folders.' -Force | Out-Null
Start-ScheduledTask -TaskName $TaskName
Write-Host "EvoShield installed for this Windows account. Dashboard: http://127.0.0.1:8000"
Write-Host "Watching: $($config.watch_folders -join ', ')"
Write-Host 'Manage it in Task Scheduler or run scripts\uninstall_evoshield.ps1 to remove automatic startup.'
