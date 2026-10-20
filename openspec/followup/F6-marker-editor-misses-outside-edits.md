---
id: F6
title: Marker editor doesn't refresh when the selected marker is edited from elsewhere
found: 2026-10-20
source: add-collapsible-side-panels
capability: clip-marking
location: roughcut/ui/markers.py:211
type: tech-debt
size: S
---

## What
The marker editor reloads its fields (name, note, color dot) only on `selectionChanged`. The
color dot stays correct because the flyout sets it directly when a color is picked. If anything
else changes the selected marker's name, color or note, the editor keeps showing the old values.

## Why it matters
Nothing does that today, but the planned marker shortcuts, undo or an import would. The editor
would then show the old values, and the next edit typed into it could overwrite the new ones.

## Notes
Refreshing on `changed` means the name field mustn't be reset while Azzey is typing in it (cursor
jumps). One fix is to reload only fields whose value differs from the marker's. No test covers this
yet.
