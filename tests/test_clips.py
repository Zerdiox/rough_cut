import unittest

from roughcut.model.clips import derive_clips, total_length_ms
from roughcut.model.recording import HandleSettings, Marker, Recording, Window


def at(minutes, seconds):
    return (minutes * 60 + seconds) * 1000


def recording(*markers, duration_ms=at(82, 10)):
    return Recording(name="raid_night_0412", duration_ms=duration_ms, markers=list(markers))


class DeriveClipsTest(unittest.TestCase):
    def test_bookmarks_make_no_clips(self):
        rec = recording(Marker(1, at(3, 12)), Marker(2, at(11, 40)))
        self.assertEqual(derive_clips(rec, HandleSettings(enabled=False)), [])

    def test_one_clip_per_separate_window(self):
        rec = recording(Marker(1, at(3, 12)), Marker(2, at(11, 40)))
        clips = derive_clips(rec, HandleSettings())
        self.assertEqual([(c.start_ms, c.end_ms) for c in clips],
                         [(at(2, 52), at(3, 17)), (at(11, 20), at(11, 45))])
        self.assertEqual([c.marker_ids for c in clips], [(1,), (2,)])

    def test_overlapping_windows_merge(self):
        rec = recording(Marker(1, at(11, 40)), Marker(2, at(11, 50)))
        clips = derive_clips(rec, HandleSettings())
        self.assertEqual(len(clips), 1)
        self.assertEqual((clips[0].start_ms, clips[0].end_ms), (at(11, 20), at(11, 55)))
        self.assertEqual(clips[0].marker_ids, (1, 2))

    def test_touching_windows_merge(self):
        rec = recording(
            Marker(1, at(1, 0), window=Window(at(0, 50), at(1, 10))),
            Marker(2, at(1, 20), window=Window(at(1, 10), at(1, 30))),
        )
        clips = derive_clips(rec, HandleSettings(enabled=False))
        self.assertEqual([(c.start_ms, c.end_ms) for c in clips], [(at(0, 50), at(1, 30))])

    def test_window_clamps_at_recording_start(self):
        rec = recording(Marker(1, at(0, 5)))
        self.assertEqual(derive_clips(rec, HandleSettings())[0].start_ms, 0)

    def test_window_clamps_at_recording_end(self):
        rec = recording(Marker(1, at(82, 8)))
        self.assertEqual(derive_clips(rec, HandleSettings())[0].end_ms, at(82, 10))

    def test_clips_follow_recording_order_not_marker_order(self):
        rec = recording(Marker(1, at(40, 0)), Marker(2, at(3, 0)))
        clips = derive_clips(rec, HandleSettings())
        self.assertEqual([c.marker_ids for c in clips], [(2,), (1,)])

    def test_merged_clip_lists_markers_by_time(self):
        rec = recording(Marker(7, at(11, 50)), Marker(3, at(11, 40)))
        self.assertEqual(derive_clips(rec, HandleSettings())[0].marker_ids, (3, 7))

    def test_count_and_total_length(self):
        rec = recording(Marker(1, at(3, 12)), Marker(2, at(11, 40)), Marker(3, at(11, 50)))
        clips = derive_clips(rec, HandleSettings())
        self.assertEqual(len(clips), 2)
        self.assertEqual(total_length_ms(clips), 25_000 + 35_000)


if __name__ == "__main__":
    unittest.main()
