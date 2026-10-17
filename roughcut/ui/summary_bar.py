from PySide6.QtCore import Signal
from PySide6.QtWidgets import QHBoxLayout, QWidget
from qfluentwidgets import BodyLabel, FluentIcon, PrimaryPushButton

from roughcut.model.clips import total_length_ms
from roughcut.ui import theme


def summary_text(session):
    clips = session.clips()
    noun = "clip" if len(clips) == 1 else "clips"
    return f"{len(clips)} {noun}, {theme.format_length(total_length_ms(clips))} total"


class SummaryBar(QWidget):
    """What the export will produce, and the button to start it."""

    exportRequested = Signal()

    def __init__(self, session, parent=None):
        super().__init__(parent)
        self.session = session
        self.summary = BodyLabel()
        self.export_button = PrimaryPushButton(FluentIcon.SHARE, "Export")
        self.export_button.clicked.connect(self.exportRequested)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.addWidget(self.summary)
        layout.addStretch(1)
        layout.addWidget(self.export_button)

        session.changed.connect(self.refresh)
        self.refresh()

    def refresh(self):
        self.summary.setText(summary_text(self.session))
        has_clips = bool(self.session.clips())
        self.export_button.setEnabled(has_clips)
        self.export_button.setToolTip("" if has_clips else "Mark a moment and give it a clip window first")
