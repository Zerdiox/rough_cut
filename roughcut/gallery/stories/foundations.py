from PySide6.QtCore import QRectF, QSize, Qt
from PySide6.QtGui import QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QGridLayout, QVBoxLayout, QWidget
from qfluentwidgets import (
    BodyLabel, CaptionLabel, DisplayLabel, LargeTitleLabel, StrongBodyLabel, SubtitleLabel,
    TitleLabel, isDarkTheme,
)

from roughcut.gallery.registry import story
from roughcut.ui import theme


class Swatch(QWidget):
    def __init__(self, fill, flag=False, parent=None):
        super().__init__(parent)
        self.fill = fill
        self.flag = flag
        self.setFixedSize(QSize(56, 40))

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(QPen(theme.color("border"), 1))
        painter.setBrush(self.fill)
        if self.flag:
            # Same shape the timeline uses for a marker.
            path = QPainterPath()
            path.addRoundedRect(QRectF(14, 4, 28, 20), 3, 3)
            path.moveTo(22, 24)
            path.lineTo(28, 34)
            path.lineTo(34, 24)
            painter.drawPath(path.simplified())
        else:
            painter.drawRoundedRect(QRectF(0.5, 0.5, self.width() - 1, self.height() - 1), 6, 6)


def _swatch_grid(entries, flag=False, columns=4):
    widget = QWidget()
    grid = QGridLayout(widget)
    grid.setHorizontalSpacing(28)
    grid.setVerticalSpacing(14)
    for index, (name, fill, detail) in enumerate(entries):
        cell = QWidget()
        row = QGridLayout(cell)
        row.setContentsMargins(0, 0, 0, 0)
        row.addWidget(Swatch(fill, flag), 0, 0, 2, 1)
        row.addWidget(StrongBodyLabel(name), 0, 1)
        row.addWidget(CaptionLabel(detail), 1, 1)
        row.setColumnStretch(1, 1)
        grid.addWidget(cell, index // columns, index % columns)
    return widget


@story("Foundations", "Colors", "all tokens")
def colors():
    entries = []
    for name, pair in theme.TOKENS.items():
        value = pair[1] if isDarkTheme() else pair[0]
        entries.append((name, theme.color(name), value))
    return _swatch_grid(entries)


@story("Foundations", "Type", "scale")
def type_scale():
    widget = QWidget()
    column = QVBoxLayout(widget)
    column.setSpacing(12)
    for label_class, use in [
        (DisplayLabel, "Display - not used in the editor"),
        (LargeTitleLabel, "Large title - empty states"),
        (TitleLabel, "Title - dialog headings"),
        (SubtitleLabel, "Subtitle - panel headings"),
        (StrongBodyLabel, "Strong body - marker and clip names"),
        (BodyLabel, "Body - most text"),
        (CaptionLabel, "Caption - times, hints, counts"),
    ]:
        column.addWidget(label_class(use))
    column.addWidget(CaptionLabel("01:22:10   00:11:40 - 00:12:05   3 clips, 2:45 total"))
    return widget


@story("Foundations", "Marker colors", "all 16")
def marker_colors():
    entries = [(name, theme.marker_color(name), "") for name in theme.MARKER_COLORS]
    return _swatch_grid(entries, flag=True)
