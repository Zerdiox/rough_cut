import unittest

import qt
from roughcut.gallery import fixtures
from roughcut.model.recording import HandleSettings
from roughcut.ui.markers import handles_summary, marker_summary
from roughcut.ui.session import Session


class HandlesSummaryTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = qt.app()

    def test_defaults(self):
        self.assertEqual(handles_summary(Session(fixtures.raid_night())), "On, 20 s / 5 s")

    def test_follows_a_changed_length(self):
        session = Session(fixtures.raid_night())
        session.set_handle_before_ms(30_000)
        self.assertEqual(handles_summary(session), "On, 30 s / 5 s")

    def test_off(self):
        session = Session(fixtures.raid_night(), HandleSettings(enabled=False))
        self.assertEqual(handles_summary(session), "Off")


class MarkerSummaryTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = qt.app()

    def setUp(self):
        self.session = Session(fixtures.raid_night())

    def test_selected_marker(self):
        self.session.select_marker(2)
        self.assertEqual(marker_summary(self.session), "Ambush · 00:11:40")

    def test_follows_a_rename(self):
        self.session.select_marker(2)
        self.session.update_marker(2, name="Ambush and push")
        self.assertEqual(marker_summary(self.session), "Ambush and push · 00:11:40")

    def test_unnamed_marker(self):
        self.session.select_marker(4)
        self.assertEqual(marker_summary(self.session), "Unnamed · 00:27:05")

    def test_nothing_selected(self):
        self.assertEqual(marker_summary(self.session), "No marker selected")


if __name__ == "__main__":
    unittest.main()
