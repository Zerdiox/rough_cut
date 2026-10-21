# Proposal

## Why

Two small gaps left over from earlier changes. Saving one of the gallery window's own files does
nothing until the gallery is restarted by hand, which is confusing while designing (F3). The
marker editor only reloads its fields when the selection changes, so once anything other than the
editor changes the selected marker (marker shortcuts, undo or an import, all planned), the editor
would show old values and the next keystroke could overwrite the new ones (F6). Fixing both now
keeps the gallery's "save and see it" promise whole and puts the editor rule in place before the
features that need it.

## What Changes

- Saving one of the gallery window's own files restarts the gallery on the same story and theme,
  instead of needing a manual restart. Saving any other file keeps reloading in place, as today.
- Before restarting, the gallery checks that the saved files load. If they don't, it shows the error
  in place of the story and stays open, the same as for a broken story; saving the fixed file then
  restarts it.
- The marker editor always shows the selected marker's current name, color and note, also when they
  change somewhere other than the editor. The field being typed in is never reset under the cursor.
- The README no longer says that changes to the gallery window need a restart.

## Capabilities

### New Capabilities
<!-- None. -->

### Modified Capabilities
- `component-gallery`: "Saved changes appear without restarting" now also covers the gallery
  window's own files, including saving a broken one.
- `clip-marking`: adds a requirement that the marker editor shows the selected marker's current
  values, also after changes made elsewhere.

## Out of Scope / Deferred

- Marker shortcuts, undo and importing markers: the new marker editor rule is in place for them, but
  none of them is built here.
- F5 (hand markers to Resolve) and F1/F2 (release and FFmpeg) stay open; unrelated.
- Keeping the gallery's window position and size across a restart: it opens maximized, as it does
  from `gallery.bat`. Not a follow-up candidate unless it bothers in practice.

## Resolves

- F3
- F6

## Impact

- Gallery window and its file watcher; the README's gallery section.
- Marker editor in the side panel.
- New tests for telling a gallery-window save from a story save, the load check before a restart,
  and the marker editor following outside changes.
- No new dependencies.
