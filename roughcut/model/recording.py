"""A recording, its markers and the auto-handle settings.

Times are whole milliseconds so merging and clamping compare exactly.
Only windows the user set by hand are stored on a marker; suggested windows
are worked out from the handle settings each time, so changing the handles
can never touch a hand-set window.
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Window:
    start_ms: int
    end_ms: int

    @property
    def length_ms(self):
        return self.end_ms - self.start_ms


@dataclass
class Marker:
    id: int
    time_ms: int
    name: str = ""
    color: str = "Blue"
    note: str = ""
    window: Window | None = None  # hand-set only


@dataclass
class HandleSettings:
    enabled: bool = True
    before_ms: int = 20_000
    after_ms: int = 5_000


@dataclass
class Recording:
    name: str
    duration_ms: int
    markers: list[Marker] = field(default_factory=list)

    def marker(self, marker_id):
        for marker in self.markers:
            if marker.id == marker_id:
                return marker
        raise KeyError(marker_id)


def effective_window(marker, handles):
    """The window a marker contributes, or None when it is a bookmark."""
    if marker.window is not None:
        return marker.window
    if handles.enabled:
        return Window(marker.time_ms - handles.before_ms, marker.time_ms + handles.after_ms)
    return None
