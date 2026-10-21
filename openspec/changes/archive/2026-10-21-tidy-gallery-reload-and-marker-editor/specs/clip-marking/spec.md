# Spec Delta

## ADDED Requirements

### Requirement: The marker editor shows the marker as it is
The marker editor SHALL show the selected marker's current name, color and note, and SHALL update as
soon as any of them changes, also when the change is made somewhere other than the marker editor.
Updating SHALL NOT reset the text or cursor of the field the user is typing in.

#### Scenario: A change made elsewhere
- **WHEN** "Ambush" is selected and its name changes to "Ambush and push" and its color to Red
  somewhere other than the marker editor
- **THEN** the marker editor shows "Ambush and push" and a Red color dot without reselecting the
  marker

#### Scenario: Typing is not disturbed
- **WHEN** the user types in the middle of the selected marker's name in the marker editor
- **THEN** each character appears where the cursor is and the cursor stays after it
