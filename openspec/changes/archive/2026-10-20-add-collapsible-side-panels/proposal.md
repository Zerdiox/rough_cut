# Proposal

## Why

The side panel is the tallest part of the main window: the marker editor and the auto-handle
settings have a fixed height, so on a 1440x900 screen the marker list, the one part Azzey scrolls
through, shrinks to about two rows. Playback will add more controls below, so the room only gets
tighter. Letting the two fixed panels fold away gives that room back to the marker list.

## What Changes

- The **marker editor** and the **auto-handle settings** can each be folded to a one-line header and
  opened again by clicking it.
- A folded panel's header still shows its current state, so folding never hides what the app is doing:
  - Marker editor: the selected marker's name (or "Unnamed") and time, or "No marker selected".
  - Auto-handle settings: "On, 20 s / 5 s" with the current lengths, or "Off".
  Headers update as soon as the values change.
- The marker editor opens and folds only when Azzey clicks its header; selecting or clearing a marker
  never opens or folds it. Its header follows the selection either way.
- Folding a panel never changes the size of the video area; only the marker list grows.
- The marker editor's always-visible grid of 16 colors is replaced by a single color dot after the
  name field. Clicking it opens a small flyout with the 16 marker colors, the current one ringed and
  each named on hover. Picking a color applies it and closes the flyout; Esc or clicking elsewhere
  closes it unchanged. The open editor gets two rows shorter.
- Selecting a marker goes to it: the playhead moves to the marker, and the detail timeline brings it
  into view, centered where the recording allows, when the marker is outside the part of the
  recording it shows. A marker already in view leaves the timeline where it is.
- The auto-handle settings start folded and only open or fold when Azzey clicks the header.
- The marker list never folds; it takes whatever height the folded panels give up.
- Gallery stories for the folded and open states of both panels, and the main screen with both
  folded.

## Capabilities

### New Capabilities
<!-- None. -->

### Modified Capabilities
- `clip-marking`: adds requirements for folding the marker editor and auto-handle settings, what a
  folded header shows, that the marker editor folds only by hand, how selecting a marker moves
  the playhead and timeline to it, and how a marker's color is picked.

## Out of Scope / Deferred

- F3 (gallery shell not hot-reloaded) is in the same area but unrelated, and stays open.
- F5 (hand markers to Resolve): the color flyout keeps Resolve's 16 named marker colors, which keeps
  that open, but exporting markers is not part of this change.
- Candidates for Kenny to approve as follow-ups:
  - Remember which panels are folded between sessions. Nothing is saved between sessions yet, the
    marker editor is driven by the selection, and the auto-handle header shows its values, so a
    fixed starting state is enough for now.
  - Lower the main window's minimum height now that the side panel can be shorter. Worth deciding
    after seeing the folded panels in the gallery.

## Resolves

- F4

## Impact

- Side panel code (marker editor and its color picker, auto-handle settings) and the main window's
  side panel layout.
- The editing session gains a way to move the playhead; the detail timeline and transport readout
  follow it.
- Gallery stories for the two panels and the main screen; tests for the fold rules and headers.
- No new dependencies; the fold header and the color flyout use widgets QFluentWidgets already
  provides.
