# Design

## Context

The side panel stacks three widgets on one fixed-width column: the marker list (the only one with a
stretch factor), the marker editor and the auto-handle settings, separated by dividers. Every widget
reads from the editing session and repaints on its `changed` and `selectionChanged` signals; widgets
never talk to each other. The marker editor already switches between a hint ("Select a marker…") and
its fields based on the selection.

## Goals / Non-Goals

**Goals:**
- One reusable fold container used by both panels, so they look and behave the same.
- The fold rules (start state, folding only by hand) live where they can be unit-tested
  without clicking through a window.

**Non-Goals:**
- Fold animation. A plain show/hide is enough and keeps layout predictable.
- Changing what the open panels contain or how they edit the session.

## Decisions

### A small fold container instead of QFluentWidgets' expander cards
A `FoldPanel` widget: a clickable header row (chevron, title, state text) above a body widget that is
shown or hidden. The existing `MarkerEditor` and `HandleSettingsPanel` become its bodies unchanged.

Alternative: `ExpandSettingCard` / `ExpandGroupSettingCard`. They are built as settings-page cards: a
scroll area that sets fixed heights from the content at expand time, an icon slot, card background and
border, and an animation. The marker editor's height changes with the selection (hint vs. fields),
which a fixed-height card would clip, and the card styling doesn't match the rest of the side panel.
The chevron icons (`FluentIcon.CHEVRON_RIGHT_MED` / `CHEVRON_DOWN_MED`) and Fluent labels give the
same look without those constraints.

### State text comes from the session, not from the body
Each fold panel gets a small function that turns the session into its header text, and refreshes it on
`changed` and `selectionChanged`. The text functions are plain functions (session in, string out), so
"On, 20 s / 5 s", "Off", "Unnamed 00:07:40" and "No marker selected" are tested without Qt widgets.
The marker time uses the existing time format the marker list and editor already use.

### The marker editor folds only by hand
The marker editor's fold panel is a plain fold panel: only a header click opens or folds it. Selection
changes refresh its header (and the editor's fields) but never its fold state. An earlier version
opened the editor on every new selection and folded it when the selection was cleared; in the gallery
that felt intrusive, because a fold Azzey chose was undone by the next click in the list.

With no marker selected, clicking the folded header still opens the editor, showing its existing hint.
That explains the panel instead of making the header look broken.

### Start state set by the main window
The fold panel takes its starting state as a constructor argument. The main window creates the
auto-handle panel folded and the marker editor in whatever state the selection implies. Nothing is read
from or written to disk.

### The video area has a preferred size
The video area had only a minimum size, so the upper row's natural height came from the side panel:
folding both panels made the whole main window ask for less height, and a window shown at its
preferred size (the gallery stage, or the app opening on an empty recording) shrank the video. The
video area now has a 16:9 preferred size, so the main window's preferred height no longer depends on
which panels are folded, and the folded height goes to the marker list only. The marker list asks for no more
than its minimum height, since it is the stretch item, so the side panel never outgrows the video.

### Marker color in a Flyout, not a dialog or a custom popup
The dot is a small button after the name field that opens a QFluentWidgets `Flyout` anchored to it,
holding the existing 16 color buttons in the same 8x2 grid. The flyout closes itself on outside click
and Esc, so "close without picking" needs no code. Picking a color goes through `update_marker` as
today and then closes the flyout.

Alternatives: `ColorDialog` / `ColorPickerButton` pick any RGB color in a large modal, while markers
use a fixed set of named colors with a light and a dark value each; free colors would lose the names,
the dark-theme variant and the gallery's named swatches. A dialog of large named swatches was also
considered; it is clearer but modal, and slower for repeated marking. A hand-made popup would re-do
the focus, outside-click and Esc handling Flyout already has.

### Going to the selected marker
The session gets a `set_playhead` editing call with its own `playheadChanged` signal rather than
`changed`: once playback exists the playhead moves many times a second, and `changed` rebuilds the
marker list and recomputes clips. The detail timeline and transport bar repaint on `playheadChanged`.

On `selectionChanged`, the session moves the playhead to the selected marker (selection and playhead
are both session state, so widgets stay unaware of each other). The detail timeline, also on
`selectionChanged`, calls its existing `center_on` only when the marker lies outside its visible
range. `center_on` keeps the range inside the recording, so a marker near either end lands in view
but off-center. Clicking a flag on the timeline selects a marker that is by definition in view, so
the strip never jumps under the cursor. Clearing the selection leaves the playhead where it is.

Alternative: always center. Predictable, but the view jumps on every click even when the marker was
already visible, which is disorienting while working through nearby markers.

### Dividers stay between panels
The dividers between the list and the two fold panels remain, so a folded header still reads as its own
section.

## Risks / Trade-offs

- [The flyout is its own top-level window] → Offscreen tests check that it opens, applies and closes,
  not how it looks; its position next to the side panel is a manual check.
- [The 330 px side panel is narrow for title plus state text] → Short titles ("Marker",
  "Suggest clips") and the state text elides on the right if it doesn't fit; checked in the gallery at
  both themes.
- [`SecondsBox` places its text field by hand after layout passes] → It already re-places on
  `showEvent`, so showing the auto-handle body after a fold keeps the numbers visible; covered by a
  manual check.
