import unittest

from PySide6.QtWidgets import QWidget

import qt
from roughcut.gallery import fixtures
from roughcut.ui.fold_panel import FoldPanel
from roughcut.ui.markers import handles_summary, marker_summary
from roughcut.ui.session import Session


class FoldPanelTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = qt.app()

    def setUp(self):
        self.session = Session(fixtures.raid_night())

    def panel(self, summary=handles_summary, folded=False):
        return FoldPanel("Suggest clips", QWidget(), self.session, summary, folded=folded)

    def test_starts_open(self):
        panel = self.panel()
        self.assertTrue(panel.is_open())
        self.assertFalse(panel.body.isHidden())

    def test_starts_folded(self):
        panel = self.panel(folded=True)
        self.assertFalse(panel.is_open())
        self.assertTrue(panel.body.isHidden())
        self.assertFalse(panel.header.isHidden())

    def test_clicking_the_header_toggles_the_body(self):
        panel = self.panel(folded=True)
        panel.header.click()
        self.assertFalse(panel.body.isHidden())
        panel.header.click()
        self.assertTrue(panel.body.isHidden())

    def test_header_shows_title_and_state(self):
        panel = self.panel()
        self.assertEqual(panel.header.title, "Suggest clips")
        self.assertEqual(panel.header.state, "On, 20 s / 5 s")

    def test_state_follows_changed(self):
        panel = self.panel(folded=True)
        self.session.set_handles_enabled(False)
        self.assertEqual(panel.header.state, "Off")
        self.assertFalse(panel.is_open())

    def test_state_follows_selection_changed(self):
        panel = self.panel(summary=marker_summary)
        self.session.select_marker(2)
        self.assertEqual(panel.header.state, "Ambush · 00:11:40")


if __name__ == "__main__":
    unittest.main()
