---
id: F3
title: Gallery shell files need a restart instead of reloading live
found: 2026-10-14
source: add-component-gallery
capability: component-gallery
location: roughcut/gallery/reloader.py
type: tech-debt
size: S
---

## What
Saving the gallery window's own files (`roughcut/gallery/app.py`, `reloader.py`, `__main__.py`)
doesn't reload them: they stay loaded until the gallery is restarted. Every other file under
`roughcut/` reloads live.

## Why it matters
An edit to the gallery shell silently does nothing until a restart, which is confusing while
designing. Low impact, since the shell rarely changes.

## Notes
The README documents the limitation. Restarting the gallery process with the current story and
theme passed as `--story` / `--theme` would cover it.
