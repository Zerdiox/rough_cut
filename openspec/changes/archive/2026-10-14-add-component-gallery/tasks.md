# Tasks

## 1. Project setup

- [x] 1.1 Create `.venv` with Python 3.14, add `requirements.txt` pinning PySide6 6.12 and PySide6-Fluent-Widgets 1.11, install it, and verify `python -c "import PySide6, qfluentwidgets"` succeeds
- [x] 1.2 Create the `roughcut/` package (`model/`, `ui/`, `gallery/stories/`) and `tests/` with an empty passing test; verify `python -m unittest discover -s tests` runs from the repository root and reports OK
- [x] 1.3 Update `openspec/config.yaml` context: stack is PySide6 + QFluentWidgets (not Tkinter), research hint names PySide6/QFluentWidgets; verify `openspec validate --all` still passes

## 2. Clip rules (no Qt)

- [x] 2.1 Write failing tests for markers and effective windows: bookmark when no window and handles off; suggested `[t-before, t+after]` when on; hand-set window wins; default handles on, 20 s / 5 s
- [x] 2.2 Implement recording, marker and handle settings with millisecond times so 2.1 passes
- [x] 2.3 Write failing tests for clip derivation: clamping at 0 and at duration, merging overlapping and touching windows (00:11:40 + 00:11:50 -> one clip 00:11:20-00:11:55), recording order, count and total length
- [x] 2.4 Implement clip derivation so 2.3 passes
- [x] 2.5 Write failing tests for edge drags: dragging materialises a hand-set window, start can't pass its marker, end can't pass its marker, edges clamp to the recording, a dragged window survives handle on/off and length changes, merged-clip edges move the window that forms them
- [x] 2.6 Implement edge drags so 2.5 passes
- [x] 2.7 Write failing tests for clip names: default from earliest marker name, `<recording> NN` for unnamed, typed name kept across a resize, typed name independent of marker rename, merge keeps the earlier clip's name
- [x] 2.8 Implement clip names so 2.7 passes
- [x] 2.9 Write failing tests for name validation: empty, each forbidden character, trailing space/dot, reserved names (`con`, `NUL.txt`, `COM1`, `LPT1`), case-insensitive duplicates flag both rows, count of problems
- [x] 2.10 Implement name validation so 2.9 passes

## 3. Theme and session

- [x] 3.1 Add theme tokens for light and dark and the 16 marker colors; verify with a unit test that every marker color has a name and a value for both themes
- [x] 3.2 Add the session object wrapping recording, handle settings and clip names that emits `changed` after each edit; verify with an offscreen unit test that a handle change, an edge drag and a rename each emit `changed` once
- [x] 3.3 Add fixtures: empty recording, `raid_night_0412` (1:22:10, six named markers incl. one unnamed and two close together), a 40+ marker recording, a recording with a marker 5 s from each edge; verify a unit test loads each fixture into a session

## 4. Gallery shell

- [x] 4.1 Add the story registry (group / component / state) with a test that registering two stories lists them grouped and in order
- [x] 4.2 Add the gallery window: story tree, stage, light/dark switch; `python -m roughcut.gallery` opens it on the first story; verify by launching it
- [x] 4.3 Add the reloader (watch `roughcut/`, debounce, drop `roughcut.*` modules except the shell, rebuild the shown story, show the traceback on failure); verify by hand: edit a story's label and save -> stage updates on the same story and theme; introduce a syntax error -> traceback shows, gallery stays open; fix it -> story returns
- [x] 4.4 Add an offscreen smoke test that builds every registered story; verify it passes and fails when a story raises
- [x] 4.5 Add `gallery.bat` (create `.venv` and install on first run, then `pythonw -m roughcut.gallery`) and a short `README.md` covering what RoughCut is and how to open the gallery; verify double-clicking the bat on a machine state without `.venv` opens the gallery

## 5. Foundations stories

- [x] 5.1 Add Foundations stories: colors, type scale, marker colors with names; verify the smoke test passes and each shows correctly in light and dark

## 6. Component widgets and stories

- [x] 6.1 Build the overview timeline strip (whole recording, marker flags, clip blocks, visible-range box) with stories: empty, bookmarks only, clips, 40+ markers; verify the smoke test passes
- [x] 6.2 Build the detail timeline strip (zoom and scroll, flags with names, clip blocks, draggable edges via the session) with stories: empty, bookmarks only, clip windows, merged windows, handles on, handles off, clamped at edges, 40+ markers, zoomed in; verify the smoke test passes
- [x] 6.3 Build the marker list (time, color dot, name; selecting a marker selects it in the session) with stories: empty, few markers, 40+ markers, one selected; verify the smoke test passes
- [x] 6.4 Build the marker editor (name, color picker over the 16 colors, note) with stories: nothing selected, marker selected, unnamed marker; verify the smoke test passes
- [x] 6.5 Build the auto-handle settings (on/off switch, before and after seconds) with stories: on 20/5, off; verify the smoke test passes
- [x] 6.6 Build the transport bar (buttons and time readout, visual only) with a story at 00:11:40 / 01:22:10; verify the smoke test passes
- [x] 6.7 Build the summary bar (clip count, total length, Export button) with stories: 0 clips, 3 clips; verify the smoke test passes
- [x] 6.8 Build the export dialog (rows with range, editable name, read-only marker; save folder with Browse; problem flags per row; problem count; Export disabled while any problem) with stories: all valid, forbidden character, duplicates, empty name, reserved name; verify the smoke test passes

## 7. Screens

- [x] 7.1 Compose the main window (viewer placeholder, marker list + editor + handle settings on the right, transport bar, overview and detail strips, summary bar) from the shared session, with stories "Main (empty)" and "Main (loaded)"; verify the smoke test passes
- [x] 7.2 Add the "Export dialog over main" screen story; Export in the summary bar opens the dialog in the loaded story; verify the smoke test passes
- [x] 7.3 Run `python -m unittest discover -s tests` and verify it is green

## 8. Manual check in the gallery

- [x] 8.1 Walk the gallery in light and in dark and tick each:
  - [x] Every story in the tree opens without an error
  - [x] Marker colors story shows 16 named swatches, readable on both themes
  - [x] Detail strip: dragging a window's start left grows it and the summary total grows by the same amount; dragging past the marker stops at the marker
  - [x] Main (loaded): turning auto-handles off leaves only hand-set windows, the rest become flags; turning on brings suggestions back; changing "before" resizes suggestions only
  - [x] Main (loaded): the two close markers show as one clip and the summary counts it once
  - [x] Export dialog: renaming a clip doesn't rename its marker in the list; "Ambush?" flags the row and disables Export; "Breach"/"breach" flags both; fixing the last one enables Export
  - [x] Editing a widget file while its story is shown updates the stage within a couple of seconds
  - [x] `gallery.bat` opens the gallery with no console window left open

## 9. Follow-up harvest

- [x] 9.1 List each out-of-scope issue discovered during implementation as a follow-up candidate in the completion summary; record them (see openspec/followup/README.md) on Kenny's go.
