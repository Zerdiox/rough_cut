"""The marker list, the marker editor, and the auto-handle settings: the right-hand panel."""

from PySide6.QtCore import QRectF, QSize, Qt
from PySide6.QtGui import QPainter, QPen
from PySide6.QtWidgets import (
    QAbstractButton, QButtonGroup, QGridLayout, QHBoxLayout, QListWidgetItem, QVBoxLayout, QWidget,
)
from qfluentwidgets import (
    BodyLabel, CaptionLabel, FluentIcon, LineEdit, ListWidget, PlainTextEdit, SpinBox,
    StrongBodyLabel, SubtitleLabel, SwitchButton, ToolButton,
)

from roughcut.ui import theme

ID_ROLE = Qt.ItemDataRole.UserRole


class ColorDot(QWidget):
    def __init__(self, color_name, size=12, parent=None):
        super().__init__(parent)
        self.color_name = color_name
        self.setFixedSize(size, size)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(theme.marker_color(self.color_name))
        painter.drawEllipse(QRectF(0, 0, self.width(), self.height()))


class MarkerRow(QWidget):
    def __init__(self, session, marker, parent=None):
        super().__init__(parent)
        window = session.window_for(marker)
        name = StrongBodyLabel(marker.name or "Unnamed")
        if not marker.name:
            name.setStyleSheet(f"color: {theme.color('text_muted').name()}; font-style: italic;")
        kind = CaptionLabel("clip" if window else "bookmark")
        kind.setToolTip(
            f"{theme.format_time(window.start_ms)} - {theme.format_time(window.end_ms)}" if window
            else "No clip around this marker yet")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(10)
        layout.addWidget(ColorDot(marker.color))
        layout.addWidget(CaptionLabel(theme.format_time(marker.time_ms)))
        layout.addWidget(name, 1)
        layout.addWidget(kind)


class MarkerList(QWidget):
    """Every marker in time order; clicking one selects it."""

    def __init__(self, session, parent=None):
        super().__init__(parent)
        self.session = session
        self.count = CaptionLabel()
        self.add_button = ToolButton(FluentIcon.ADD)
        self.add_button.setToolTip("Add a marker at the playhead (M). Comes with playback.")
        self.add_button.setEnabled(False)
        self.empty_hint = CaptionLabel(
            "No markers yet. Chapter markers from OBS show up here; press M while watching to add one.")
        self.empty_hint.setWordWrap(True)
        self.list = ListWidget()
        self.list.currentItemChanged.connect(self._current_changed)

        header = QHBoxLayout()
        header.addWidget(SubtitleLabel("Markers"))
        header.addWidget(self.count)
        header.addStretch(1)
        header.addWidget(self.add_button)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(header)
        layout.addWidget(self.empty_hint)
        layout.addWidget(self.list, 1)

        session.changed.connect(self.refresh)
        session.selectionChanged.connect(self._follow_selection)
        self.refresh()

    def refresh(self):
        self.list.blockSignals(True)
        self.list.clear()
        markers = self.session.markers_by_time()
        for marker in markers:
            item = QListWidgetItem()
            item.setData(ID_ROLE, marker.id)
            row = MarkerRow(self.session, marker)
            item.setSizeHint(QSize(0, row.sizeHint().height()))
            self.list.addItem(item)
            self.list.setItemWidget(item, row)
        self.list.blockSignals(False)
        self.count.setText(str(len(markers)) if markers else "")
        self.empty_hint.setVisible(not markers)
        self.list.setVisible(bool(markers))
        self._follow_selection()

    def _follow_selection(self):
        self.list.blockSignals(True)
        selected = self.session.selected_marker_id
        self.list.setCurrentRow(-1)
        for row in range(self.list.count()):
            if self.list.item(row).data(ID_ROLE) == selected:
                self.list.setCurrentRow(row)
                self.list.scrollToItem(self.list.item(row))
        self.list.blockSignals(False)

    def _current_changed(self, current, previous):
        self.session.select_marker(current.data(ID_ROLE) if current else None)


class ColorChoice(QAbstractButton):
    def __init__(self, color_name, parent=None):
        super().__init__(parent)
        self.color_name = color_name
        self.setCheckable(True)
        self.setToolTip(color_name)
        self.setFixedSize(22, 22)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        if self.isChecked():
            painter.setPen(QPen(theme.color("text"), 2))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(QRectF(1, 1, 20, 20))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(theme.marker_color(self.color_name))
        painter.drawEllipse(QRectF(5, 5, 12, 12))


class MarkerEditor(QWidget):
    """Name, color and note of the selected marker."""

    def __init__(self, session, parent=None):
        super().__init__(parent)
        self.session = session
        self.nothing = CaptionLabel("Select a marker to edit its name, color and note.")
        self.time = CaptionLabel()
        self.name = LineEdit()
        self.name.setPlaceholderText("Unnamed")
        self.name.textEdited.connect(lambda text: self._update(name=text))
        self.note = PlainTextEdit()
        self.note.setPlaceholderText("Note")
        self.note.setFixedHeight(52)
        self.note.textChanged.connect(lambda: self._update(note=self.note.toPlainText()))

        self.colors = QButtonGroup(self)
        self.colors.setExclusive(True)
        palette = QGridLayout()
        palette.setSpacing(2)
        for index, color_name in enumerate(theme.MARKER_COLORS):
            choice = ColorChoice(color_name)
            self.colors.addButton(choice)
            palette.addWidget(choice, index // 8, index % 8)
        self.colors.buttonClicked.connect(lambda button: self._update(color=button.color_name))

        self.fields = QWidget()
        fields = QVBoxLayout(self.fields)
        fields.setContentsMargins(0, 0, 0, 0)
        fields.setSpacing(6)
        fields.addWidget(self.time)
        fields.addWidget(self.name)
        fields.addLayout(palette)
        fields.addWidget(self.note)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.nothing)
        layout.addWidget(self.fields)

        session.selectionChanged.connect(self.refresh)
        self.refresh()

    def refresh(self):
        marker = self.session.selected_marker()
        self.nothing.setVisible(marker is None)
        self.fields.setVisible(marker is not None)
        if marker is None:
            return
        self._loading = True
        self.time.setText(f"Marker at {theme.format_time(marker.time_ms)}")
        self.name.setText(marker.name)
        self.note.setPlainText(marker.note)
        for button in self.colors.buttons():
            button.setChecked(button.color_name == marker.color)
        self._loading = False

    def _update(self, **fields):
        if getattr(self, "_loading", False) or self.session.selected_marker_id is None:
            return
        self.session.update_marker(self.session.selected_marker_id, **fields)


class SecondsBox(SpinBox):
    """QFluentWidgets' spin box, with its text field given the room left of the arrows.

    With PySide6 6.12 the field inside SpinBox is laid out 1 px wide, so the
    number never shows; placing it by hand after every layout pass fixes that.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setRange(0, 600)
        self.setSuffix(" s")
        self.setMinimumWidth(150)

    def _place_field(self):
        right = min(self.upButton.x(), self.downButton.x()) - 4
        if right > 0:
            self.lineEdit().setGeometry(0, 0, right, self.height())

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._place_field()

    def showEvent(self, event):
        super().showEvent(event)
        self._place_field()


class HandleSettingsPanel(QWidget):
    """Auto-handles: suggest a clip window around every marker without one."""

    def __init__(self, session, parent=None):
        super().__init__(parent)
        self.session = session
        self.switch = SwitchButton()
        self.switch.setOnText("On")
        self.switch.setOffText("Off")
        self.switch.checkedChanged.connect(session.set_handles_enabled)
        self.before = self._seconds_box(lambda s: session.set_handle_before_ms(s * 1000))
        self.after = self._seconds_box(lambda s: session.set_handle_after_ms(s * 1000))
        hint = CaptionLabel("Clips you adjust by hand keep their own length.")
        hint.setWordWrap(True)

        top = QHBoxLayout()
        top.addWidget(StrongBodyLabel("Suggest clips around markers"), 1)
        top.addWidget(self.switch)

        lengths = QGridLayout()
        lengths.addWidget(BodyLabel("Before"), 0, 0)
        lengths.addWidget(self.before, 0, 1)
        lengths.addWidget(BodyLabel("After"), 1, 0)
        lengths.addWidget(self.after, 1, 1)
        lengths.setColumnStretch(2, 1)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(top)
        layout.addLayout(lengths)
        layout.addWidget(hint)

        session.changed.connect(self.refresh)
        self.refresh()

    def _seconds_box(self, on_change):
        box = SecondsBox()
        box.valueChanged.connect(on_change)
        return box

    def refresh(self):
        handles = self.session.handles
        for widget, value in ((self.switch, None), (self.before, handles.before_ms // 1000),
                              (self.after, handles.after_ms // 1000)):
            widget.blockSignals(True)
            if value is None:
                widget.setChecked(handles.enabled)
            else:
                widget.setValue(value)
                widget.setEnabled(handles.enabled)
            widget.blockSignals(False)
