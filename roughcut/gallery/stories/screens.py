from roughcut.gallery import fixtures
from roughcut.gallery.fixtures import at
from roughcut.gallery.registry import story
from roughcut.ui.main_window import MainWindow
from roughcut.ui.session import Session


def _loaded():
    session = Session(fixtures.raid_night(), playhead_ms=at(0, 11, 40))
    session.select_marker(2)
    window = MainWindow(session)
    window.timeline.set_visible_range(at(0, 8, 0), at(0, 16, 0))
    return window


@story("Screens", "Main", "empty")
def main_empty():
    return MainWindow(Session(fixtures.empty_recording()))


@story("Screens", "Main", "loaded")
def main_loaded():
    return _loaded()


@story("Screens", "Main", "export dialog over main")
def main_export():
    window = _loaded()
    window.open_export()
    return window
