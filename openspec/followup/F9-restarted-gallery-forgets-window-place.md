---
id: F9
title: A restarted gallery opens maximized and behind other windows
found: 2026-10-21
source: tidy-gallery-reload-and-marker-editor
capability: component-gallery
location: roughcut/gallery/__main__.py:33
type: idea
size: S
---

## What
After a save to the gallery window's own files restarts it, the new gallery opens maximized on the
main screen, ignoring the old window's size, position and screen, and Windows keeps it behind the
window that was in front (the editor).

## Why it matters
Mildly disruptive on multi-monitor setups: the gallery jumps screens and has to be found again.
The design leaves this out of scope.

## Notes
The old gallery could pass its geometry (and maximized state) like `--story` and `--theme`. Coming
to the front is limited by Windows' foreground lock; the old process could call
`AllowSetForegroundWindow` for the new one's process id before it leaves.
