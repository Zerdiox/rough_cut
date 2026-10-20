# Tasks

## 1. Header text

- [x] 1.1 Write failing tests for the auto-handle header text: "On, 20 s / 5 s" for the defaults, "On, 30 s / 5 s" after changing before, "Off" when disabled; verify they fail for the missing function
- [x] 1.2 Write failing tests for the marker editor header text on `raid_night`: "Ambush" with 00:11:40 when marker 2 is selected, the new name after a rename, "Unnamed" with 00:27:05 for marker 4, "No marker selected" with nothing selected; verify they fail
- [x] 1.3 Implement both header text functions (session in, text out, using the existing time format); verify the tests from 1.1 and 1.2 pass

## 2. Fold panel

- [x] 2.1 Write failing offscreen tests for a fold panel: it starts in the state it was given, clicking the header toggles the body's visibility, the header text refreshes when the session emits `changed` or `selectionChanged`; verify they fail
- [x] 2.2 Implement the fold panel (clickable header with chevron, title and elided state text above a body that is shown or hidden; no animation); verify the tests from 2.1 pass

## 3. Marker editor folds only by hand

- [x] 3.1 Write failing offscreen tests for the marker editor's fold panel: folded, selecting a marker keeps it folded and the header follows; open, selecting another marker keeps it open on that marker; clearing the selection keeps it open on the hint with "No marker selected"; folding by hand then editing the marker or dragging a window keeps it folded; with nothing selected, clicking the header opens it on the hint; verify they fail
- [x] 3.2 Make the marker editor's fold panel a plain fold panel that only the header opens or folds (start state still from the selection); verify the tests from 3.1 pass

## 4. Main window and stories

- [x] 4.1 Write failing offscreen tests for the main window: on open, the auto-handle settings are folded; the marker editor is folded with no selection and open with one; the marker list never folds and grows taller when a panel folds; verify they fail
- [x] 4.2 Wrap the marker editor ("Marker") and auto-handle settings ("Suggest clips") in fold panels in the main window's side panel, keeping the dividers; verify the tests from 4.1 pass
- [x] 4.3 Add gallery stories: marker editor folded and open, folded header for an unnamed marker, auto-handle settings folded (on) and folded (off) and open, and "Main (both panels folded)"; keep the existing stories working; verify the smoke test that builds every story passes
- [x] 4.4 Run `python -m unittest discover -s tests` and verify it is green
- [x] 4.5 Write a failing offscreen test that the main window's preferred height is the same with both panels open and both folded; give the video area a 16:9 preferred size so "Main (loaded)" still fits the gallery at 1440x900 without scrolling; verify the test, the story smoke test and `python -m unittest discover -s tests` are green

## 5. Go to the selected marker

- [x] 5.1 Write failing tests for the session: selecting a marker moves the playhead to its time and emits `playheadChanged`; clearing the selection leaves the playhead; editing a marker doesn't move it; verify they fail
- [x] 5.2 Add `set_playhead` / `playheadChanged` to the session and move the playhead on selection; make the transport readout and detail timeline repaint on `playheadChanged`; verify the tests from 5.1 pass
- [x] 5.3 Write failing offscreen tests for the timeline panel showing 00:08:00 to 00:16:00: selecting Breach (00:03:12) brings it into view (00:00:00 to 00:08:00, clamped at the start) and moves the overview box; selecting Ambush (00:11:40) leaves the range unchanged; verify they fail
- [x] 5.4 Make the detail timeline center on the selected marker only when it is outside the visible range; verify the tests from 5.3 pass and the story smoke test and `python -m unittest discover -s tests` are green

## 6. Marker color flyout

- [x] 6.1 Write failing offscreen tests for the marker editor: one color dot with the marker's color name as tooltip and no visible color grid; clicking the dot opens a flyout with 16 colors and the current one checked; picking Red sets the marker to Red, closes the flyout and updates the dot; closing the flyout without picking leaves the color; verify they fail
- [x] 6.2 Replace the editor's color grid with the dot after the name field, opening a `Flyout` with the 16 colors; verify the tests from 6.1 pass
- [x] 6.3 Check the "Marker editor" stories still build and show the dot; verify the story smoke test and `python -m unittest discover -s tests` are green

## 7. Manual check in the gallery

- [x] 7.1 Walk the gallery in light and in dark and tick each:
  - [x] Every new and existing story opens without an error
  - [x] Main (loaded): clicking "Suggest clips" opens it; the before and after numbers are visible in their boxes; clicking again folds it and the marker list grows while the video area keeps its size
  - [x] Main (loaded): with settings folded, the header reads "On, 20 s / 5 s"; open them, change before to 30 and turn them off; the header follows each change
  - [x] Main (loaded): fold the marker editor, click another marker in the list, and the editor stays folded with the header showing that marker; drag a window edge on the timeline, and it stays folded; open it, clear the selection, and it stays open on the hint
  - [x] Renaming the selected marker updates the editor header as you type
  - [x] Main (empty): both panels are folded, the marker editor header reads "No marker selected", and clicking it shows the hint
  - [x] Header text fits the side panel or elides cleanly; the chevron points right when folded and down when open
  - [x] At a 1440x900 window the marker list shows clearly more rows with both panels folded than open
  - [x] Main (loaded): clicking Breach in the marker list moves the playhead and readout to 00:03:12 and the timeline scrolls to show it; clicking a marker already in view moves the playhead without scrolling the strip
  - [x] Clicking a flag on the detail timeline selects it and moves the playhead there without scrolling the strip
  - [x] The color dot sits after the name field; clicking it opens the flyout next to it with the current color ringed and names on hover
  - [x] Picking a color closes the flyout and the marker list and timeline follow; Esc or clicking outside closes it unchanged
  - [x] The open marker editor is two rows shorter than before

## 8. Follow-up harvest

- [x] 8.1 List each out-of-scope issue discovered during implementation as a follow-up candidate in the completion summary; record them (see openspec/followup/README.md) on Kenny's go.
