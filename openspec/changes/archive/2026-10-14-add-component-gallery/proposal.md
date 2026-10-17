# Proposal

## Why

RoughCut has no code yet, and the layout of a marker-driven mini editor is the riskiest part to get
wrong for a non-technical user. Kenny wants to settle the layout and the look of every piece before
any video, FFmpeg or export work starts, in a Storybook-style gallery where each component can be
seen in all its states with fake data, and shown to Azzey for feedback.

## What Changes

- New Python desktop project on PySide6 + QFluentWidgets (Fluent design, light and dark), replacing
  the Tkinter assumption in the project context.
- A **gallery** app: a sidebar of stories grouped as Foundations, Components and Screens; a stage that
  renders the selected story; a light/dark theme switch; and automatic reload of the shown story when
  a source file is saved.
- Foundations stories: colors, type, and the marker color set.
- Component stories, each with named states on fake recordings:
  - **Timeline** (overview strip and zoomed detail strip): empty, bookmarks only, clip windows,
    merged windows, auto-handles on and off, windows clamped at the recording's edges, 40+ markers,
    zoomed in. Clip window edges can be dragged.
  - **Marker list** and **marker editor** (name, color, note).
  - **Auto-handle settings** (on/off, seconds before, seconds after).
  - **Transport bar** (visual only, no playback).
  - **Summary bar** (clip count, total length, Export).
  - **Export dialog**: one row per clip with time range, editable clip name and read-only source
    marker; save folder; clip names that can't be used as Windows file names, or that clash, are
    flagged and Export is blocked until fixed.
- Screens stories: the main window empty and loaded (with a video viewer placeholder), and the export
  dialog over it.
- The clip rules behind those stories are real, not drawn by hand: markers without a window are
  bookmarks, auto-handles suggest windows only for markers without one and never touch windows set by
  hand, overlapping windows merge into one clip, windows clamp to the recording, and a clip's name
  starts as its marker's name (or `<recording> NN`) and is independent after that.
- A `.bat` launcher for the gallery so Azzey can open it without a terminal.

## Capabilities

### New Capabilities
- `component-gallery`: browsing RoughCut's UI pieces as stories with fake data, switching theme, and
  seeing saved changes without restarting.
- `clip-marking`: how markers become clips on the timeline: bookmarks, auto-handles, adjusting clip
  windows, merging and clamping.
- `clip-export`: naming clips before export and catching names that can't be written.

### Modified Capabilities
<!-- None: there are no existing specs. -->

## Out of Scope / Deferred

- Video playback, scrubbing, and the J/K/L, I/O and M keyboard controls. The viewer is a placeholder
  and the transport bar is visual only, so a bookmark can't be turned into a clip by hand yet (that
  needs I/O at a playhead).
- Reading OBS chapter markers from a recording, and any FFmpeg use.
- Writing clip files on Export; the dialog validates and stops there.
- Saving work between sessions (markers, windows, clip names).
- Packaging beyond a `.bat` launcher.

No follow-ups exist yet. Candidates for Kenny to approve as follow-ups:
- When two clips merge, a name typed on the later clip is hidden (the merged clip keeps the earlier
  clip's name).
- Default `<recording> NN` names follow clip position, so adding a clip earlier in the recording
  renumbers the untyped names after it (03 becomes 04).

## Resolves

None.

## Impact

- New: Python package, gallery entry point, unit tests, `requirements.txt` (PySide6 6.12,
  PySide6-Fluent-Widgets 1.11; both install on Python 3.14), `.bat` launcher.
- `openspec/config.yaml`: the stack line and research hint change from Tkinter to PySide6 +
  QFluentWidgets.
- License: PySide6-Fluent-Widgets is GPLv3 for non-commercial use, which fits a personal tool; a
  commercial release would need its commercial license.
