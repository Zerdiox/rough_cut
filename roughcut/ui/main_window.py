"""The editor window: viewer and side panel on top, transport, timeline and summary below."""

from PySide6.QtCore import QRectF, QSize, Qt
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout, QWidget
from qfluentwidgets import BodyLabel, FluentIcon, PushButton

from roughcut.ui import theme
from roughcut.ui.export_dialog import ExportOverlay
from roughcut.ui.markers import MarkerList, handle_settings_panel, marker_editor_panel
from roughcut.ui.summary_bar import SummaryBar
from roughcut.ui.timeline import TimelinePanel
from roughcut.ui.transport_bar import TransportBar


class ViewerPlaceholder(QWidget):
    """Where the video will play."""

    def __init__(self, session, parent=None):
        super().__init__(parent)
        self.session = session
        self.setMinimumSize(400, 225)

    def sizeHint(self):
        # Taller than the side panel needs with both panels open, so folding
        # them never changes the window's preferred height (or the video).
        return QSize(854, 480)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(theme.color("viewer"))
        painter.drawRoundedRect(QRectF(self.rect()), 6, 6)
        painter.setPen(theme.color("viewer_text"))
        text = "Video will play here"
        if self.session.recording.markers:
            text += f"\n{self.session.recording.name}"
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, text)


def _divider():
    line = QFrame()
    line.setFrameShape(QFrame.Shape.HLine)
    line.setStyleSheet(f"color: {theme.color('border').name()};")
    return line


class MainWindow(QWidget):
    def __init__(self, session, parent=None):
        super().__init__(parent)
        self.session = session
        self.setObjectName("MainWindow")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
        self.setStyleSheet(f"#MainWindow {{ background: {theme.color('surface_alt').name()}; }}")
        self.setMinimumSize(1040, 680)
        self.overlay = None

        open_button = PushButton(FluentIcon.FOLDER, "Open recording...")
        open_button.setToolTip("Opening recordings comes with playback")
        file_name = BodyLabel(f"{session.recording.name}.mp4" if session.recording.markers else "")
        top = QHBoxLayout()
        top.addWidget(open_button)
        top.addSpacing(12)
        top.addWidget(file_name)
        top.addStretch(1)

        self.viewer = ViewerPlaceholder(session)
        side = QVBoxLayout()
        side.setSpacing(8)
        self.marker_list = MarkerList(session)
        self.marker_panel = marker_editor_panel(session)
        self.handles_panel = handle_settings_panel(session)
        side.addWidget(self.marker_list, 1)
        side.addWidget(_divider())
        side.addWidget(self.marker_panel)
        side.addWidget(_divider())
        side.addWidget(self.handles_panel)
        side_panel = QWidget()
        side_panel.setFixedWidth(330)
        side_panel.setLayout(side)

        upper = QHBoxLayout()
        upper.setSpacing(16)
        upper.addWidget(self.viewer, 1)
        upper.addWidget(side_panel)

        self.timeline = TimelinePanel(session)
        self.summary = SummaryBar(session)
        self.summary.exportRequested.connect(self.open_export)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 8, 16, 8)
        layout.setSpacing(6)
        layout.addLayout(top)
        layout.addLayout(upper, 1)
        layout.addWidget(TransportBar(session))
        layout.addWidget(self.timeline)
        layout.addWidget(_divider())
        layout.addWidget(self.summary)

    def open_export(self):
        if self.overlay is not None:
            self.overlay.close()
        self.overlay = ExportOverlay(self.session, self)
        self.overlay.show()
        self.overlay.raise_()
        return self.overlay
