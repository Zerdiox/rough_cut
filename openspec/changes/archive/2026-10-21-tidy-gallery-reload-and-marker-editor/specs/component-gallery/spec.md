# Spec Delta

## MODIFIED Requirements

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
