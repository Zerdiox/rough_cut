"""Name the clips and pick a folder before export.

Each clip becomes its own file, so every name is checked against what Windows
allows. Export stays disabled while any name has a problem. The panel is the
dialog's content; the overlay shows it over the main window.
"""

from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QFileDialog, QGridLayout, QHBoxLayout, QScrollArea, QFrame, QVBoxLayout, QWidget,
)
from qfluentwidgets import (
    BodyLabel, CaptionLabel, LineEdit, PrimaryPushButton, PushButton, StrongBodyLabel, TitleLabel,
)

from roughcut.model.clip_names import name_problems
from roughcut.ui import theme


def default_folder(recording):
    return str(Path.home() / "Videos" / recording.name)


class ClipRow:
    """The widgets for one clip, kept so typing doesn't rebuild the dialog."""

    def __init__(self, panel, clip):
        self.clip = clip
        self.number = CaptionLabel()
        self.range = CaptionLabel()
        self.name = LineEdit()
        self.name.setClearButtonEnabled(True)
        self.name.textEdited.connect(lambda text: panel.session.rename_clip(self.clip, text))
        self.marker = CaptionLabel()
        self.problem = CaptionLabel()
        self.problem.setStyleSheet(f"color: {theme.color('error').name()};")
        self.problem.hide()

    def widgets(self):
        return self.number, self.range, self.name, self.marker


class ExportPanel(QWidget):
    accepted = Signal(list, str)  # [(clip, name), ...], folder
    cancelled = Signal()

    def __init__(self, session, parent=None):
        super().__init__(parent)
        self.session = session
        self.rows = []
        self.setMinimumWidth(620)

        self.grid_host = QWidget()
        self.grid = QGridLayout(self.grid_host)
        self.grid.setHorizontalSpacing(14)
        self.grid.setVerticalSpacing(4)
        self.grid.setColumnStretch(2, 1)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setWidget(self.grid_host)
        scroll.setMaximumHeight(320)
        scroll.setStyleSheet("QScrollArea, QScrollArea > QWidget > QWidget { background: transparent; }")
        self.scroll = scroll

        self.folder = LineEdit()
        self.folder.setText(default_folder(session.recording))
        browse = PushButton("Browse")
        browse.clicked.connect(self._browse)
        self.status = CaptionLabel()
        self.export_button = PrimaryPushButton("Export")
        self.export_button.clicked.connect(self._accept)
        cancel = PushButton("Cancel")
        cancel.clicked.connect(self.cancelled)

        folder_row = QHBoxLayout()
        folder_row.addWidget(BodyLabel("Save to"))
        folder_row.addWidget(self.folder, 1)
        folder_row.addWidget(browse)

        buttons = QHBoxLayout()
        buttons.addWidget(self.status, 1)
        buttons.addWidget(cancel)
        buttons.addWidget(self.export_button)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        layout.addWidget(TitleLabel("Export clips"))
        layout.addWidget(CaptionLabel("Each clip is saved as its own file, named as below."))
        layout.addWidget(scroll)
        layout.addLayout(folder_row)
        layout.addLayout(buttons)

        session.changed.connect(self.refresh)
        self.refresh()

    def refresh(self):
        clips = self.session.clips()
        if [row.clip.key for row in self.rows] != [clip.key for clip in clips]:
            self._rebuild(clips)
        names = self.session.clip_names(clips)
        problems = name_problems(names)
        for position, (row, clip, name, problem) in enumerate(zip(self.rows, clips, names, problems), 1):
            row.clip = clip
            row.number.setText(f"{position}")
            row.range.setText(f"{theme.format_time(clip.start_ms)} - {theme.format_time(clip.end_ms)}")
            if not row.name.hasFocus() and row.name.text() != name:
                row.name.setText(name)
            row.marker.setText(self.session.recording.marker(clip.key).name or "Unnamed")
            row.name.setError(problem is not None)
            row.problem.setText(problem or "")
            row.problem.setVisible(problem is not None)
        count = sum(problem is not None for problem in problems)
        self.export_button.setEnabled(bool(clips) and count == 0)
        if count:
            self.status.setText(f"{count} name{'s' if count != 1 else ''} need{'' if count != 1 else 's'} fixing")
            self.status.setStyleSheet(f"color: {theme.color('error').name()};")
        else:
            noun = "clip" if len(clips) == 1 else "clips"
            self.status.setText(f"{len(clips)} {noun} ready")
            self.status.setStyleSheet("")

    def _rebuild(self, clips):
        while self.grid.count():
            item = self.grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        for column, title in enumerate(["#", "Range", "Name", "Marker"]):
            self.grid.addWidget(StrongBodyLabel(title), 0, column)
        self.rows = [ClipRow(self, clip) for clip in clips]
        for index, row in enumerate(self.rows):
            line = 1 + index * 2
            for column, widget in enumerate(row.widgets()):
                self.grid.addWidget(widget, line, column)
            self.grid.addWidget(row.problem, line + 1, 2)
        self.grid.setRowStretch(1 + len(self.rows) * 2, 1)

    def _browse(self):
        folder = QFileDialog.getExistingDirectory(self, "Save clips to", self.folder.text())
        if folder:
            self.folder.setText(folder)

    def _accept(self):
        clips = self.session.clips()
        self.accepted.emit(list(zip(clips, self.session.clip_names(clips))), self.folder.text())


class ExportOverlay(QWidget):
    """Dims the window it covers and shows the export panel in a card."""

    def __init__(self, session, parent):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
        self.setObjectName("ExportOverlay")
        mask = QColor(0, 0, 0, 120)
        self.setStyleSheet(
            f"#ExportOverlay {{ background: rgba({mask.red()},{mask.green()},{mask.blue()},{mask.alpha()}); }}"
            f"#ExportCard {{ background: {theme.color('surface').name()};"
            f" border: 1px solid {theme.color('border').name()}; border-radius: 10px; }}")
        self.card = QWidget()
        self.card.setObjectName("ExportCard")
        self.card.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
        self.panel = ExportPanel(session)
        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(24, 20, 24, 20)
        card_layout.addWidget(self.panel)
        layout = QVBoxLayout(self)
        layout.addStretch(1)
        row = QHBoxLayout()
        row.addStretch(1)
        row.addWidget(self.card)
        row.addStretch(1)
        layout.addLayout(row)
        layout.addStretch(1)
        self.panel.cancelled.connect(self.close)
        self.panel.accepted.connect(lambda *_: self.close())
        parent.installEventFilter(self)
        self.setGeometry(parent.rect())

    def eventFilter(self, watched, event):
        if watched is self.parent() and event.type() == event.Type.Resize:
            self.setGeometry(self.parent().rect())
        return False
