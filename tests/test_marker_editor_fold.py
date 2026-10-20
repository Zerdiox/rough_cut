import unittest

import qt
from roughcut.gallery import fixtures
from roughcut.gallery.fixtures import at
from roughcut.ui.markers import marker_editor_panel
from roughcut.ui.session import Session


class MarkerEditorFoldTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = qt.app()

    def setUp(self):
        self.session = Session(fixtures.raid_night())
        self.panel = marker_editor_panel(self.session)

    def test_folded_with_nothing_selected(self):
        self.assertFalse(self.panel.is_open())

    def test_open_when_built_with_a_selection(self):
        self.session.select_marker(2)
        self.assertTrue(marker_editor_panel(self.session).is_open())

    def test_selecting_keeps_a_folded_editor_folded(self):
        self.session.select_marker(2)
        self.assertFalse(self.panel.is_open())
        self.assertEqual(self.panel.header.state, "Ambush · 00:11:40")

    def test_selecting_keeps_a_fold_by_hand(self):
        self.session.select_marker(2)
        self.panel.header.click()
        self.panel.header.click()
        self.assertFalse(self.panel.is_open())
        self.session.select_marker(1)
        self.assertFalse(self.panel.is_open())
        self.assertEqual(self.panel.header.state, "Breach · 00:03:12")

    def test_selecting_keeps_an_open_editor_open_on_the_new_marker(self):
        self.session.select_marker(2)
        self.panel.header.click()
        self.session.select_marker(1)
        self.assertTrue(self.panel.is_open())
        self.assertEqual(self.panel.body.name.text(), "Breach")

    def test_a_fold_holds_while_editing(self):
        panel = marker_editor_panel(self.session)
        self.session.select_marker(2)
        self.session.update_marker(2, name="Ambush and push")
        clip = self.session.clips()[0]
        self.session.drag_edge(clip, "start", clip.start_ms - at(0, 0, 10))
        self.assertFalse(panel.is_open())

    def test_clearing_the_selection_keeps_it_open_on_the_hint(self):
        self.session.select_marker(2)
        self.panel.header.click()
        self.session.select_marker(None)
        self.assertTrue(self.panel.is_open())
        self.assertEqual(self.panel.header.state, "No marker selected")
        self.assertFalse(self.panel.body.nothing.isHidden())
        self.assertTrue(self.panel.body.fields.isHidden())

    def test_opening_with_nothing_selected_shows_the_hint(self):
        self.panel.header.click()
        self.assertTrue(self.panel.is_open())
        editor = self.panel.body
        self.assertFalse(editor.nothing.isHidden())
        self.assertTrue(editor.fields.isHidden())


if __name__ == "__main__":
    unittest.main()
