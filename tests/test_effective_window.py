import unittest

from roughcut.model.recording import HandleSettings, Marker, Window, effective_window


def at(minutes, seconds):
    return (minutes * 60 + seconds) * 1000


class HandleDefaultsTest(unittest.TestCase):
    def test_handles_start_on_with_20_before_and_5_after(self):
        handles = HandleSettings()
        self.assertTrue(handles.enabled)
        self.assertEqual(handles.before_ms, 20_000)
        self.assertEqual(handles.after_ms, 5_000)


class EffectiveWindowTest(unittest.TestCase):
    def test_marker_is_a_bookmark_when_handles_are_off_and_no_window_is_set(self):
        marker = Marker(id=1, time_ms=at(11, 40))
        self.assertIsNone(effective_window(marker, HandleSettings(enabled=False)))

    def test_handles_suggest_a_window_around_the_marker(self):
        marker = Marker(id=1, time_ms=at(11, 40))
        window = effective_window(marker, HandleSettings())
        self.assertEqual(window, Window(at(11, 20), at(11, 45)))

    def test_suggestion_follows_changed_handle_lengths(self):
        marker = Marker(id=1, time_ms=at(11, 40))
        window = effective_window(marker, HandleSettings(before_ms=30_000))
        self.assertEqual(window.start_ms, at(11, 10))

    def test_hand_set_window_wins_over_handles(self):
        marker = Marker(id=1, time_ms=at(11, 40), window=Window(at(11, 30), at(12, 5)))
        self.assertEqual(effective_window(marker, HandleSettings()), Window(at(11, 30), at(12, 5)))

    def test_hand_set_window_stays_when_handles_are_off(self):
        marker = Marker(id=1, time_ms=at(11, 40), window=Window(at(11, 30), at(12, 5)))
        window = effective_window(marker, HandleSettings(enabled=False))
        self.assertEqual(window, Window(at(11, 30), at(12, 5)))


if __name__ == "__main__":
    unittest.main()
