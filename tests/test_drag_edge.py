import unittest

from roughcut.model.clips import derive_clips, drag_edge, set_window_edge
from roughcut.model.recording import HandleSettings, Marker, Recording, Window


def at(minutes, seconds):
    return (minutes * 60 + seconds) * 1000


def recording(*markers):
    return Recording(name="raid_night_0412", duration_ms=at(82, 10), markers=list(markers))


class DragEdgeTest(unittest.TestCase):
    def setUp(self):
        self.handles = HandleSettings()

    def only_clip(self, rec):
        clips = derive_clips(rec, self.handles)
        self.assertEqual(len(clips), 1)
        return clips[0]

    def test_dragging_a_suggested_window_makes_it_hand_set(self):
        rec = recording(Marker(1, at(11, 40)))
        drag_edge(rec, self.handles, self.only_clip(rec), "start", at(11, 10))
        self.assertEqual(rec.marker(1).window, Window(at(11, 10), at(11, 45)))

    def test_dragging_the_end(self):
        rec = recording(Marker(1, at(11, 40)))
        drag_edge(rec, self.handles, self.only_clip(rec), "end", at(12, 5))
        self.assertEqual(rec.marker(1).window, Window(at(11, 20), at(12, 5)))

    def test_start_stops_at_the_marker(self):
        rec = recording(Marker(1, at(11, 40)))
        drag_edge(rec, self.handles, self.only_clip(rec), "start", at(11, 55))
        self.assertEqual(rec.marker(1).window.start_ms, at(11, 40))

    def test_end_stops_at_the_marker(self):
        rec = recording(Marker(1, at(11, 40)))
        drag_edge(rec, self.handles, self.only_clip(rec), "end", at(11, 0))
        self.assertEqual(rec.marker(1).window.end_ms, at(11, 40))

    def test_edges_stop_at_the_recording(self):
        rec = recording(Marker(1, at(0, 30)), Marker(2, at(82, 0)))
        first, last = derive_clips(rec, self.handles)
        drag_edge(rec, self.handles, first, "start", -5_000)
        drag_edge(rec, self.handles, last, "end", at(90, 0))
        self.assertEqual(rec.marker(1).window.start_ms, 0)
        self.assertEqual(rec.marker(2).window.end_ms, at(82, 10))

    def test_materialised_window_is_clamped_before_moving_the_other_edge(self):
        rec = recording(Marker(1, at(0, 5)))
        drag_edge(rec, self.handles, self.only_clip(rec), "end", at(0, 20))
        self.assertEqual(rec.marker(1).window, Window(0, at(0, 20)))

    def test_dragged_window_survives_handle_changes(self):
        rec = recording(Marker(1, at(11, 40)))
        drag_edge(rec, self.handles, self.only_clip(rec), "end", at(12, 5))
        self.handles.before_ms = 30_000
        self.handles.enabled = False
        clip = self.only_clip(rec)
        self.assertEqual((clip.start_ms, clip.end_ms), (at(11, 20), at(12, 5)))

    def test_merged_clip_start_moves_the_earliest_starting_window(self):
        rec = recording(Marker(1, at(11, 40)), Marker(2, at(11, 50)))
        drag_edge(rec, self.handles, self.only_clip(rec), "start", at(11, 0))
        self.assertEqual(rec.marker(1).window, Window(at(11, 0), at(11, 45)))
        self.assertIsNone(rec.marker(2).window)

    def test_merged_clip_end_moves_the_latest_ending_window(self):
        rec = recording(Marker(1, at(11, 40)), Marker(2, at(11, 50)))
        drag_edge(rec, self.handles, self.only_clip(rec), "end", at(12, 30))
        self.assertEqual(rec.marker(2).window, Window(at(11, 30), at(12, 30)))
        self.assertIsNone(rec.marker(1).window)

    def test_returns_the_marker_whose_window_moved(self):
        rec = recording(Marker(1, at(11, 40)), Marker(2, at(11, 50)))
        self.assertEqual(drag_edge(rec, self.handles, self.only_clip(rec), "end", at(12, 0)), 2)

    def test_continuing_a_drag_keeps_moving_the_same_window(self):
        rec = recording(Marker(1, at(11, 40)), Marker(2, at(11, 50)))
        moved = drag_edge(rec, self.handles, self.only_clip(rec), "start", at(11, 25))
        set_window_edge(rec, self.handles, moved, "start", at(11, 35))
        self.assertEqual(rec.marker(1).window.start_ms, at(11, 35))
        self.assertIsNone(rec.marker(2).window)

    def test_a_bookmark_has_no_window_to_move(self):
        rec = recording(Marker(1, at(11, 40)))
        with self.assertRaises(ValueError):
            set_window_edge(rec, HandleSettings(enabled=False), 1, "start", at(11, 0))


if __name__ == "__main__":
    unittest.main()
