$ErrorActionPreference = 'Stop'
$ForwardArgs = @($args)
$InstallerRepo = if ($env:KITT_INSTALLER_REPO) { $env:KITT_INSTALLER_REPO } else { 'https://github.com/rfdetoni/kitt.git' }
$InstallerRef = if ($env:KITT_INSTALLER_REF) { $env:KITT_INSTALLER_REF } else { 'main' }

function Find-KittPython {
  $Candidates = @()
  $Py = Get-Command py -ErrorAction SilentlyContinue
  if ($Py) {
    foreach ($Minor in 14, 13, 12, 11, 10) {
      $Candidates += ,@($Py.Source, "-3.$Minor")
    }
  }
  foreach ($Name in 'python3.14', 'python3.13', 'python3.12', 'python3', 'python') {
    $Command = Get-Command $Name -ErrorAction SilentlyContinue
    if ($Command) { $Candidates += ,@($Command.Source) }
  }

  foreach ($Candidate in $Candidates) {
    $Exe = $Candidate[0]
    $Prefix = @($Candidate | Select-Object -Skip 1)
    try {
      $VersionText = & $Exe @Prefix -c "import sys; print('.'.join(map(str, sys.version_info[:3])))" 2>$null
      if ($LASTEXITCODE -eq 0 -and ([version]$VersionText) -ge [version]'3.10') {
        return [pscustomobject]@{ Exe = $Exe; Prefix = $Prefix }
      }
    } catch { }
  }
  return $null
}

$Python = Find-KittPython
if (-not $Python) {
  throw 'K.I.T.T. requires Python 3.10+ for the installer (Agent requires Python 3.12+).'
}

$LocalRoot = $null
if ($PSScriptRoot -and (Test-Path (Join-Path $PSScriptRoot 'installer\__main__.py')) -and (Test-Path (Join-Path $PSScriptRoot 'ecosystem.json'))) {
  $LocalRoot = $PSScriptRoot
}

$TempRoot = $null
try {
  if (-not $LocalRoot) {
    if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
      throw 'K.I.T.T. requires git.'
    }
    $TempRoot = Join-Path ([IO.Path]::GetTempPath()) ("kitt-installer-" + [guid]::NewGuid().ToString('N'))
    $LocalRoot = Join-Path $TempRoot 'kitt'
    New-Item -ItemType Directory -Force -Path $TempRoot | Out-Null
    & git clone --filter=blob:none --no-checkout $InstallerRepo $LocalRoot *> $null
    if ($LASTEXITCODE -ne 0) { throw 'Failed to download the K.I.T.T. installer.' }
    & git -C $LocalRoot fetch --force --depth 1 origin $InstallerRef *> $null
    if ($LASTEXITCODE -ne 0) { throw "Failed to resolve K.I.T.T. installer ref: $InstallerRef" }
    & git -C $LocalRoot checkout --detach --force FETCH_HEAD *> $null
    if ($LASTEXITCODE -ne 0) { throw 'Failed to prepare the K.I.T.T. installer.' }
  }

  Push-Location $LocalRoot
  try {
    $Prefix = @($Python.Prefix)
    & $Python.Exe @Prefix -m installer @ForwardArgs
    if ($LASTEXITCODE -ne 0) { throw "K.I.T.T. installer failed with exit code $LASTEXITCODE." }
  } finally {
    Pop-Location
  }
} finally {
  if ($TempRoot -and (Test-Path $TempRoot)) {
    Remove-Item -LiteralPath $TempRoot -Recurse -Force -ErrorAction SilentlyContinue
  }
}
