# clip-marking Specification

## Purpose

Defines how markers on a recording become clips: markers are interesting moments, and a clip is the
stretch of recording kept around them, suggested automatically or set by hand.

## Requirements

### Requirement: A marker without a clip window is a bookmark
A marker SHALL either be a bookmark, shown as a flag on the timeline with no clip around it, or have
a clip window around it. Bookmarks produce no clip.

#### Scenario: Bookmarks only
- **WHEN** a recording has markers and none has a clip window
- **THEN** the timeline shows a flag for each marker, no clip windows, and the summary bar shows
  0 clips

### Requirement: Auto-handles suggest clip windows
The user SHALL be able to turn auto-handles on or off and set how many seconds before and after a
marker they cover. While on, every marker without a hand-set window SHALL get a suggested window from
that many seconds before to that many seconds after the marker. Auto-handles SHALL start on, with
20 seconds before and 5 seconds after.

#### Scenario: Turning auto-handles on
- **WHEN** auto-handles are turned on with 20 seconds before and 5 seconds after
- **THEN** a marker at 00:11:40 that had no window gets a window from 00:11:20 to 00:11:45

#### Scenario: Changing the handle lengths
- **WHEN** auto-handles are on and the user changes "before" from 20 to 30 seconds
- **THEN** every suggested window grows to start 30 seconds before its marker, and hand-set windows
  stay as they were

#### Scenario: Turning auto-handles off
- **WHEN** auto-handles are turned off
- **THEN** suggested windows are removed so those markers become bookmarks again, and hand-set
  windows stay

### Requirement: Hand-set windows are never overwritten
Once the user has changed a clip window by hand, auto-handle changes SHALL NOT alter it.

#### Scenario: Hand-set window survives
- **WHEN** the user drags a suggested window's end to 00:12:05 and then changes the handle lengths
- **THEN** that window still ends at 00:12:05

### Requirement: Clip window edges can be dragged
The user SHALL be able to drag the start or end of a clip window on the detail timeline. A dragged
window becomes hand-set. A window's start SHALL NOT be dragged past its marker, and its end SHALL NOT
be dragged before its marker.

#### Scenario: Dragging an edge
- **WHEN** the user drags a window's start from 00:11:20 to 00:11:10
- **THEN** the window starts at 00:11:10 and the summary bar's total length grows by 10 seconds

#### Scenario: Edge stops at the marker
- **WHEN** the user drags a window's start past its own marker
- **THEN** the start stops at the marker

### Requirement: Overlapping windows merge into one clip
Clip windows that overlap or touch SHALL form a single clip, shown as one block on the timeline and
counted once in the summary bar.

#### Scenario: Two close markers
- **WHEN** markers at 00:11:40 and 00:11:50 each have a window of 20 seconds before and 5 seconds after
- **THEN** the timeline shows one clip from 00:11:20 to 00:11:55 and the summary bar counts it as one
  clip

### Requirement: Windows stay inside the recording
A clip window SHALL NOT start before the recording's start or end after its end; a window that would
reach past an edge SHALL stop at that edge.

#### Scenario: Marker near the start
- **WHEN** auto-handles are 20 seconds before and a marker sits at 00:00:05
- **THEN** its window starts at 00:00:00

### Requirement: Clips stay in recording order
Clips SHALL always be listed, counted and exported in the order they occur in the recording; there is
no reordering.

#### Scenario: Order follows the recording
- **WHEN** a marker earlier than all existing clips gets a window
- **THEN** that clip becomes the first clip in the export list

### Requirement: Summary of what will be kept
The summary bar SHALL show the number of clips and their total length, and SHALL update as soon as a
window changes.

#### Scenario: Summary updates
- **WHEN** a window is added, removed, merged or resized
- **THEN** the clip count and total length in the summary bar change to match

### Requirement: Side panels fold away
The marker editor and the auto-handle settings SHALL each be foldable to a single header line, and
clicking a header SHALL fold or open that panel. The marker list SHALL NOT fold, and SHALL take the
height the folded panels give up.

#### Scenario: Folding the auto-handle settings
- **WHEN** the auto-handle settings are open and the user clicks their header
- **THEN** only the header stays visible and the marker list grows taller by the height the settings
  used

#### Scenario: Opening a folded panel
- **WHEN** a panel is folded and the user clicks its header
- **THEN** the panel opens and its controls work as before

#### Scenario: Folding leaves the video alone
- **WHEN** the user folds or opens either panel
- **THEN** the video area keeps its size, and the main window asks for the same height either way

### Requirement: A folded header shows the panel's current state
A panel's header SHALL show its current state whether the panel is folded or open, and SHALL update as
soon as that state changes. The auto-handle header SHALL show "On" with the seconds before and after
(for example "On, 20 s / 5 s"), or "Off". The marker editor header SHALL show the selected marker's
name and time, "Unnamed" with the time for a marker without a name, or "No marker selected".

#### Scenario: Auto-handle header
- **WHEN** auto-handles are on with 20 seconds before and 5 seconds after and the settings are folded
- **THEN** the header reads "On, 20 s / 5 s"

#### Scenario: Header follows a change
- **WHEN** the auto-handle settings are folded and auto-handles are turned off elsewhere, or the user
  changes "before" to 30 seconds
- **THEN** the header reads "Off", or "On, 30 s / 5 s", without opening the panel

#### Scenario: Marker editor header
- **WHEN** the marker "Ambush" at 00:11:40 is selected and the user renames it to "Ambush and push"
- **THEN** the marker editor header shows "Ambush and push" and 00:11:40

#### Scenario: Unnamed marker
- **WHEN** a marker without a name at 00:27:05 is selected
- **THEN** the marker editor header shows "Unnamed" and 00:27:05

### Requirement: The marker editor folds only by hand
Selecting a marker or clearing the selection SHALL NOT open or fold the marker editor; only clicking
its header SHALL. Its header SHALL follow the selection whether the editor is folded or open. When the
editor is open with no marker selected, it SHALL show a hint to select a marker.

#### Scenario: Selecting keeps a folded editor folded
- **WHEN** the user folds the marker editor while "Ambush" is selected and then selects "Breach"
- **THEN** the marker editor stays folded and its header shows "Breach" and 00:03:12

#### Scenario: Selecting keeps an open editor open
- **WHEN** the marker editor is open on "Ambush" and the user selects "Breach"
- **THEN** the marker editor stays open and shows Breach's name, color and note

#### Scenario: Clearing the selection
- **WHEN** the marker editor is open and the selection is cleared
- **THEN** the marker editor stays open, shows the hint to select a marker, and its header reads
  "No marker selected"

#### Scenario: Opening with nothing selected
- **WHEN** no marker is selected and the user clicks the folded marker editor's header
- **THEN** the marker editor opens on the hint to select a marker

### Requirement: A marker's color is picked from a flyout
The marker editor SHALL show the selected marker's color as a single dot after its name field, named
on hover. Clicking the dot SHALL open a flyout with every marker color, the current one marked and each
named on hover. Picking a color SHALL apply it to the marker and close the flyout. Pressing Esc or
clicking outside SHALL close the flyout without changing the color.

#### Scenario: Picking a color
- **WHEN** "Ambush" is Yellow and the user clicks its color dot and picks Red
- **THEN** the flyout closes, the dot shows Red, and Ambush shows Red in the marker list and on the
  timeline

#### Scenario: Current color is marked
- **WHEN** the user opens the flyout for a Yellow marker
- **THEN** Yellow is marked as the current color among all 16

#### Scenario: Closing without picking
- **WHEN** the user opens the flyout and presses Esc
- **THEN** the flyout closes and the marker keeps its color

### Requirement: Selecting a marker goes to it
Selecting a marker, in the marker list or on the timeline, SHALL move the playhead to the marker's
time. If the marker is outside the part of the recording the detail timeline shows, the detail
timeline SHALL bring it into view, centered on it unless that would show time before the start or
after the end of the recording, in which case the view stops at that end; if it is already in view,
the detail timeline SHALL NOT scroll.

#### Scenario: Marker out of view
- **WHEN** the detail timeline shows 00:08:00 to 00:16:00 and the user selects "Breach" at 00:03:12 in
  the marker list
- **THEN** the detail timeline shows 00:00:00 to 00:08:00, with 00:03:12 in view (centering would start
  before the recording), and the overview's visible-range box moves with it

#### Scenario: Marker out of view, mid-recording
- **WHEN** the detail timeline shows 00:08:00 to 00:16:00 and the user selects the unnamed marker at
  00:27:05
- **THEN** the detail timeline centers on 00:27:05

#### Scenario: Marker already in view
- **WHEN** the detail timeline shows 00:08:00 to 00:16:00 and the user selects "Ambush" at 00:11:40
- **THEN** the detail timeline does not scroll

#### Scenario: Playhead follows
- **WHEN** the user selects "Ambush" at 00:11:40
- **THEN** the playhead line sits on 00:11:40 and the transport readout shows 00:11:40

### Requirement: Side panels start in a fixed state
When the main window opens, the auto-handle settings SHALL be folded, and the marker editor SHALL be
open if a marker is selected and folded otherwise. Which panels were folded SHALL NOT be remembered
between sessions.

#### Scenario: Opening the main window
- **WHEN** the main window opens with no marker selected
- **THEN** both the marker editor and the auto-handle settings are folded and the marker list fills the
  rest of the side panel
