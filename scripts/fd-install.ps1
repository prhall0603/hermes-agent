# The Fiber Dad desktop — one-command installer for Windows.
#
#   irm https://github.com/prhall0603/hermes-agent/releases/latest/download/fd-install.ps1 | iex
#   (or: powershell -ExecutionPolicy Bypass -File fd-install.ps1)
#
# Default: runs the NSIS installer silently (no Developer Mode needed).
# -MSIX    installs the signed-store-style package instead (requires
#          Developer Mode on an unsigned build).
# -Uninstall removes the app.
param(
  [switch]$MSIX,
  [switch]$Uninstall
)

$ErrorActionPreference = 'Stop'
$Repo = 'prhall0603/hermes-agent'

function Write-Step($msg) { Write-Host "`e[1;36m==>`e[0m $msg" }

if ($Uninstall) {
  Write-Step 'Uninstalling The Fiber Dad…'
  # NSIS installs register an uninstaller in the registry.
  $uk = Get-ItemProperty 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*' -ErrorAction SilentlyContinue |
        Where-Object { $_.DisplayName -like '*The Fiber Dad*' }
  if ($uk) {
    Start-Process -FilePath $uk.UninstallString -Wait
  } else {
    Get-AppxPackage '*TheFiberDad*' | Remove-AppxPackage
  }
  Write-Host 'Removed.'
  exit 0
}

$base = "https://github.com/$Repo/releases/latest/download"
$tmp = Join-Path $env:TEMP ("thefiberdad-" + [guid]::NewGuid().ToString('N').Substring(0,8))
New-Item -ItemType Directory -Path $tmp -Force | Out-Null

if ($MSIX) {
  Write-Step 'Downloading TheFiberDad-win-x64.msix'
  $file = Join-Path $tmp 'TheFiberDad.msix'
  Invoke-WebRequest "$base/TheFiberDad-win-x64.msix" -OutFile $file
  Write-Step 'Installing MSIX (needs Developer Mode on an unsigned build)'
  Add-AppxPackage -Path $file
} else {
  Write-Step 'Downloading TheFiberDad-win-x64.exe'
  $file = Join-Path $tmp 'TheFiberDad-setup.exe'
  Invoke-WebRequest "$base/TheFiberDad-win-x64.exe" -OutFile $file
  Write-Step 'Installing silently…'
  # NSIS: /S = silent, /CurrentUser = per-user install (no elevation needed)
  $proc = Start-Process -FilePath $file -ArgumentList '/S' -Wait -PassThru
  if ($proc.ExitCode -ne 0) {
    Write-Warning "Installer exited with $($proc.ExitCode) — retry interactively (double-click the exe): $file"
    Start-Process explorer.exe "/select,$file"
    exit 1
  }
  Write-Host "   installer log/exe kept at: $file"
}

Remove-Item -Recurse -Force $tmp -ErrorAction SilentlyContinue
Write-Host ''
Write-Host '✅ The Fiber Dad installed — look for it in the Start menu.'
Write-Host "   First launch: 'Connect to existing Hermes' → your gateway URL, then sign in."
Write-Host '   Re-running this command installs/updates to the newest release.'