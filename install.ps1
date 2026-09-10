param(
  [string]$Ref = $(if ($env:KITT_REF) { $env:KITT_REF } else { 'main' }),
  [switch]$WithAiWorkers,
  [switch]$Force,
  [switch]$Uninstall
)
$ErrorActionPreference = 'Stop'
$Root = if ($env:KITT_HOME) { $env:KITT_HOME } else { Join-Path $env:LOCALAPPDATA 'KITT\ecosystem' }
$Bin = if ($env:KITT_BIN_DIR) { $env:KITT_BIN_DIR } else { Join-Path $env:LOCALAPPDATA 'KITT\bin' }

if ($Uninstall) {
  $Ctl = Join-Path $Root 'kitt-assistant\target\release\kittctl.exe'
  if (Test-Path $Ctl) { try { & $Ctl service stop | Out-Null } catch {} }
  Remove-Item $Root -Recurse -Force -ErrorAction SilentlyContinue
  foreach ($Name in @('kitt.cmd','kittctl.cmd','kittd.cmd','kitt-reverse-proxy.cmd','kitt-agent-gateway.cmd')) {
    Remove-Item (Join-Path $Bin $Name) -Force -ErrorAction SilentlyContinue
  }
  Write-Host 'K.I.T.T. ecosystem removed.'
  exit 0
}
foreach ($Tool in @('git','python','node','npm')) {
  if (-not (Get-Command $Tool -ErrorAction SilentlyContinue)) { throw "$Tool is required" }
}
& python -c "import sys; assert sys.version_info >= (3,12), 'Python 3.12+ required'"
& node -e "if(Number(process.versions.node.split('.')[0])<20)process.exit(1)"
if ($LASTEXITCODE -ne 0) { throw 'Node.js 20+ required' }
New-Item -ItemType Directory -Force -Path $Root,$Bin | Out-Null

function Sync-Repo([string]$Name) {
  $Dir = Join-Path $Root $Name
  if (Test-Path (Join-Path $Dir '.git')) {
    if (-not $Force) {
      $Dirty = & git -C $Dir status --porcelain
      if ($Dirty) { throw "$Name has local changes; commit/stash them or rerun with -Force" }
    } else { & git -C $Dir reset --hard HEAD | Out-Null }
  } else {
    Remove-Item $Dir -Recurse -Force -ErrorAction SilentlyContinue
    & git clone --filter=blob:none --no-checkout "https://github.com/rfdetoni/$Name.git" $Dir
    if ($LASTEXITCODE -ne 0) { throw "$Name clone failed" }
  }
  & git -C $Dir remote set-url origin "https://github.com/rfdetoni/$Name.git"
  & git -C $Dir fetch --force --depth 1 origin $Ref
  if ($LASTEXITCODE -ne 0) { throw "$Name fetch failed" }
  & git -C $Dir checkout --detach --force FETCH_HEAD
  if ($LASTEXITCODE -ne 0) { throw "$Name checkout failed" }
  & git -C $Dir clean -ffd
  Write-Host ("{0,-22} {1}" -f $Name, (& git -C $Dir rev-parse --short HEAD))
}

$Components = @(
  'kitt-protocol',
  'kitt-memory',
  'kitt-assistant',
  'kitt-toolbox',
  'kitt-agent-cli',
  'kitt-ai-workers',
  'kitt-reverse-proxy'
)
foreach ($Component in $Components) { Sync-Repo $Component }

$Cargo = Get-Command cargo -ErrorAction SilentlyContinue
if ($Cargo) {
  foreach ($Component in @('kitt-protocol','kitt-memory','kitt-toolbox','kitt-assistant')) {
    $Dir = Join-Path $Root $Component
    Push-Location $Dir
    try {
      if (Test-Path 'Cargo.lock') { & cargo build --release --locked } else { & cargo build --release }
      if ($LASTEXITCODE -ne 0) { throw "$Component build failed" }
    } finally { Pop-Location }
  }
} else { Write-Warning 'Rust/Cargo not found; native services and Agent native acceleration will be skipped.' }

$Hud = Join-Path $Root 'kitt-assistant\apps\kitt-hud'
if (Test-Path $Hud) {
  Push-Location $Hud
  try {
    & npm ci --no-audit --no-fund
    if ($LASTEXITCODE -ne 0) { throw 'HUD npm install failed' }
    & npm run build
    if ($LASTEXITCODE -ne 0) { throw 'HUD build failed' }
  } finally { Pop-Location }
}

$Venv = Join-Path $Root '.venv-agent'
$Vpy = Join-Path $Venv 'Scripts\python.exe'
if (-not (Test-Path $Vpy)) { & python -m venv $Venv }
& $Vpy -m pip install --disable-pip-version-check -U pip wheel | Out-Null

# Install the portable control plane first. Separately owned Python companions
# extend the same kitt namespace without vendoring code back into Agent.
& $Vpy -m pip install --disable-pip-version-check --upgrade --force-reinstall (Join-Path $Root 'kitt-agent-cli')
if ($LASTEXITCODE -ne 0) { throw 'Agent CLI install failed' }
$AssistantRuntime = Join-Path $Root 'kitt-assistant\packages\kitt-assistant-runtime'
$Evolution = Join-Path $Root 'kitt-ai-workers\packages\kitt-evolution'
$Evals = Join-Path $Root 'kitt-ai-workers\packages\kitt-evals'
& $Vpy -m pip install --disable-pip-version-check --no-deps --upgrade --force-reinstall $AssistantRuntime $Evolution $Evals
if ($LASTEXITCODE -ne 0) { throw 'Assistant runtime/Evolution/Evals install failed' }

$Native = $false
if ($Cargo) {
  try {
    & $Vpy -m pip install --disable-pip-version-check -U 'maturin>=1.8,<2' | Out-Null
    $Dist = Join-Path $Root '.cache\toolbox-native'
    Remove-Item $Dist -Recurse -Force -ErrorAction SilentlyContinue
    New-Item -ItemType Directory -Force -Path $Dist | Out-Null
    & $Vpy (Join-Path $Root 'kitt-toolbox\packaging\build_native_release.py') --out $Dist
    if ($LASTEXITCODE -ne 0) { throw 'native build failed' }
    $Wheel = Get-ChildItem $Dist -Filter '*.whl' | Select-Object -First 1
    if (-not $Wheel) { throw 'native wheel missing' }
    & $Vpy -m pip install --disable-pip-version-check --no-deps --force-reinstall $Wheel.FullName
    if ($LASTEXITCODE -ne 0) { throw 'native install failed' }
    $Native = $true
  } catch { Write-Warning "Native acceleration unavailable; using Python fallback. $_" }
}

if ($WithAiWorkers) {
  & $Vpy -m pip install --disable-pip-version-check -e "$(Join-Path $Root 'kitt-ai-workers')[stt]"
  if ($LASTEXITCODE -ne 0) { throw 'AI/STT worker install failed' }
}

$Proxy = Join-Path $Root 'kitt-reverse-proxy'
Push-Location $Proxy
try {
  & npm ci --no-audit --no-fund
  if ($LASTEXITCODE -ne 0) { throw 'Reverse proxy npm install failed' }
  & npm run build
  if ($LASTEXITCODE -ne 0) { throw 'Reverse proxy build failed' }
  $Chrome = @("$env:ProgramFiles\Google\Chrome\Application\chrome.exe", "${env:ProgramFiles(x86)}\Google\Chrome\Application\chrome.exe", "$env:LOCALAPPDATA\Google\Chrome\Application\chrome.exe") | Where-Object { $_ -and (Test-Path $_) } | Select-Object -First 1
  if (-not $Chrome) {
    $Playwright = Join-Path $Proxy 'node_modules\.bin\playwright.cmd'
    if (-not (Test-Path $Playwright)) { throw 'Locked Playwright binary is missing after npm ci' }
    & $Playwright install chromium
    if ($LASTEXITCODE -ne 0) { throw 'Playwright Chromium install failed' }
  }
  & npm prune --omit=dev --no-audit --no-fund
  if ($LASTEXITCODE -ne 0) { throw 'Reverse proxy prune failed' }
} finally { Pop-Location }

$KittExe = Join-Path $Venv 'Scripts\kitt.exe'
Set-Content (Join-Path $Bin 'kitt.cmd') -Encoding Ascii -Value "@echo off`r`n`"$KittExe`" %*"
Set-Content (Join-Path $Bin 'kitt-reverse-proxy.cmd') -Encoding Ascii -Value "@echo off`r`nnode `"$Proxy\dist\cli.js`" %*"
Set-Content (Join-Path $Bin 'kitt-agent-gateway.cmd') -Encoding Ascii -Value "@echo off`r`nnode `"$Proxy\dist\gateway\cli.js`" %*"
$Ctl = Join-Path $Root 'kitt-assistant\target\release\kittctl.exe'
if (Test-Path $Ctl) {
  Set-Content (Join-Path $Bin 'kittctl.cmd') -Encoding Ascii -Value "@echo off`r`n`"$Ctl`" %*"
  try { & $Ctl service install; & $Ctl service start } catch { Write-Warning $_ }
}
$UserPath = [Environment]::GetEnvironmentVariable('Path','User')
$Parts = @($UserPath -split ';' | Where-Object { $_ })
if ($Parts -notcontains $Bin) { [Environment]::SetEnvironmentVariable('Path', (($Parts + $Bin) -join ';'), 'User'); $env:Path = "$Bin;$env:Path" }
& $KittExe --help | Out-Null
& $Vpy -c "import kitt.daemon.client, kitt.remote.server, kitt.evolution, kitt.evals.corpus; print('split KITT namespace: ok')" | Out-Null
if ($LASTEXITCODE -ne 0) { throw 'Split module smoke test failed' }
$Backend = & $Vpy -c "from kitt.native.bridge import NativeCodeEngine; print(NativeCodeEngine(r'$(Join-Path $Root 'kitt-agent-cli')').status.backend)"
Write-Host "K.I.T.T. ecosystem installed/updated at $Root (Agent backend: $Backend; native wheel: $Native)."
Write-Host 'Open a new terminal and run: kitt'
