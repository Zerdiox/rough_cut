# Design

## Context

The repository has no application code yet. The stack is Python 3.14 on Windows, PySide6 6.12 and
PySide6-Fluent-Widgets 1.11 (both install on 3.14), with FFmpeg already on PATH but unused by this
change. The gate is `python -m unittest discover -s tests`. See proposal.md for scope and the specs
for behaviour.

## Goals / Non-Goals

**Goals:**
- The widgets built here are the ones the real editor will use; the gallery only feeds them made-up
  data. Nothing is drawn just for the gallery.
- The clip rules (bookmarks, auto-handles, merging, clamping, names) live in plain Python with no Qt,
  so they are unit-tested directly.
- Saving a file redraws the shown story fast enough to design by trial and error.

**Non-Goals:**
- No video decoding, playhead or keyboard transport. The transport bar draws its controls only.
- No persistence. Every story starts from its fixture.

## Decisions

### Package layout: one importable package at the repository root
```
roughcut/
  model/      recording, markers, clip derivation, clip names   (no Qt)
  ui/         theme tokens, widgets, main window, export dialog  (Qt)
  gallery/    gallery window, story registry, reloader, fixtures, stories/
tests/
requirements.txt
gallery.bat
```
`python -m unittest discover -s tests` run from the repository root can import `roughcut` because
`-m` puts the working directory on the import path, so tests need no path tweaking and there is no
install step. A `src/` layout was considered; it needs an editable install before tests run, which
is one more thing to break on Azzey's machine.

### Clip rules: store only what the user set, derive the rest
Times are whole milliseconds (integers) so merges and clamps compare exactly.

- A marker holds its time, name, color, note, and an optional **hand-set window**.
- Handle settings hold on/off, seconds before, seconds after.
- A marker's **effective window** is its hand-set window if it has one; otherwise, when handles are
  on, `[time - before, time + after]`; otherwise none (a bookmark).
- **Clips** are derived on demand: take all effective windows, clamp each to `[0, duration]`, sort by
  start, and merge any that overlap or touch. Each clip records the markers it came from.

Because suggested windows are never stored, turning handles off, on, or changing their lengths can't
touch a hand-set window, which is the rule the spec cares most about. Storing suggested windows and
flagging them was the alternative; it needs every settings change to rewrite markers and is easy to
get wrong.

**Dragging an edge** of a clip moves the window that forms that edge (the earliest-starting window for
the start, the latest-ending one for the end). The drag first copies that window's effective values
into a hand-set window, then moves the edge, limited so start <= marker time <= end and within the
recording.

### Clip names keyed by the clip's earliest marker
A clip's identity is its earliest marker. Names the user typed are stored per marker id; anything not
typed is computed: the earliest marker's name, else `<recording> NN` with NN the clip's 1-based
position in recording order. This keeps edited names through resizes (the earliest marker doesn't
change) and keeps marker renames flowing into clips the user never renamed. When two clips merge, the
merged clip keeps the earlier clip's name; a typed name on the later clip is no longer shown (it is
kept, and returns if the clips separate again). That is a rare case and is acceptable for a rough cut.

Name validation is a pure function over the list of names returning a problem per row: empty, a
forbidden character, trailing space or dot, a reserved device name (checked on the part before the
first dot, case-insensitive), or a case-insensitive duplicate.

### One session object between model and widgets
A small Qt `QObject` wraps the recording, handle settings and clip names and emits `changed` after any
edit. Every widget reads from it and repaints on `changed`; edits go through it. Widgets never talk to
each other. The main window and every component story build a session from a fixture, so a component
in a story behaves exactly as it does in the main window (dragging a window updates the summary bar in
the "Main (loaded)" story).

### Timeline strips are custom-painted widgets
The overview and detail strips are `QWidget`s painted with `QPainter`, with mouse handling for edge
drags and a zoom/scroll state on the detail strip. `QGraphicsView` was considered; it adds a scene
graph and item lifecycle that two strips of rectangles and flags don't need. Colors come from the
theme tokens so both strips follow light/dark.

### Theme tokens and marker colors
`ui/theme` holds named color tokens for light and dark, follows QFluentWidgets' theme switch, and
defines the marker color set. The set is the 16 marker colors DaVinci Resolve offers (Blue, Cyan,
Green, Yellow, Red, Pink, Purple, Fuchsia, Rose, Lavender, Sky, Mint, Lemon, Sand, Cocoa, Cream), since
Azzey already thinks in those; the exact shades are ours, tuned to read on both themes.

### Gallery: registry, stage, reloader
- Stories are functions registered with a decorator naming their group, component and state
  (`Components / Timeline / merged windows`). Each returns a widget built from a fixture.
- The gallery window is a Fluent window: a tree of stories on the left, a stage on the right, a
  light/dark switch in the title bar.
- **Reload**: a `QFileSystemWatcher` on the `roughcut` folder, debounced ~300 ms. On a change, every
  `roughcut.*` module except the gallery shell itself is dropped from `sys.modules`, the story
  modules are imported again, and the shown story is rebuilt. Old widgets are destroyed with the old
  stage contents, so no instance of an old class survives. If the import or build raises, the stage
  shows the traceback and the watcher keeps running.
  Alternatives: `importlib.reload` per module (has to be done in dependency order and leaves stale
  references in modules that imported names), or restarting the whole process on save (robust but
  loses window position and flickers). If dropping modules proves unreliable, process restart with the
  selected story and theme passed on the command line is the fallback.

### Launcher
`gallery.bat` creates `.venv` and installs `requirements.txt` on first run, then starts the gallery
with `pythonw -m roughcut.gallery` so no console window stays open.

### Testing
- `tests/` covers clip derivation, handle settings, edge drags, clamping, merging, default names and
  name validation as plain unit tests, written before the code.
- A smoke test sets `QT_QPA_PLATFORM=offscreen`, creates the application once, and builds every
  registered story, so a broken story fails the gate.
- Widget layout and look are checked by eye in the gallery, listed as manual tasks.

## Risks / Trade-offs

- [PySide6-Fluent-Widgets is GPLv3] -> Fine for a personal, non-commercial tool; noted in the proposal.
  A commercial release would need the commercial license or a swap to plain Qt widgets.
- [Module purging misses state held by Qt (for example a registered theme callback pointing at an old
  function)] -> Callbacks are connected per story build and disconnected when the stage is cleared;
  process restart is the fallback.
- [Custom-painted timeline needs its own hit-testing and accessibility] -> Acceptable for two strips;
  keyboard editing arrives with the transport change.
- [Python 3.14 is new and some later dependency (for example a video binding) may lag] -> Checked for
  this change's dependencies; recheck when playback is planned.
