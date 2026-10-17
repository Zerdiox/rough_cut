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
