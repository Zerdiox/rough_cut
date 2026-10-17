from PySide6.QtWidgets import QVBoxLayout, QWidget
from qfluentwidgets import CaptionLabel

from roughcut.gallery import fixtures
from roughcut.gallery.fixtures import at
from roughcut.gallery.registry import story
from roughcut.model.recording import HandleSettings
from roughcut.ui.session import Session
from roughcut.ui.timeline import OverviewStrip, TimelinePanel


def _with_summary(widget, session):
    """A live line under the strip so drags show their effect on the clips."""
    from roughcut.ui.summary_bar import summary_text

    wrapper = QWidget()
    layout = QVBoxLayout(wrapper)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.addWidget(widget)
    line = CaptionLabel(summary_text(session))
    session.changed.connect(lambda: line.setText(summary_text(session)))
    layout.addWidget(line)
    wrapper.setMinimumWidth(900)
    return wrapper


def _panel(recording, handles=None, view=None, selected=None):
    session = Session(recording, handles or HandleSettings(), playhead_ms=at(0, 11, 40))
    if selected is not None:
        session.select_marker(selected)
    panel = TimelinePanel(session)
    if view:
        panel.set_visible_range(*view)
    widget = _with_summary(panel, session)
    widget.session = session
    return widget


# Overview

def _overview(recording, handles=None):
    session = Session(recording, handles or HandleSettings())
    return _with_summary(OverviewStrip(session), session)


@story("Components", "Timeline overview", "empty")
def overview_empty():
    return _overview(fixtures.empty_recording())


@story("Components", "Timeline overview", "bookmarks only")
def overview_bookmarks():
    return _overview(fixtures.raid_night(), HandleSettings(enabled=False))


@story("Components", "Timeline overview", "clips")
def overview_clips():
    return _overview(fixtures.raid_night())


@story("Components", "Timeline overview", "40+ markers")
def overview_many():
    return _overview(fixtures.many_markers())


# Detail (with its overview)

@story("Components", "Timeline", "empty")
def timeline_empty():
    return _panel(fixtures.empty_recording())


@story("Components", "Timeline", "bookmarks only")
def timeline_bookmarks():
    return _panel(fixtures.raid_night(), HandleSettings(enabled=False), view=(0, at(0, 50, 0)))


@story("Components", "Timeline", "clip windows")
def timeline_windows():
    return _panel(fixtures.raid_night_hand_set(), view=(at(0, 25, 0), at(0, 45, 0)))


@story("Components", "Timeline", "merged windows")
def timeline_merged():
    return _panel(fixtures.raid_night(), view=(at(0, 10, 30), at(0, 13, 0)), selected=2)


@story("Components", "Timeline", "handles on")
def timeline_handles_on():
    return _panel(fixtures.raid_night(), view=(0, at(0, 50, 0)))


@story("Components", "Timeline", "handles off")
def timeline_handles_off():
    return _panel(fixtures.raid_night_hand_set(), HandleSettings(enabled=False), view=(0, at(0, 50, 0)))


@story("Components", "Timeline", "clamped at edges")
def timeline_clamped():
    return _panel(fixtures.edge_markers())


@story("Components", "Timeline", "40+ markers")
def timeline_many():
    return _panel(fixtures.many_markers())


@story("Components", "Timeline", "zoomed in")
def timeline_zoomed():
    return _panel(fixtures.raid_night(), view=(at(0, 11, 0), at(0, 12, 30)), selected=3)
