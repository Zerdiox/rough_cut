import unittest

import qt
from roughcut.gallery import fixtures
from roughcut.ui.main_window import MainWindow
from roughcut.ui.session import Session


class MainWindowSidePanelTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = qt.app()

    def window(self, selected=None):
        session = Session(fixtures.raid_night())
        if selected is not None:
            session.select_marker(selected)
        window = MainWindow(session)
        window.resize(1440, 900)
        window.show()
        self.settle()
        self.addCleanup(window.close)
        return window

    def settle(self):
        # A folded body relayouts the fold panel first and the side panel on a later pass.
        for _ in range(3):
            self.app.processEvents()

    def test_auto_handle_settings_start_folded(self):
        self.assertFalse(self.window().handles_panel.is_open())

    def test_marker_editor_folded_without_a_selection(self):
        self.assertFalse(self.window().marker_panel.is_open())

    def test_marker_editor_open_with_a_selection(self):
        self.assertTrue(self.window(selected=2).marker_panel.is_open())

    def test_marker_list_grows_when_a_panel_folds(self):
        window = self.window(selected=2)
        window.handles_panel.set_open(True)
        self.settle()
        open_height = window.marker_list.height()
        window.handles_panel.set_open(False)
        window.marker_panel.set_open(False)
        self.settle()
        self.assertGreater(window.marker_list.height(), open_height)
        self.assertTrue(window.marker_list.isVisible())

    def test_folding_leaves_the_preferred_height_alone(self):
        # The gallery, and a window opened at its preferred size, size the
        # screen by its size hint; folding must not shrink it (and the video).
        window = self.window(selected=2)
        window.handles_panel.set_open(True)
        self.settle()
        open_hint = window.sizeHint().height()
        window.handles_panel.set_open(False)
        window.marker_panel.set_open(False)
        self.settle()
        self.assertEqual(window.sizeHint().height(), open_hint)


if __name__ == "__main__":
    unittest.main()
