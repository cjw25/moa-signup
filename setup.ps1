param([string]$PythonPath)
$ErrorActionPreference = 'Stop'
$projectRoot = $PSScriptRoot

function Invoke-Checked {
    param([string]$Executable, [string[]]$Arguments)
    & $Executable @Arguments
    if ($LASTEXITCODE -ne 0) { throw "Command failed: $Executable" }
}

if (-not $PythonPath) {
    $pythonCommand = Get-Command python -ErrorAction SilentlyContinue
    $pyCommand = Get-Command py -ErrorAction SilentlyContinue
    $bundledPython = Join-Path $env:USERPROFILE '.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
    if ($pythonCommand -and $pythonCommand.Source -notlike '*WindowsApps*') {
        $PythonPath = $pythonCommand.Source
    } elseif ($pyCommand) {
        $PythonPath = (& $pyCommand.Source -3 -c 'import sys; print(sys.executable)').Trim()
    } elseif (Test-Path -LiteralPath $bundledPython) {
        $PythonPath = $bundledPython
    } else {
        throw 'Install Python 3.12+ or pass -PythonPath with the full executable path.'
    }
}
if (-not (Get-Command npm.cmd -ErrorAction SilentlyContinue)) { throw 'Install Node.js 20.9+ first.' }
$venvDirectory = Join-Path $projectRoot 'backend/.venv'
$venvPython = Join-Path $venvDirectory 'Scripts/python.exe'
if (-not (Test-Path -LiteralPath $venvPython)) {
    Invoke-Checked $PythonPath @('-m', 'venv', $venvDirectory)
}
Invoke-Checked $venvPython @('-m', 'pip', 'install', '-r', (Join-Path $projectRoot 'backend/requirements-lock.txt'))
Invoke-Checked $venvPython @((Join-Path $projectRoot 'backend/scripts/setup_env.py'))
Push-Location (Join-Path $projectRoot 'frontend')
try { Invoke-Checked 'npm.cmd' @('ci', '--no-fund', '--no-audit') } finally { Pop-Location }
Write-Host 'Setup complete. Run .\start.ps1'
