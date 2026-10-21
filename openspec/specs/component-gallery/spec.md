# component-gallery Specification

## Purpose

Lets Kenny and Azzey look at every piece of RoughCut's interface on its own, in each of its states,
with made-up recordings, so the layout and look can be agreed before the real editor exists.

## Requirements

### Requirement: Gallery opens without a terminal
The gallery SHALL open from a double-clickable launcher on Windows, without typing commands and
without a real recording.

#### Scenario: Launching the gallery
- **WHEN** the user double-clicks the gallery launcher
- **THEN** the gallery window opens showing the story list and the first story

### Requirement: Stories are grouped and browsable
The gallery SHALL list its stories in a sidebar grouped as Foundations, Components and Screens, with
each component's states listed under it, and SHALL show the selected story in the main area.

#### Scenario: Picking a story
- **WHEN** the user clicks "Timeline" then its "merged windows" state in the sidebar
- **THEN** the main area shows the timeline with overlapping clip windows drawn as one clip

#### Scenario: Every story opens
- **WHEN** the user opens any story in the list
- **THEN** it is shown without an error, using only made-up recordings and markers

### Requirement: Foundations are visible as stories
The gallery SHALL include stories for the color palette, the type scale and the full set of marker
colors, each labelled with its name.

#### Scenario: Marker colors
- **WHEN** the user opens the marker colors story
- **THEN** every marker color available in RoughCut is shown as a swatch with its name

### Requirement: Light and dark theme
The gallery SHALL let the user switch between light and dark theme at any time, and the shown story
SHALL follow the switch immediately.

#### Scenario: Switching to dark
- **WHEN** the user switches the theme to dark while a story is shown
- **THEN** the story and the gallery redraw in the dark theme without losing the selected story

### Requirement: Saved changes appear without restarting
When a source file of RoughCut's interface, or of the gallery window itself, is saved while the
gallery is open, the gallery SHALL show the change without the user restarting it, keeping the
selected story and theme.

#### Scenario: Editing a component
- **WHEN** a component's file is changed and saved while its story is shown
- **THEN** the story redraws with the change within a couple of seconds, on the same story and theme

#### Scenario: Saving a broken file
- **WHEN** a saved change makes the story fail to build
- **THEN** the main area shows the error message instead of the story and the gallery stays open;
  the story returns once the file is fixed and saved again

#### Scenario: Editing the gallery window
- **WHEN** one of the gallery window's own files is changed and saved while the dark theme and the
  "Main (loaded)" story are shown
- **THEN** within a few seconds the gallery shows the change, on "Main (loaded)" in the dark theme,
  without the user starting it again

#### Scenario: Saving a broken gallery window file
- **WHEN** a saved change to one of the gallery window's own files makes the gallery fail to load
- **THEN** the main area shows the error message and the gallery stays open on its previous version;
  once the file is fixed and saved again, the gallery shows the change on the same story and theme

### Requirement: Screens show the full window
The gallery SHALL include screen stories that show the complete RoughCut main window, empty and with a
recording loaded, and the export dialog over it, with a placeholder where the video will play.

#### Scenario: Loaded main window
- **WHEN** the user opens the "Main (loaded)" screen story
- **THEN** the main window shows the viewer placeholder, marker list and editor, auto-handle settings,
  transport bar, overview and detail timeline, and summary bar with Export, filled with a made-up
  recording
