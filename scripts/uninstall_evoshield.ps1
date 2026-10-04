$ErrorActionPreference = 'Stop'
$TaskName = 'EvoShield Protection'
$task = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($task) {
    Stop-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
    Write-Host 'EvoShield automatic startup has been removed.'
} else {
    Write-Host 'EvoShield automatic startup was not installed.'
}
Write-Host 'Existing scan history and settings are kept under LocalAppData and the project database.'
