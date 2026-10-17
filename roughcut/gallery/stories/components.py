from PySide6.QtWidgets import QVBoxLayout, QWidget

from roughcut.gallery import fixtures
from roughcut.gallery.fixtures import at
from roughcut.gallery.registry import story
from roughcut.model.recording import HandleSettings
from roughcut.ui.export_dialog import ExportPanel
from roughcut.ui.markers import HandleSettingsPanel, MarkerEditor, MarkerList
from roughcut.ui.session import Session
from roughcut.ui.summary_bar import SummaryBar
from roughcut.ui.transport_bar import TransportBar


def _sized(widget, width, height=None):
    """Stories show a component at roughly the size it gets in the main window."""
    holder = QWidget()
    layout = QVBoxLayout(holder)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.addWidget(widget)
    widget.setFixedWidth(width)
    if height:
        widget.setFixedHeight(height)
    return holder


# Marker list

@story("Components", "Marker list", "empty")
def marker_list_empty():
    return _sized(MarkerList(Session(fixtures.empty_recording())), 320, 360)


@story("Components", "Marker list", "few markers")
def marker_list_few():
    return _sized(MarkerList(Session(fixtures.raid_night_hand_set(), HandleSettings(enabled=False))), 320, 360)


@story("Components", "Marker list", "40+ markers")
def marker_list_many():
    return _sized(MarkerList(Session(fixtures.many_markers())), 320, 360)


@story("Components", "Marker list", "one selected")
def marker_list_selected():
    session = Session(fixtures.raid_night())
    session.select_marker(2)
    return _sized(MarkerList(session), 320, 360)


# Marker editor

@story("Components", "Marker editor", "nothing selected")
def marker_editor_nothing():
    return _sized(MarkerEditor(Session(fixtures.raid_night())), 320)


@story("Components", "Marker editor", "marker selected")
def marker_editor_selected():
    session = Session(fixtures.raid_night())
    session.select_marker(1)
    return _sized(MarkerEditor(session), 320)


@story("Components", "Marker editor", "unnamed marker")
def marker_editor_unnamed():
    session = Session(fixtures.raid_night())
    session.select_marker(4)
    return _sized(MarkerEditor(session), 320)


# Auto-handle settings

@story("Components", "Auto-handle settings", "on, 20 s before, 5 s after")
def handles_on():
    return _sized(HandleSettingsPanel(Session(fixtures.raid_night())), 320)


@story("Components", "Auto-handle settings", "off")
def handles_off():
    return _sized(HandleSettingsPanel(Session(fixtures.raid_night(), HandleSettings(enabled=False))), 320)


# Transport bar

@story("Components", "Transport bar", "at a marker")
def transport():
    return _sized(TransportBar(Session(fixtures.raid_night(), playhead_ms=at(0, 11, 40))), 1000)


# Summary bar

@story("Components", "Summary bar", "0 clips")
def summary_none():
    return _sized(SummaryBar(Session(fixtures.raid_night(), HandleSettings(enabled=False))), 1000)


@story("Components", "Summary bar", "3 clips")
def summary_three():
    recording = fixtures.raid_night()
    recording.markers = [m for m in recording.markers if m.id in (1, 2, 6)]
    return _sized(SummaryBar(Session(recording)), 1000)


# Export dialog

def _export(*renames):
    session = Session(fixtures.raid_night())
    clips = session.clips()
    for index, name in renames:
        session.rename_clip(clips[index], name)
    return _sized(ExportPanel(session), 680)


@story("Components", "Export dialog", "all valid")
def export_valid():
    return _export()


@story("Components", "Export dialog", "forbidden character")
def export_forbidden():
    return _export((1, "Ambush?"))


@story("Components", "Export dialog", "duplicates")
def export_duplicates():
    return _export((3, "breach"))


@story("Components", "Export dialog", "empty name")
def export_empty():
    return _export((2, ""))


@story("Components", "Export dialog", "reserved name")
def export_reserved():
    return _export((4, "CON"))
