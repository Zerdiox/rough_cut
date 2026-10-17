import unittest

from roughcut.model.clip_names import ClipNames
from roughcut.model.clips import derive_clips, drag_edge
from roughcut.model.recording import HandleSettings, Marker, Recording


def at(minutes, seconds):
    return (minutes * 60 + seconds) * 1000


class ClipNamesTest(unittest.TestCase):
    def setUp(self):
        self.handles = HandleSettings()
        self.rec = Recording(name="raid_night_0412", duration_ms=at(82, 10), markers=[
            Marker(1, at(3, 12), name="Breach"),
            Marker(2, at(11, 40), name="Ambush"),
            Marker(3, at(27, 5)),
        ])
        self.names = ClipNames()

    def clips(self):
        return derive_clips(self.rec, self.handles)

    def current(self):
        return self.names.names_for(self.rec, self.clips())

    def test_name_starts_as_marker_name(self):
        self.assertEqual(self.current()[:2], ["Breach", "Ambush"])

    def test_unnamed_marker_gives_recording_name_and_position(self):
        self.assertEqual(self.current()[2], "raid_night_0412 03")

    def test_typed_name_is_kept_across_a_resize(self):
        clip = self.clips()[1]
        self.names.rename(clip, "Ambush and push")
        drag_edge(self.rec, self.handles, clip, "end", at(12, 5))
        self.assertEqual(self.current()[1], "Ambush and push")

    def test_renaming_a_clip_leaves_the_marker_alone(self):
        self.names.rename(self.clips()[1], "Ambush and push")
        self.assertEqual(self.rec.marker(2).name, "Ambush")

    def test_marker_rename_flows_into_untyped_clip_name(self):
        self.rec.marker(2).name = "Flank"
        self.assertEqual(self.current()[1], "Flank")

    def test_marker_rename_does_not_change_typed_clip_name(self):
        self.names.rename(self.clips()[1], "Ambush and push")
        self.rec.marker(2).name = "Flank"
        self.assertEqual(self.current()[1], "Ambush and push")

    def test_merged_clip_keeps_the_earlier_clips_name(self):
        self.rec.markers.append(Marker(4, at(11, 50), name="Wipe"))
        self.names.rename(self.clips()[1], "Ambush and push")
        self.assertEqual(self.current()[1], "Ambush and push")

    def test_merged_clip_defaults_to_the_earliest_marker_name(self):
        self.rec.markers.append(Marker(4, at(11, 50), name="Wipe"))
        self.assertEqual(self.current()[1], "Ambush")


if __name__ == "__main__":
    unittest.main()
