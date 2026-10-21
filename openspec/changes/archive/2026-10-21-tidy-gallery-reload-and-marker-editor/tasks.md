# Tasks

## 1. Marker editor follows outside changes

- [x] 1.1 Write failing offscreen tests for the marker editor on `raid_night` with Ambush selected: renaming it to "Ambush and push" and making it Red through the session updates the name field and the color dot without reselecting; changing its note through the session updates the note; typing a character in the middle of the name leaves the cursor right after it and the field's text equal to the marker's name; verify they fail
- [x] 1.2 Make the marker editor refresh on `changed` as well, setting the time, name, note and color dot only where they differ from the marker, and drop the separate dot update after picking a color; verify the tests from 1.1 and the existing color flyout tests pass

## 2. Gallery restarts itself on a shell save

- [x] 2.1 Write failing tests for telling a shell save apart: with a temporary copy of the shell files, an unchanged save and a save to a story file are not shell saves; changing a shell file's content is; verify they fail
- [x] 2.2 Implement the snapshot of the shell files' contents taken at start and the comparison on each change; verify the tests from 2.1 pass
- [x] 2.3 Write failing tests for the load check: a shell that imports cleanly reports success; a shell with a syntax error or a failing import reports failure with the error text; verify they fail
- [x] 2.4 Implement the load check as an asynchronous child process with the same Python, run from the folder holding the `roughcut` package, with a save during a running check starting a fresh check afterwards; verify the tests from 2.3 pass
- [x] 2.5 Write failing offscreen tests for the gallery window, with the restart itself replaced by a recorder: a shell save whose check passes asks for a restart with the current story ("Group/Component/State") and theme; a failing check shows the error on the stage, keeps the window, and asks for no restart; a story save reloads in place without a check; a restart that fails to start shows an error; verify they fail
- [x] 2.6 Wire it into the gallery window: start the new gallery detached with `-m roughcut.gallery --story ... --theme ...` and quit on success, show the error otherwise; verify the tests from 2.5 pass
- [x] 2.6a Make a restart leave exactly one gallery even when the old gallery's restart code is broken: the old one exits with `exit(0)` and stops reacting to saves before restarting (showing any restart error), and the new one ends the old process passed as `--replace <pid>` once shown, only if it is a running python(w).exe; verify the restart tests and a replay of switching `started = result[0]` to `//` and back leave one gallery window
- [x] 2.7 Remove the README's note that changes to the gallery window need a restart and update the watcher's module docstring to match; verify the README's gallery section describes shell saves as restarting on the same story and theme
- [x] 2.8 Run `python -m unittest discover -s tests` and verify it is green

## 3. Manual check in the gallery

- [ ] 3.1 Start the gallery with `gallery.bat`, switch to dark, open "Main (loaded)", then tick each:
  - [ ] Editing and saving a component file (e.g. a color token in `roughcut/ui/theme.py`) redraws the story in place, without the window blinking
  - [ ] Adding a harmless line to `roughcut/gallery/app.py` and saving restarts the gallery within a few seconds, on "Main (loaded)" in dark
  - [ ] Saving `app.py` with a syntax error shows the error on the stage and the gallery stays open; fixing and saving restarts it on the same story and theme
  - [ ] Saving `app.py` with an import of a name that doesn't exist does the same
  - [ ] Saving a shell file without changing it does nothing
  - [ ] Main (loaded): typing in the middle of the marker name keeps the cursor in place; picking a color from the dot still updates the dot, list and timeline
  - [x] Revert the test edits to `app.py` and `theme.py` afterwards

## 4. Follow-up harvest

- [x] 4.1 List each out-of-scope issue discovered during implementation as a follow-up candidate in the completion summary; record them (see openspec/followup/README.md) on Kenny's go.
