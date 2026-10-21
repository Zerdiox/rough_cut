import unittest

import qt
from PySide6.QtTest import QTest

from roughcut.gallery import fixtures
from roughcut.ui.markers import MarkerEditor
from roughcut.ui.session import Session


class MarkerEditorFollowsOutsideChangesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = qt.app()

    def setUp(self):
        self.session = Session(fixtures.raid_night())
        self.session.select_marker(2)  # Ambush, Yellow
        self.editor = MarkerEditor(self.session)
        self.editor.show()
        self.addCleanup(self.editor.close)

    def test_a_rename_and_color_change_elsewhere_show_up(self):
        self.session.update_marker(2, name="Ambush and push", color="Red")
        self.assertEqual(self.editor.name.text(), "Ambush and push")
        self.assertEqual(self.editor.color.color_name, "Red")
        self.assertEqual(self.editor.color.toolTip(), "Red")

    def test_a_note_change_elsewhere_shows_up(self):
        self.session.update_marker(2, note="Second squad from the left")
        self.assertEqual(self.editor.note.toPlainText(), "Second squad from the left")

    def test_typing_in_the_middle_keeps_the_cursor(self):
        self.editor.name.setFocus()
        self.editor.name.setCursorPosition(3)  # Amb|ush
        QTest.keyClicks(self.editor.name, "XY")
        self.assertEqual(self.editor.name.text(), "AmbXYush")
        self.assertEqual(self.editor.name.cursorPosition(), 5)
        self.assertEqual(self.session.recording.marker(2).name, "AmbXYush")

    def test_typing_in_the_note_keeps_the_cursor(self):
        self.editor.note.setFocus()
        QTest.keyClicks(self.editor.note, "Flank")
        self.assertEqual(self.editor.note.toPlainText(), "Flank")
        self.assertEqual(self.editor.note.textCursor().position(), 5)
        self.assertEqual(self.session.recording.marker(2).note, "Flank")


if __name__ == "__main__":
    unittest.main()
