import unittest

import qt
from roughcut.gallery import fixtures
from roughcut.gallery.fixtures import at
from roughcut.ui.session import Session
from roughcut.ui.timeline import TimelinePanel
from roughcut.ui.transport_bar import TransportBar


class SessionPlayheadTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = qt.app()

    def setUp(self):
        self.session = Session(fixtures.raid_night(), playhead_ms=at(0, 5, 0))
        self.moves = []
        self.session.playheadChanged.connect(lambda: self.moves.append(self.session.playhead_ms))

    def test_selecting_moves_the_playhead_to_the_marker(self):
        self.session.select_marker(2)
        self.assertEqual(self.session.playhead_ms, at(0, 11, 40))
        self.assertEqual(self.moves, [at(0, 11, 40)])

    def test_clearing_the_selection_leaves_the_playhead(self):
        self.session.select_marker(2)
        self.session.select_marker(None)
        self.assertEqual(self.session.playhead_ms, at(0, 11, 40))
        self.assertEqual(len(self.moves), 1)

    def test_editing_a_marker_does_not_move_it(self):
        self.session.select_marker(2)
        self.session.set_playhead(at(0, 20, 0))
        self.session.update_marker(2, name="Ambush and push", color="Red")
        self.assertEqual(self.session.playhead_ms, at(0, 20, 0))

    def test_set_playhead_emits_only_on_a_move(self):
        self.session.set_playhead(at(0, 5, 0))
        self.assertEqual(self.moves, [])
        self.session.set_playhead(at(0, 6, 0))
        self.assertEqual(self.moves, [at(0, 6, 0)])

    def test_transport_readout_follows_the_playhead(self):
        bar = TransportBar(self.session)
        self.session.select_marker(2)
        self.assertTrue(bar.time.text().startswith("00:11:40 /"))


class TimelineFollowsSelectionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = qt.app()

    def setUp(self):
        self.session = Session(fixtures.raid_night())
        self.panel = TimelinePanel(self.session)
        self.panel.resize(1000, 200)
        self.panel.set_visible_range(at(0, 8, 0), at(0, 16, 0))

    def detail_range(self):
        return self.panel.detail.view_start, self.panel.detail.view_end

    def test_a_marker_out_of_view_is_centered(self):
        self.session.select_marker(1)  # Breach, 00:03:12
        # Centered, then kept inside the recording: 00:03:12 is less than half
        # the 8-minute span from the start, so the range starts at 0.
        self.assertEqual(self.detail_range(), (0, at(0, 8, 0)))
        self.assertEqual(self.panel.overview.visible_range, self.detail_range())

    def test_a_marker_out_of_view_mid_recording_is_centered_exactly(self):
        self.session.select_marker(4)  # Unnamed, 00:27:05
        start, end = self.detail_range()
        self.assertEqual((start + end) // 2, at(0, 27, 5))
        self.assertEqual(end - start, at(0, 8, 0))
        self.assertEqual(self.panel.overview.visible_range, self.detail_range())

    def test_a_marker_in_view_leaves_the_range(self):
        self.session.select_marker(2)  # Ambush, 00:11:40
        self.assertEqual(self.detail_range(), (at(0, 8, 0), at(0, 16, 0)))

    def test_clearing_the_selection_leaves_the_range(self):
        self.session.select_marker(None)
        self.session.select_marker(2)
        self.session.select_marker(None)
        self.assertEqual(self.detail_range(), (at(0, 8, 0), at(0, 16, 0)))


if __name__ == "__main__":
    unittest.main()
