$ErrorActionPreference = 'Stop'
$statePath = Join-Path $PSScriptRoot '.run/processes.json'
if (-not (Test-Path -LiteralPath $statePath)) { Write-Host 'No recorded servers.'; return }
$servers = Get-Content -LiteralPath $statePath -Raw | ConvertFrom-Json

function Stop-OwnedProcessTree([int]$ProcessIdToStop) {
    $children = Get-CimInstance Win32_Process -Filter "ParentProcessId = $ProcessIdToStop" -ErrorAction SilentlyContinue
    foreach ($child in $children) { Stop-OwnedProcessTree $child.ProcessId }
    Stop-Process -Id $ProcessIdToStop -Force -ErrorAction SilentlyContinue
}

foreach ($server in $servers) {
    $process = Get-Process -Id $server.processId -ErrorAction SilentlyContinue
    # Avoid terminating unrelated processes if Windows has reused an old PID.
    if ($process -and $process.StartTime.ToUniversalTime().Ticks -eq ([datetime]$server.startTime).ToUniversalTime().Ticks) {
        Stop-OwnedProcessTree $process.Id
    }
}
Remove-Item -LiteralPath $statePath
Write-Host 'Project servers stopped.'
