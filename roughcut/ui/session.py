"""The editing session every widget reads from and edits through.

Widgets never talk to each other: they call the session and repaint when it
emits `changed` (anything about markers, windows, handles or clip names) or
`selectionChanged` (which marker is selected).
"""

from PySide6.QtCore import QObject, Signal

from roughcut.model import clips as clip_rules
from roughcut.model.clip_names import ClipNames
from roughcut.model.recording import HandleSettings


class Session(QObject):
    changed = Signal()
    selectionChanged = Signal()

    def __init__(self, recording, handles=None, playhead_ms=0, parent=None):
        super().__init__(parent)
        self.recording = recording
        self.handles = handles or HandleSettings()
        self.names = ClipNames()
        self.playhead_ms = playhead_ms
        self.selected_marker_id = None

    # reading

    def clips(self):
        return clip_rules.derive_clips(self.recording, self.handles)

    def clip_names(self, clips=None):
        return self.names.names_for(self.recording, clips if clips is not None else self.clips())

    def markers_by_time(self):
        return sorted(self.recording.markers, key=lambda m: (m.time_ms, m.id))

    def selected_marker(self):
        if self.selected_marker_id is None:
            return None
        return self.recording.marker(self.selected_marker_id)

    def window_for(self, marker):
        return clip_rules.clamped_window(marker, self.handles, self.recording.duration_ms)

    # editing

    def set_handles_enabled(self, enabled):
        if self.handles.enabled != enabled:
            self.handles.enabled = enabled
            self.changed.emit()

    def set_handle_before_ms(self, ms):
        if self.handles.before_ms != ms:
            self.handles.before_ms = ms
            self.changed.emit()

    def set_handle_after_ms(self, ms):
        if self.handles.after_ms != ms:
            self.handles.after_ms = ms
            self.changed.emit()

    def drag_edge(self, clip, edge, to_ms):
        """Move a clip edge; returns the marker id to keep dragging with drag_window_edge."""
        marker_id = clip_rules.drag_edge(self.recording, self.handles, clip, edge, to_ms)
        self.changed.emit()
        return marker_id

    def drag_window_edge(self, marker_id, edge, to_ms):
        clip_rules.set_window_edge(self.recording, self.handles, marker_id, edge, to_ms)
        self.changed.emit()

    def rename_clip(self, clip, name):
        self.names.rename(clip, name)
        self.changed.emit()

    def update_marker(self, marker_id, **fields):
        marker = self.recording.marker(marker_id)
        changed = False
        for key in ("name", "color", "note"):
            if key in fields and getattr(marker, key) != fields[key]:
                setattr(marker, key, fields[key])
                changed = True
        if changed:
            self.changed.emit()

    def select_marker(self, marker_id):
        if self.selected_marker_id != marker_id:
            self.selected_marker_id = marker_id
            self.selectionChanged.emit()
