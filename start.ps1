param([string]$PythonPath, [switch]$NoBrowser)
$ErrorActionPreference = 'Stop'
$projectRoot = $PSScriptRoot
$runDirectory = Join-Path $projectRoot '.run'
$statePath = Join-Path $runDirectory 'processes.json'
if (-not $PythonPath) { $PythonPath = Join-Path $projectRoot 'backend/.venv/Scripts/python.exe' }
if (-not (Test-Path -LiteralPath $PythonPath)) { throw 'Run .\setup.ps1 first, or specify -PythonPath.' }
if (-not (Test-Path -LiteralPath (Join-Path $projectRoot 'backend/.env'))) { throw 'Run .\setup.ps1 first to generate keys.' }
$nodeCommand = Get-Command node -ErrorAction Stop
$nextCli = Join-Path $projectRoot 'frontend/node_modules/next/dist/bin/next'
if (-not (Test-Path -LiteralPath $nextCli)) { throw 'Run .\setup.ps1 first to install Next.js.' }

foreach ($port in @(3000, 8000)) {
    $listener = [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Loopback, $port)
    try { $listener.Start() } catch { throw "Port $port is in use. Stop the existing server before starting." }
    finally { $listener.Stop() }
}

New-Item -ItemType Directory -Force -Path $runDirectory | Out-Null
$startedProcesses = @()
try {
    $backend = Start-Process -FilePath $PythonPath -ArgumentList @('-m', 'uvicorn', 'app.main:create_app', '--factory', '--host', '127.0.0.1', '--port', '8000') -WorkingDirectory (Join-Path $projectRoot 'backend') -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $runDirectory 'backend.log') -RedirectStandardError (Join-Path $runDirectory 'backend-error.log')
    $startedProcesses += $backend
    @($startedProcesses | ForEach-Object { @{ processId = $_.Id; startTime = $_.StartTime.ToUniversalTime().ToString('o') } }) | ConvertTo-Json | Set-Content -LiteralPath $statePath -Encoding UTF8
    $frontend = Start-Process -FilePath $nodeCommand.Source -ArgumentList @(('"{0}"' -f $nextCli), 'dev', '--hostname', '127.0.0.1', '--port', '3000') -WorkingDirectory (Join-Path $projectRoot 'frontend') -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $runDirectory 'frontend.log') -RedirectStandardError (Join-Path $runDirectory 'frontend-error.log')
    $startedProcesses += $frontend
    @($startedProcesses | ForEach-Object { @{ processId = $_.Id; startTime = $_.StartTime.ToUniversalTime().ToString('o') } }) | ConvertTo-Json | Set-Content -LiteralPath $statePath -Encoding UTF8
    $ready = $false
    for ($attempt = 0; $attempt -lt 30; $attempt++) {
        foreach ($server in $startedProcesses) { if ($server.HasExited) { throw 'A server exited. Check .run/ logs.' } }
        try {
            $health = Invoke-WebRequest 'http://127.0.0.1:8000/api/health' -UseBasicParsing -TimeoutSec 2
            $page = Invoke-WebRequest 'http://127.0.0.1:3000' -UseBasicParsing -TimeoutSec 2
            if ($health.StatusCode -eq 200 -and $page.StatusCode -eq 200) { $ready = $true; break }
        } catch { Start-Sleep -Milliseconds 500 }
    }
    if (-not $ready) { throw 'Servers did not become ready. Check .run/ logs.' }
    Write-Host 'Ready: http://127.0.0.1:3000 (stop with .\stop.ps1)'
    if (-not $NoBrowser) { Start-Process 'http://127.0.0.1:3000' }
} catch {
    & (Join-Path $projectRoot 'stop.ps1')
    throw
}
