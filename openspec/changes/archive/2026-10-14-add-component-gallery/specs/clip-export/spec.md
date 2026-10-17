# Spec Delta

## Purpose

Lets the user give each clip a name before export, since each clip becomes its own file, and stops
an export whose names can't be written as files on Windows.

## ADDED Requirements

### Requirement: Export lists every clip
The export dialog SHALL list one row per clip in recording order, showing its time range, an editable
clip name and the marker it came from (read-only), plus the folder the files will be saved to.

#### Scenario: Opening export
- **WHEN** the user clicks Export with three clips on the timeline
- **THEN** the dialog shows three rows in recording order, each with time range, name and source
  marker

### Requirement: Clip names start from the marker name
A clip's name SHALL start as its marker's name. A clip whose marker has no name SHALL start as the
recording's name followed by the clip's two-digit position (for example "raid_night_0412 03"). A
clip made from merged windows SHALL start with the name of its earliest marker.

#### Scenario: Named marker
- **WHEN** a clip comes from a marker named "Ambush"
- **THEN** its name in the export dialog starts as "Ambush"

#### Scenario: Unnamed marker
- **WHEN** the third clip of recording "raid_night_0412" comes from an unnamed marker
- **THEN** its name starts as "raid_night_0412 03"

### Requirement: Clip names are independent of marker names
Renaming a clip SHALL NOT rename its marker, and renaming a marker SHALL NOT change a clip name the
user has already edited. A clip's edited name SHALL be kept while its window is resized.

#### Scenario: Renaming a clip
- **WHEN** the user renames clip "Ambush" to "Ambush and push"
- **THEN** the marker is still named "Ambush" in the marker list

#### Scenario: Name survives a resize
- **WHEN** the user has renamed a clip and then drags its window's end
- **THEN** the clip keeps the name the user gave it

### Requirement: Unusable names block export
The dialog SHALL flag, on the row itself, any clip name that is empty, contains a character Windows
does not allow in file names (`\ / : * ? " < > |`), ends with a space or a dot, is a name Windows
reserves (such as CON, PRN, AUX, NUL, COM1, LPT1), or matches another clip's name ignoring upper and
lower case. While any name is flagged, Export SHALL be disabled and the dialog SHALL say how many
names need fixing.

#### Scenario: Forbidden character
- **WHEN** the user names a clip "Ambush?"
- **THEN** that row is flagged as containing a character Windows doesn't allow, and Export is disabled

#### Scenario: Duplicate names
- **WHEN** two clips are named "Breach" and "breach"
- **THEN** both rows are flagged as duplicates and Export is disabled

#### Scenario: Fixing the last problem
- **WHEN** the user corrects the only flagged name
- **THEN** the flag disappears and Export is enabled
