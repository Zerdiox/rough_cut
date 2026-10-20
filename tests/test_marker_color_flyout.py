import unittest

import qt
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest

from roughcut.gallery import fixtures
from roughcut.ui import theme
from roughcut.ui.markers import ColorChoice, MarkerEditor
from roughcut.ui.session import Session


class MarkerColorFlyoutTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = qt.app()

    def setUp(self):
        self.session = Session(fixtures.raid_night())
        self.session.select_marker(2)  # Ambush, Yellow
        self.editor = MarkerEditor(self.session)
        self.editor.show()

    def tearDown(self):
        if self.editor.flyout is not None:
            self.editor.flyout.close()
        self.editor.close()

    def choices(self):
        return self.editor.flyout.findChildren(ColorChoice)

    def test_one_dot_named_on_hover_and_no_grid(self):
        self.assertEqual(self.editor.color.color_name, "Yellow")
        self.assertEqual(self.editor.color.toolTip(), "Yellow")
        self.assertEqual(self.editor.findChildren(ColorChoice), [self.editor.color])

    def test_dot_sits_after_the_name_field(self):
        self.assertEqual(self.editor.color.parent(), self.editor.name.parent())
        self.assertGreater(self.editor.color.x(), self.editor.name.x())

    def test_clicking_the_dot_opens_every_color_with_the_current_one_checked(self):
        self.editor.color.click()
        self.assertTrue(self.editor.flyout.isVisible())
        choices = self.choices()
        self.assertEqual([c.color_name for c in choices], list(theme.MARKER_COLORS))
        self.assertEqual([c.color_name for c in choices if c.isChecked()], ["Yellow"])
        self.assertEqual({c.toolTip() for c in choices}, set(theme.MARKER_COLORS))

    def test_picking_a_color_applies_it_and_closes(self):
        changes = []
        self.session.changed.connect(lambda: changes.append(True))
        self.editor.color.click()
        flyout = self.editor.flyout
        next(c for c in self.choices() if c.color_name == "Red").click()
        self.assertEqual(self.session.recording.marker(2).color, "Red")
        self.assertEqual(changes, [True])
        self.assertFalse(flyout.isVisible())
        self.assertIsNone(self.editor.flyout)
        self.assertEqual(self.editor.color.color_name, "Red")
        self.assertEqual(self.editor.color.toolTip(), "Red")

    def test_escape_closes_without_changing_the_color(self):
        self.editor.color.click()
        flyout = self.editor.flyout
        QTest.keyClick(flyout, Qt.Key.Key_Escape)
        self.assertFalse(flyout.isVisible())
        self.assertIsNone(self.editor.flyout)
        self.assertEqual(self.session.recording.marker(2).color, "Yellow")
        self.assertEqual(self.editor.color.color_name, "Yellow")

    def test_dot_follows_the_selection(self):
        self.session.select_marker(1)  # Breach, Red
        self.assertEqual(self.editor.color.color_name, "Red")


if __name__ == "__main__":
    unittest.main()
