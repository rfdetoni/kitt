# ==============================================================================
# K.I.T.T. Ecosystem Installer for Windows (PowerShell)
# ==============================================================================
$ErrorActionPreference = "Stop"

function Write-Header {
    Write-Host ""
    Write-Host "  _  __ _____ _______ _______ " -ForegroundColor Green
    Write-Host " | |/ /|_   _|__   __|__   __|" -ForegroundColor Green
    Write-Host " | ' /   | |    | |     | |   " -ForegroundColor Green
    Write-Host " |  <    | |    | |     | |   " -ForegroundColor Green
    Write-Host " | . \  _| |_   | |     | |   " -ForegroundColor Green
    Write-Host " |_|\_\|_____|  |_|     |_|   " -ForegroundColor Green
    Write-Host "  Ecosystem Installer (Windows) " -ForegroundColor Green
    Write-Host ""
}

Write-Header

# 1. Determine Ecosystem Root
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
if (Test-Path "$ScriptDir\..\..\kitt-assistant") {
    $RootDir = Resolve-Path "$ScriptDir\..\.."
} elseif (Test-Path "$ScriptDir\..\kitt-assistant") {
    $RootDir = Resolve-Path "$ScriptDir\.."
} elseif (Test-Path ".\kitt-assistant") {
    $RootDir = (Get-Location).Path
} else {
    $RootDir = Resolve-Path "$ScriptDir\.."
}

Write-Host "[INFO] KITT workspace root detected at: $RootDir" -ForegroundColor Cyan

# 2. Check System Prerequisites
Write-Host "[INFO] Verifying prerequisites..." -ForegroundColor Cyan

function Check-Command($cmd) {
    if (-not (Get-Command $cmd -ErrorAction SilentlyContinue)) {
        Write-Error "Missing required command: $cmd. Please install it before proceeding."
    }
}

Check-Command "git"
Check-Command "cargo"
Check-Command "rustc"
Check-Command "python"
Check-Command "node"
Check-Command "npm"

Write-Host "[OK] All required commands are present." -ForegroundColor Green

# 3. Create Configuration Directories
$ConfigRoot = Join-Path $env:APPDATA "kitt"
$ControlCenterDir = Join-Path $ConfigRoot "control-center"
$AssistantDir = Join-Path $ConfigRoot "assistant"

New-Item -ItemType Directory -Force -Path $ControlCenterDir | Out-Null
New-Item -ItemType Directory -Force -Path $AssistantDir | Out-Null
Write-Host "[OK] Configuration directory initialized at: $ConfigRoot" -ForegroundColor Green

# 4. Helper to ensure repo exists
function Ensure-Repo($name) {
    $dir = Join-Path $RootDir $name
    if (-not (Test-Path $dir)) {
        Write-Host "[INFO] Cloning $name from GitHub..." -ForegroundColor Cyan
        git clone "https://github.com/rfdetoni/$name.git" $dir
    }
}

# 5. Build kitt-protocol
$ProtocolDir = Join-Path $RootDir "kitt-protocol"
if (Test-Path $ProtocolDir) {
    Write-Host "[INFO] Building kitt-protocol..." -ForegroundColor Cyan
    Push-Location $ProtocolDir
    try { cargo build --release } finally { Pop-Location }
    Write-Host "[OK] kitt-protocol ready." -ForegroundColor Green
}

# 6. Build kitt-memory
$MemoryDir = Join-Path $RootDir "kitt-memory"
if (Test-Path $MemoryDir) {
    Write-Host "[INFO] Building kitt-memory..." -ForegroundColor Cyan
    Push-Location $MemoryDir
    try { cargo build --release } finally { Pop-Location }
    Write-Host "[OK] kitt-memory ready." -ForegroundColor Green
}

# 7. Build kitt-assistant
Ensure-Repo "kitt-assistant"
$AssistantRepo = Join-Path $RootDir "kitt-assistant"
Write-Host "[INFO] Building kitt-assistant (kittd + kittctl)..." -ForegroundColor Cyan
Push-Location $AssistantRepo
try {
    cargo build --release --workspace
    $HudDir = Join-Path $AssistantRepo "apps\kitt-hud"
    if (Test-Path $HudDir) {
        Write-Host "[INFO] Building ephemeral HUD frontend..." -ForegroundColor Cyan
        Push-Location $HudDir
        try {
            npm install --silent
            npm run build --silent
        } finally {
            Pop-Location
        }
    }
} finally {
    Pop-Location
}
Write-Host "[OK] kitt-assistant and KITT Control Center built successfully." -ForegroundColor Green

# 8. Setup kitt-agent-cli
Ensure-Repo "kitt-agent-cli"
$AgentDir = Join-Path $RootDir "kitt-agent-cli"
Write-Host "[INFO] Setting up kitt-agent-cli (Python virtualenv)..." -ForegroundColor Cyan
Push-Location $AgentDir
try {
    $VenvDir = Join-Path $AgentDir ".venv"
    if (-not (Test-Path $VenvDir)) {
        python -m venv .venv
    }
    $PipExe = Join-Path $VenvDir "Scripts\pip.exe"
    & $PipExe install --upgrade pip --quiet
    & $PipExe install -e . --quiet
} finally {
    Pop-Location
}
Write-Host "[OK] kitt-agent-cli ready in $AgentDir\.venv." -ForegroundColor Green

# 9. Setup kitt-reverse-proxy
$ProxyDir = Join-Path $RootDir "kitt-reverse-proxy"
if (Test-Path $ProxyDir) {
    Write-Host "[INFO] Building kitt-reverse-proxy..." -ForegroundColor Cyan
    Push-Location $ProxyDir
    try {
        npm install --silent
        npm run build --silent
    } finally {
        Pop-Location
    }
    Write-Host "[OK] kitt-reverse-proxy ready." -ForegroundColor Green
}

# 10. Build kitt-toolbox
$ToolboxDir = Join-Path $RootDir "kitt-toolbox"
if (Test-Path $ToolboxDir) {
    Write-Host "[INFO] Building kitt-toolbox..." -ForegroundColor Cyan
    Push-Location $ToolboxDir
    try { cargo build --release } finally { Pop-Location }
    Write-Host "[OK] kitt-toolbox ready." -ForegroundColor Green
}

# 11. Install and Start Background Service Natively
Write-Host "[INFO] Installing and starting K.I.T.T. native background service..." -ForegroundColor Cyan
$KittctlExe = Join-Path $AssistantRepo "target\release\kittctl.exe"
& $KittctlExe service install
& $KittctlExe service start
Write-Host "[OK] K.I.T.T. background service is active." -ForegroundColor Green

Write-Host ""
Write-Host "================================================================" -ForegroundColor Green
Write-Host "        K.I.T.T. Ecosystem Installed & Running!                 " -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Green
Write-Host ""
Write-Host "The K.I.T.T. daemon is now running natively in the background." -ForegroundColor Green
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host ""
Write-Host " 1. Open KITT Control Center Web GUI:"
Write-Host "    http://127.0.0.1:41828/" -ForegroundColor Cyan
Write-Host ""
Write-Host " 2. Manage Background Service:"
Write-Host "    $KittctlExe service status"
Write-Host "    $KittctlExe service restart"
Write-Host "    $KittctlExe service stop"
Write-Host ""
Write-Host " 3. Run Agent CLI:"
Write-Host "    $RootDir\kitt-agent-cli\.venv\Scripts\Activate.ps1"
Write-Host "    kitt"
Write-Host ""
Write-Host " 4. Query Assistant directly via CLI:"
Write-Host "    $KittctlExe ask 'Ola KITT'"
Write-Host ""
