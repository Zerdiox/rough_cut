"""The two timeline strips: an overview of the whole recording and a zoomable detail strip.

Both paint straight from the session. The detail strip owns the visible range;
the overview shows it as a box and asks the detail strip to move there when
clicked.
"""

from PySide6.QtCore import QPointF, QRectF, Qt, Signal
from PySide6.QtGui import QColor, QFont, QFontMetrics, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QVBoxLayout, QWidget

from roughcut.ui import theme

EDGE_GRAB_PX = 6
MIN_SPAN_MS = 10_000
TICK_STEPS_MS = [s * 1000 for s in (1, 2, 5, 10, 15, 30, 60, 120, 300, 600, 900, 1800, 3600)]


def _with_alpha(color, alpha):
    color = QColor(color)
    color.setAlpha(alpha)
    return color


def _flag_path(x, top, size=1.0):
    """The marker flag: a rounded tab with a point at x."""
    w, h, tip = 14 * size, 10 * size, 5 * size
    path = QPainterPath()
    path.addRoundedRect(QRectF(x - w / 2, top, w, h), 2, 2)
    path.moveTo(x - 3.5 * size, top + h)
    path.lineTo(x, top + h + tip)
    path.lineTo(x + 3.5 * size, top + h)
    return path.simplified()


class OverviewStrip(QWidget):
    """The whole recording at a glance; click to move the detail strip there."""

    centerRequested = Signal(int)

    def __init__(self, session, parent=None):
        super().__init__(parent)
        self.session = session
        self.visible_range = (0, session.recording.duration_ms)
        self.setMinimumHeight(40)
        self.setMaximumHeight(40)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        session.changed.connect(self.update)

    def set_visible_range(self, start_ms, end_ms):
        self.visible_range = (start_ms, end_ms)
        self.update()

    def _x(self, ms):
        duration = max(1, self.session.recording.duration_ms)
        return 1 + (self.width() - 2) * ms / duration

    def mousePressEvent(self, event):
        duration = self.session.recording.duration_ms
        ms = int((event.position().x() - 1) / max(1, self.width() - 2) * duration)
        self.centerRequested.emit(max(0, min(duration, ms)))

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.MouseButton.LeftButton:
            self.mousePressEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        track = QRectF(1, 12, self.width() - 2, 18)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(theme.color("track"))
        painter.drawRoundedRect(track, 4, 4)

        painter.setBrush(_with_alpha(theme.color("clip_fill"), 200))
        for clip in self.session.clips():
            x1, x2 = self._x(clip.start_ms), self._x(clip.end_ms)
            painter.drawRect(QRectF(x1, track.top(), max(2.0, x2 - x1), track.height()))

        for marker in self.session.recording.markers:
            x = self._x(marker.time_ms)
            painter.setPen(QPen(theme.marker_color(marker.color), 2))
            painter.drawLine(QPointF(x, 4), QPointF(x, track.bottom()))

        start, end = self.visible_range
        if (start, end) != (0, self.session.recording.duration_ms):
            x1, x2 = self._x(start), self._x(end)
            painter.setPen(QPen(theme.color("visible_range"), 2))
            painter.setBrush(_with_alpha(theme.color("visible_range"), 30))
            painter.drawRoundedRect(QRectF(x1, 2, max(4.0, x2 - x1), self.height() - 4), 3, 3)


class DetailStrip(QWidget):
    """Ruler, marker flags with names, clip blocks with draggable edges.

    Wheel scrolls, Ctrl+wheel zooms around the pointer, clicking a flag selects
    its marker.
    """

    visibleRangeChanged = Signal(int, int)

    RULER = 22
    FLAGS = 34
    TRACK = 46

    def __init__(self, session, parent=None):
        super().__init__(parent)
        self.session = session
        self.view_start = 0
        self.view_end = max(MIN_SPAN_MS, session.recording.duration_ms)
        self._drag = None  # (marker_id, edge) while an edge is being dragged
        self.setMouseTracking(True)
        self.setMinimumHeight(self.RULER + self.FLAGS + self.TRACK + 8)
        self.setMaximumHeight(self.RULER + self.FLAGS + self.TRACK + 8)
        session.changed.connect(self.update)
        session.selectionChanged.connect(self._follow_selection)
        session.playheadChanged.connect(self.update)

    # visible range

    def set_visible_range(self, start_ms, end_ms):
        duration = max(MIN_SPAN_MS, self.session.recording.duration_ms)
        span = max(MIN_SPAN_MS, min(duration, end_ms - start_ms))
        start = max(0, min(start_ms, duration - span))
        self.view_start, self.view_end = start, start + span
        self.visibleRangeChanged.emit(self.view_start, self.view_end)
        self.update()

    def center_on(self, ms):
        span = self.view_end - self.view_start
        self.set_visible_range(ms - span // 2, ms - span // 2 + span)

    def _follow_selection(self):
        """Bring a newly selected marker into view; one already in view stays put."""
        marker = self.session.selected_marker()
        if marker and not self.view_start <= marker.time_ms <= self.view_end:
            self.center_on(marker.time_ms)
        self.update()

    def _x(self, ms):
        return (ms - self.view_start) * self.width() / max(1, self.view_end - self.view_start)

    def _ms(self, x):
        return int(self.view_start + x * (self.view_end - self.view_start) / max(1, self.width()))

    # hit testing

    def _edge_at(self, x, y):
        if not self.RULER + self.FLAGS <= y <= self.height():
            return None
        for clip in self.session.clips():
            for edge, ms in (("start", clip.start_ms), ("end", clip.end_ms)):
                if abs(self._x(ms) - x) <= EDGE_GRAB_PX:
                    return clip, edge
        return None

    def _flag_at(self, x, y):
        if not self.RULER <= y <= self.RULER + self.FLAGS:
            return None
        for marker in self.session.markers_by_time():
            if abs(self._x(marker.time_ms) - x) <= 8:
                return marker
        return None

    # mouse

    def mousePressEvent(self, event):
        x, y = event.position().x(), event.position().y()
        hit = self._edge_at(x, y)
        if hit:
            clip, edge = hit
            marker_id = self.session.drag_edge(clip, edge, self._ms(x))
            self._drag = (marker_id, edge)
            return
        marker = self._flag_at(x, y)
        if marker:
            self.session.select_marker(marker.id)

    def mouseMoveEvent(self, event):
        x, y = event.position().x(), event.position().y()
        if self._drag:
            marker_id, edge = self._drag
            self.session.drag_window_edge(marker_id, edge, self._ms(x))
            return
        if self._edge_at(x, y):
            self.setCursor(Qt.CursorShape.SizeHorCursor)
        elif self._flag_at(x, y):
            self.setCursor(Qt.CursorShape.PointingHandCursor)
        else:
            self.unsetCursor()

    def mouseReleaseEvent(self, event):
        self._drag = None

    def wheelEvent(self, event):
        delta = event.angleDelta().y() or event.angleDelta().x()
        if not delta:
            return
        span = self.view_end - self.view_start
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            anchor = self._ms(event.position().x())
            factor = 0.8 if delta > 0 else 1.25
            new_span = int(span * factor)
            ratio = (anchor - self.view_start) / max(1, span)
            start = int(anchor - ratio * new_span)
            self.set_visible_range(start, start + new_span)
        else:
            shift = int(span * 0.1) * (-1 if delta > 0 else 1)
            self.set_visible_range(self.view_start + shift, self.view_end + shift)
        event.accept()

    # painting

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        self._paint_ruler(painter)
        track = QRectF(0, self.RULER + self.FLAGS, self.width(), self.TRACK)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(theme.color("track"))
        painter.drawRoundedRect(track, 4, 4)
        self._paint_clips(painter, track)
        self._paint_markers(painter, track)
        self._paint_playhead(painter)

    def _paint_ruler(self, painter):
        span = self.view_end - self.view_start
        step = next((s for s in TICK_STEPS_MS if s * self.width() / max(1, span) >= 90), TICK_STEPS_MS[-1])
        font = QFont(self.font())
        font.setPointSizeF(8)
        painter.setFont(font)
        metrics = QFontMetrics(font)
        tick = (self.view_start // step) * step
        while tick <= self.view_end:
            x = self._x(tick)
            if x >= 0:
                painter.setPen(QPen(theme.color("track_tick"), 1))
                painter.drawLine(QPointF(x, self.RULER - 6), QPointF(x, self.RULER))
                label = theme.format_time(tick)
                if x + 3 + metrics.horizontalAdvance(label) <= self.width():
                    painter.setPen(theme.color("text_muted"))
                    painter.drawText(QPointF(x + 3, self.RULER - 8), label)
            tick += step

    def _paint_clips(self, painter, track):
        fill = _with_alpha(theme.color("clip_fill"), 150)
        edge_pen = QPen(theme.color("clip_edge"), 2)
        for clip in self.session.clips():
            x1, x2 = self._x(clip.start_ms), self._x(clip.end_ms)
            if x2 < 0 or x1 > self.width():
                continue
            block = QRectF(x1, track.top() + 6, max(2.0, x2 - x1), track.height() - 12)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(fill)
            painter.drawRoundedRect(block, 3, 3)
            painter.setPen(edge_pen)
            for x in (block.left(), block.right()):
                painter.drawLine(QPointF(x, block.top() - 3), QPointF(x, block.bottom() + 3))

    def _paint_markers(self, painter, track):
        name_font = QFont(self.font())
        name_font.setPointSizeF(8.5)
        metrics = QFontMetrics(name_font)
        painter.setFont(name_font)
        selected = self.session.selected_marker_id
        flag_top = self.RULER + 4
        markers = self.session.markers_by_time()
        xs = [self._x(m.time_ms) for m in markers]
        for index, marker in enumerate(markers):
            x = xs[index]
            if x < -10 or x > self.width() + 10:
                continue
            color = theme.marker_color(marker.color)
            painter.setPen(QPen(_with_alpha(color, 220), 1.5))
            painter.drawLine(QPointF(x, flag_top + 15), QPointF(x, track.bottom()))
            if marker.id == selected:
                painter.setPen(QPen(theme.color("text"), 2))
            else:
                painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(color)
            painter.drawPath(_flag_path(x, flag_top))
            # Name to the right of the flag when there's room before the next one.
            room = (xs[index + 1] if index + 1 < len(xs) else self.width()) - x - 14
            label = marker.name or "Unnamed"
            if room > 30:
                painter.setPen(theme.color("text") if marker.name else theme.color("text_muted"))
                painter.drawText(QPointF(x + 10, flag_top + 10), metrics.elidedText(
                    label, Qt.TextElideMode.ElideRight, int(room)))

    def _paint_playhead(self, painter):
        x = self._x(self.session.playhead_ms)
        if 0 <= x <= self.width():
            painter.setPen(QPen(theme.color("playhead"), 2))
            painter.drawLine(QPointF(x, 0), QPointF(x, self.height()))


class TimelinePanel(QWidget):
    """Overview over detail, kept in step."""

    def __init__(self, session, parent=None):
        super().__init__(parent)
        self.overview = OverviewStrip(session)
        self.detail = DetailStrip(session)
        self.detail.visibleRangeChanged.connect(self.overview.set_visible_range)
        self.overview.centerRequested.connect(self.detail.center_on)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        layout.addWidget(self.overview)
        layout.addWidget(self.detail)

    def set_visible_range(self, start_ms, end_ms):
        self.detail.set_visible_range(start_ms, end_ms)
