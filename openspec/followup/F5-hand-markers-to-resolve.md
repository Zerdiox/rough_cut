---
id: F5
title: Hand markers to DaVinci Resolve alongside the exported clips
found: 2026-10-18
source: add-collapsible-side-panels
capability: clip-export
location:
type: idea
size: M
---

## What
Export markers (name, color, note, time) in a form DaVinci Resolve can import, so the moments marked
in RoughCut show up as Resolve markers in the same colors. Today export writes clip files only and
no marker reaches Resolve.

## Why it matters
Azzey marks moments in RoughCut and then edits further in Resolve; re-marking them there is
duplicate work. Losing the notes and colors between the two tools also loses why a moment was marked.

## Notes
- RoughCut's 16 marker color names are exactly Resolve's marker colors, so colors map one to one
  with no closest-match guessing. The on-screen shades are RoughCut's own (with a light and a dark
  value), not Resolve's exact values. This is why the marker color picker kept the fixed set instead
  of a free RGB color dialog.
- Believed but unverified: Resolve imports timeline markers from an EDL whose marker lines carry the
  color (`|C:ResolveColorYellow |M:name |D:1`). Check Resolve's documentation before relying on it.
- Open questions: markers per exported clip (times relative to the clip) or one list for the whole
  recording; whether markers inside a clip should also be written into the clip file itself as
  chapters, and whether Resolve reads those.
