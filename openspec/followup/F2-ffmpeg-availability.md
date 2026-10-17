---
id: F2
title: Ensure ffmpeg and ffprobe are available to RoughCut without a manual install
found: 2026-10-13
source: conversation
capability:
location:
type: idea
size: S
---

## What
RoughCut will need ffmpeg (cutting/exporting clips) and ffprobe (reading OBS
chapter markers), and nothing bundles them. The approach is decided (see
Notes); it is built by the first change that reads real recordings (markers or
export), whose proposal resolves F2.

## Why it matters
If ffmpeg is missing, the app fails on a fresh machine. Asking Azzey to install
it manually is the worst experience, especially for the single-binary release (F1).

## Notes
- No code calls ffmpeg yet. Playback doesn't need ours: PySide6's QtMultimedia
  wheel ships its own FFmpeg libraries.
- ffprobe is required: `ffprobe -show_chapters` is the clean way to read OBS
  chapters; parsing `ffmpeg -i` stderr is brittle.
- Decided lookup order, first hit wins:
  1. `ROUGHCUT_FFMPEG` env var (folder holding ffmpeg.exe and ffprobe.exe).
  2. PATH, plus winget's `%LOCALAPPDATA%\Microsoft\WinGet\Links` (a fresh
     winget install isn't on the running app's PATH). The user's own build may
     be newer or have hardware encoding.
  3. RoughCut-managed copy in `%LOCALAPPDATA%\RoughCut\ffmpeg`.
- Decided fallback when nothing is found:
  1. Ask Azzey, then download a pinned BtbN win64 build from its GitHub
     release into the managed folder, verified against a pinned SHA-256.
     Prefer BtbN's LGPL variant. We own bumping the pin and checksum.
  2. If the download fails: offer `winget install Gyan.FFmpeg.Essentials`,
     then re-check the Links folder.
  3. If that fails too: a plain message with a link to get FFmpeg.
- Licensing: RoughCut is GPLv3 and runs ffmpeg as a separate program
  (aggregation), so ffmpeg's licence doesn't constrain RoughCut. Downloading
  from upstream means upstream distributes ffmpeg and hosts its source. Credit
  ffmpeg in the README/about.
- Ruled out:
  - `imageio-ffmpeg`: ships ffmpeg only, no ffprobe.
  - `static-ffmpeg`: downloads on first use too, so it's option B with less
    control over version and source.
  - Shipping ffmpeg inside the release: breaks the single binary (F1), adds
    ~100+ MB per release, and makes us the redistributor (licence text,
    source offer).
  - Requiring a manual install: worst for Azzey; kept only as the last-resort
    message.
- Related: F1 (single-binary release pipeline).
