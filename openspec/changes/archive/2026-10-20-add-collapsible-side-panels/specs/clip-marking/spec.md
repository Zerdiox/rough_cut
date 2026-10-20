# Spec Delta

## ADDED Requirements

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
