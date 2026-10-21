---
id: F8
title: A broken gallery window file shows its error again on every save
found: 2026-10-21
source: tidy-gallery-reload-and-marker-editor
capability: component-gallery
location: roughcut/gallery/app.py:144
type: idea
size: S
---

## What
While one of the gallery window's own files fails to load, every save re-runs the load check and
shows that error again, including saves to story files. The story being worked on stays hidden
until the window file is fixed.

## Why it matters
Undocumented. Someone fixing a story while a window file is half-edited sees the window error
instead of their story, which looks like their story broke.

## Notes
Comparing contents with the files at start makes every later save a "shell save" until the files
match again or load. Could reload the story in place when only story files changed since the last
failed check, keeping the shell error in a banner.
