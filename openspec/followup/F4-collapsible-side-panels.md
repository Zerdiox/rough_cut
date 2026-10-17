---
id: F4
title: Collapsible side panels in the main window
found: 2026-10-14
source: add-component-gallery
capability: component-gallery
location: roughcut/ui/main_window.py
type: idea
size: M
---

## What
Make the side panels (marker list, marker editor, auto-handle settings) collapsible, so Azzey can
fold away the ones he isn't using and give the marker list more room.

## Why it matters
The side panel is the tallest part of the main window, which needs at least 734 px of height. The
marker list already shrinks to about two rows at 1440x900, and playback will add more controls.

## Notes
- Size M rather than S because collapsing is new behaviour: it needs a spec requirement and gallery
  stories for the collapsed and expanded states.
- Open when promoted: should collapsed or expanded state be remembered between sessions? Nothing is
  saved between sessions yet.
- A 1080p screen at 100% scaling fits today; this is about room, not overflow.
