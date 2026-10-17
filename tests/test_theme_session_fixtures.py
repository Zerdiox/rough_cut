import re
import unittest

import qt
from roughcut.gallery import fixtures
from roughcut.model.clips import derive_clips
from roughcut.model.recording import HandleSettings
from roughcut.ui import theme

HEX = re.compile(r"^#[0-9A-F]{6}$")


class ThemeTest(unittest.TestCase):
    def test_sixteen_marker_colors_with_light_and_dark_values(self):
        self.assertEqual(len(theme.MARKER_COLORS), 16)
        for name, (light, dark) in theme.MARKER_COLORS.items():
            with self.subTest(name=name):
                self.assertTrue(name)
                self.assertRegex(light, HEX)
                self.assertRegex(dark, HEX)

    def test_every_token_has_light_and_dark_values(self):
        for name, (light, dark) in theme.TOKENS.items():
            with self.subTest(name=name):
                self.assertRegex(light, HEX)
                self.assertRegex(dark, HEX)

    def test_fixture_marker_colors_exist(self):
        for name, build in fixtures.ALL.items():
            for marker in build().markers:
                with self.subTest(fixture=name, marker=marker.id):
                    self.assertIn(marker.color, theme.MARKER_COLORS)

    def test_time_formats(self):
        self.assertEqual(theme.format_time(4_930_000), "01:22:10")
        self.assertEqual(theme.format_length(165_000), "2:45")
        self.assertEqual(theme.format_length(3_765_000), "1:02:45")


class SessionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = qt.app()

    def setUp(self):
        from roughcut.ui.session import Session

        self.session = Session(fixtures.raid_night())
        self.emitted = 0
        self.session.changed.connect(self.count)

    def count(self):
        self.emitted += 1

    def test_handle_change_emits_once(self):
        self.session.set_handle_before_ms(30_000)
        self.assertEqual(self.emitted, 1)

    def test_same_handle_value_does_not_emit(self):
        self.session.set_handles_enabled(True)
        self.assertEqual(self.emitted, 0)

    def test_edge_drag_emits_once(self):
        clip = self.session.clips()[0]
        self.session.drag_edge(clip, "start", clip.start_ms - 10_000)
        self.assertEqual(self.emitted, 1)

    def test_rename_emits_once(self):
        self.session.rename_clip(self.session.clips()[0], "Door")
        self.assertEqual(self.emitted, 1)

    def test_selection_has_its_own_signal(self):
        selected = []
        self.session.selectionChanged.connect(lambda: selected.append(self.session.selected_marker_id))
        self.session.select_marker(2)
        self.assertEqual((selected, self.emitted), ([2], 0))


class FixturesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = qt.app()

    def test_every_fixture_loads_into_a_session(self):
        from roughcut.ui.session import Session

        for name, build in fixtures.ALL.items():
            with self.subTest(fixture=name):
                session = Session(build(), HandleSettings())
                for clip in session.clips():
                    self.assertLessEqual(0, clip.start_ms)
                    self.assertLessEqual(clip.end_ms, session.recording.duration_ms)

    def test_raid_night_has_the_cases_stories_need(self):
        recording = fixtures.raid_night()
        self.assertEqual(len(recording.markers), 6)
        self.assertTrue(any(not m.name for m in recording.markers))
        clips = derive_clips(recording, HandleSettings())
        self.assertEqual(len(clips), 5)  # Ambush and Push merge

    def test_many_markers_has_forty_plus(self):
        self.assertGreaterEqual(len(fixtures.many_markers().markers), 40)


if __name__ == "__main__":
    unittest.main()
