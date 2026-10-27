#!/usr/bin/env bash
# The Fiber Dad desktop — one-command installer (Linux + macOS).
#
#   curl -fsSL https://github.com/prhall0603/hermes-agent/releases/latest/download/fd-install.sh | bash
#   (or: bash fd-install.sh)
#
# Flags:  --uninstall   remove the app + launcher entry
#
# What it does:
#   Linux : downloads the AppImage from the latest tdfd-v* GitHub release,
#           installs to ~/.local/bin (FUSE present) or a self-contained
#           extraction without it, fixes the sandbox when passwordless sudo
#           works, and writes the application-menu entry + icon.
#   macOS : mounts the DMG, copies the app into /Applications, clears the
#           quarantine attribute (unsigned build).
set -u

REPO="prhall0603/hermes-agent"
LATEST="$REPO/releases/latest/download"

info() { printf '\033[1;36m==>\033[0m %s\n' "$*"; }
fail() { printf '\033[1;31mx\033[0m %s\n' "$*" >&2; exit 1; }

command -v curl >/dev/null 2>&1 || fail "curl is required"
OS="$(uname -s)"

# ── uninstall ────────────────────────────────────────────────────────────
if [ "${1:-}" = "--uninstall" ]; then
  info "Uninstalling The Fiber Dad…"
  if [ "$OS" = "Darwin" ]; then
    rm -rf "/Applications/The Fiber Dad.app"
  else
    rm -rf "$HOME/.local/bin/the-fiber-dad" "$HOME/.local/share/thefiberdad"
    rm -f "$HOME/.local/share/applications/thefiberdad.desktop"
    rm -f "$HOME/.local/share/icons/hicolor/256x256/apps/thefiberdad.png"
  fi
  echo "Removed."
  exit 0
fi

dl() { # dl <asset-name> <dest>
  info "Downloading $1"
  curl -fL --retry 3 --progress-bar "$LATEST/$1" -o "$2" || fail "download failed: $1"
}

# ── macOS ────────────────────────────────────────────────────────────────
if [ "$OS" = "Darwin" ]; then
  [ "$(uname -m)" = "arm64" ] || fail "No x64 DMG is built yet (apple silicon only)"
  TMP="$(mktemp -d)"
  dl "TheFiberDad-mac-arm64.dmg" "$TMP/fd.dmg"
  info "Mounting DMG"
  hdiutil attach -quiet -nobrowse -mountpoint "$TMP/mnt" "$TMP/fd.dmg" || fail "mount failed"
  SRC="$(find "$TMP/mnt" -maxdepth 1 -name "*.app" -print -quit)"
  [ -d "$SRC" ] || fail "DMG did not contain an .app bundle"
  info "Installing to /Applications (may ask for your password)"
  sudo rm -rf "/Applications/$(basename "$SRC")"
  sudo cp -R "$SRC" /Applications/ || fail "copy failed"
  hdiutil detach -quiet "$TMP/mnt" || true
  rm -rf "$TMP"
  # Unsigned build: drop the quarantine so Gatekeeper's warning is skipped.
  xattr -dr com.apple.quarantine "/Applications/$(basename "$SRC")" 2>/dev/null || true
  echo
  echo "Installed. Launch 'The Fiber Dad' from Spotlight or /Applications."
  exit 0
fi

# ── Linux ────────────────────────────────────────────────────────────────
[ "$OS" = "Linux" ] || fail "Unsupported OS: $OS (Windows uses fd-install.ps1)"
[ "$(uname -m)" = "x86_64" ] || fail "Unsupported architecture: $(uname -m)"

TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT
APPIMAGE="TheFiberDad-linux-x86_64.AppImage"
dl "$APPIMAGE" "$TMP/app.AppImage"
chmod +x "$TMP/app.AppImage"

# FUSE (libfuse2 present) → run the AppImage directly; otherwise extract once.
if command -v fusermount3 >/dev/null 2>&1 || ldconfig -p 2>/dev/null | grep -q "libfuse.so.2"; then
  mkdir -p "$HOME/.local/bin"
  mv "$TMP/app.AppImage" "$HOME/.local/bin/the-fiber-dad"
  EXECLINE="$HOME/.local/bin/the-fiber-dad"
  APPDIR=""
else
  info "No libfuse2 — extracting a self-contained copy instead"
  mkdir -p "$HOME/.local/share/thefiberdad"
  (cd "$TMP" && ./app.AppImage --appimage-extract > /dev/null 2>&1) || fail "extraction failed"
  [ -x "$TMP/squashfs-root/AppRun" ] || fail "extraction produced no AppRun"
  rm -rf "$HOME/.local/share/thefiberdad/app"
  mv "$TMP/squashfs-root" "$HOME/.local/share/thefiberdad/app"
  EXECLINE="$HOME/.local/share/thefiberdad/app/AppRun"
  APPDIR="$HOME/.local/share/thefiberdad/app"

  # Sandbox: needs chrome-sandbox setuid root. Try passwordless sudo without
  # prompting; if that's not possible, launch with the sandbox disabled.
  SB="$APPDIR/chrome-sandbox"
  if sudo -n chown root:root "$SB" 2>/dev/null && sudo -n chmod 4755 "$SB" 2>/dev/null; then
    echo "   sandbox fixed (setuid)"
  else
    EXECLINE="$EXECLINE --no-sandbox"
    echo "   note: launched with --no-sandbox (sudo needed a password)"
  fi
fi

# Icon
curl -fL --retry 3 -s "$LATEST/thefiberdad-icon.png" -o "$TMP/icon.png" \
  && mkdir -p "$HOME/.local/share/icons/hicolor/256x256/apps" \
  && mv "$TMP/icon.png" "$HOME/.local/share/icons/hicolor/256x256/apps/thefiberdad.png" || true

# Launcher entry
mkdir -p "$HOME/.local/share/applications"
cat > "$HOME/.local/share/applications/thefiberdad.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=The Fiber Dad
Comment=The Fiber Dad AI assistant (Hermes fork)
Exec=$EXECLINE
Icon=thefiberdad
Terminal=false
Categories=Network;Utility;
StartupWMClass=com.thefiberdad.the-fiber-dad
EOF
command -v update-desktop-database >/dev/null 2>&1 && update-desktop-database "$HOME/.local/share/applications" 2>/dev/null || true

echo
echo "✅ The Fiber Dad installed — find it in your applications menu."
echo "   First launch: 'Connect to existing Hermes' → your gateway URL, then sign in."
echo "   Re-running this command installs/updates to the newest release."