# The Fiber Dad Desktop — brand fork notes

This repo is a public fork of **NousResearch/hermes-agent** (MIT-licensed).
The `thefiberdad` branch carries the branding customization; `main` tracks
upstream. Use these notes to maintain the fork.

## What changed vs upstream

Everything functional is upstream. The brand layer is:

| File | Change |
|---|---|
| `apps/desktop/product-identity.cjs` | `fiberdad` variant: display name **The Fiber Dad**, appId `com.thefiberdad.the-fiber-dad`, MSIX identity `TheFiberDad.TheFiberDad` |
| `apps/desktop/product-identity.cjs` | `appIdOrg` / `msixOrg` switch so the fiberdad variant installs beside stock Hermes without touching its userData |
| `apps/desktop/electron-builder.config.cjs` | Windows target `['msix', 'nsis']` for fiberdad (unsigned MSIX needs Developer Mode; the NSIS `.exe` does not), payload extraResources include fiberdad |
| `apps/desktop/scripts/before-build.mjs`, `scripts/write-build-stamp.mjs` | bundled-like launcher staging for fiberdad |
| `apps/desktop/src/components/chat/intro.tsx` | Wordmark string `THE FIBER DAD` |
| `apps/desktop/src/themes/accents.ts` | Default accent `#00b4ff` (Fiber Dad cyan) |
| `apps/nous-girl-*.svg` (root `assets/`) | Brand glyph: house + lightning bolt in the girl SVGs' 5487² canvases — drives **all** 99 generated icon targets |
| `scripts/bundles/desktop.py`, `scripts/bundles/desktop_prepare.py` | fiberdad accepted as a bundled-like variant |
| `.github/workflows/thefiberdad-*.yml` | Release + upstream-sync workflows |
| `apps/desktop/public/nous-girl{,-dark}.png`, `apple-touch-icon.png` | Rendered from the brand glyph masters |

Icons are committed generated artifacts (see `scripts/generate_icons.py`):
regenerate with `node scripts/generate-icons.mjs` after touching the glyph SVGs.

## Build the branded app locally

```bash
npm ci                                    # repo root
cd apps/desktop
npm run dist:fiberdad                     # payload stage + builders
# Windows: dist/*.msix + *.exe   macOS: dist/*.dmg + *.zip   Linux: dist/*.AppImage
```

## Release

Tag `tdfd-v<version>` (example: `tdfd-v0.21.3`) and push the tag —
`thefiberdad-release.yml` builds all three platforms and attaches the
installers to the tag's GitHub Release. No signing certificates are wired;
installers are unsigned (see workflow header for the per-OS caveats).

## Upstream sync

`thefiberdad-sync.yml` runs Monday 11:00 UTC: merges upstream into `main`,
then merges `main` into `thefiberdad`. On conflict it opens an issue instead
of diverging silently. Resolve the (tiny) conflict set by hand — keep the
fiberdad variant bits, take upstream elsewhere.

## No auto-update feed

Upstream installers self-update from their R2 feed; the fiberdad build bakes
**no** update feed (no `HERMES_PAYLOAD_TAG`/`CLOUDFLARE_R2_PUBLIC_URL` is set),
so the app never phones the Hermes update servers. Updates arrive when
upstream-sync + you tag a new `tdfd-v*` release.