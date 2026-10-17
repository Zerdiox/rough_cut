"""Clips are derived from the markers' windows, never stored.

Each marker's window is clamped to the recording, then windows that overlap
or touch merge into one clip. Clips are always in recording order.
"""

from dataclasses import dataclass

from roughcut.model.recording import Window, effective_window


@dataclass(frozen=True)
class Clip:
    start_ms: int
    end_ms: int
    marker_ids: tuple[int, ...]  # by marker time; the first one identifies the clip

    @property
    def key(self):
        return self.marker_ids[0]

    @property
    def length_ms(self):
        return self.end_ms - self.start_ms


def clamped_window(marker, handles, duration_ms):
    window = effective_window(marker, handles)
    if window is None:
        return None
    return Window(max(0, window.start_ms), min(duration_ms, window.end_ms))


def derive_clips(recording, handles):
    spans = []
    for marker in recording.markers:
        window = clamped_window(marker, handles, recording.duration_ms)
        if window is not None:
            spans.append((window.start_ms, window.end_ms, marker))
    spans.sort(key=lambda span: (span[0], span[2].time_ms))

    groups = []
    for start, end, marker in spans:
        if groups and start <= groups[-1][1]:
            group = groups[-1]
            group[1] = max(group[1], end)
            group[2].append(marker)
        else:
            groups.append([start, end, [marker]])

    return [
        Clip(start, end, tuple(m.id for m in sorted(markers, key=lambda m: (m.time_ms, m.id))))
        for start, end, markers in groups
    ]


def drag_edge(recording, handles, clip, edge, to_ms):
    """Move a clip's start or end edge and return the id of the marker whose window moved.

    The edge belongs to one marker's window: the earliest-starting one for the
    start, the latest-ending one for the end.
    """
    if edge not in ("start", "end"):
        raise ValueError(f"edge must be 'start' or 'end', not {edge!r}")
    duration = recording.duration_ms
    owned = [
        (marker_id, clamped_window(recording.marker(marker_id), handles, duration))
        for marker_id in clip.marker_ids
    ]
    if edge == "start":
        marker_id, _ = min(owned, key=lambda pair: pair[1].start_ms)
    else:
        marker_id, _ = max(owned, key=lambda pair: pair[1].end_ms)
    set_window_edge(recording, handles, marker_id, edge, to_ms)
    return marker_id


def set_window_edge(recording, handles, marker_id, edge, to_ms):
    """Move one edge of a marker's window, making the window hand-set.

    The edge can't cross its own marker or leave the recording. Dragging keeps
    calling this for the same marker, so a drag never jumps to another window.
    """
    marker = recording.marker(marker_id)
    window = clamped_window(marker, handles, recording.duration_ms)
    if window is None:
        raise ValueError(f"marker {marker_id} is a bookmark and has no window to move")
    if edge == "start":
        marker.window = Window(min(max(to_ms, 0), marker.time_ms), window.end_ms)
    elif edge == "end":
        marker.window = Window(window.start_ms, max(min(to_ms, recording.duration_ms), marker.time_ms))
    else:
        raise ValueError(f"edge must be 'start' or 'end', not {edge!r}")


def total_length_ms(clips):
    return sum(clip.length_ms for clip in clips)
