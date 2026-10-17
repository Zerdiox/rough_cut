from PySide6.QtWidgets import QHBoxLayout, QWidget
from qfluentwidgets import BodyLabel, CaptionLabel, FluentIcon, ToolButton, TransparentToolButton

from roughcut.ui import theme

# Shown for now so the layout has its real controls; playback wires them up.
NOT_YET = "Playback comes in a later version"


class TransportBar(QWidget):
    def __init__(self, session, parent=None):
        super().__init__(parent)
        self.session = session
        buttons = [
            (TransparentToolButton, FluentIcon.SKIP_BACK, "Previous marker (Shift+Up)"),
            (TransparentToolButton, FluentIcon.CARE_LEFT_SOLID, "Back (J)"),
            (ToolButton, FluentIcon.PLAY, "Play / pause (K)"),
            (TransparentToolButton, FluentIcon.CARE_RIGHT_SOLID, "Forward (L)"),
            (TransparentToolButton, FluentIcon.SKIP_FORWARD, "Next marker (Shift+Down)"),
        ]
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 0, 4, 0)
        layout.setSpacing(4)
        for button_class, icon, tip in buttons:
            button = button_class(icon)
            button.setToolTip(f"{tip}. {NOT_YET}.")
            layout.addWidget(button)
        layout.addSpacing(16)
        self.time = BodyLabel()
        layout.addWidget(self.time)
        layout.addStretch(1)
        keys = CaptionLabel("J K L  play    I O  clip in/out    M  marker")
        keys.setToolTip(NOT_YET)
        layout.addWidget(keys)
        session.changed.connect(self.refresh)
        self.refresh()

    def refresh(self):
        self.time.setText(
            f"{theme.format_time(self.session.playhead_ms)} / "
            f"{theme.format_time(self.session.recording.duration_ms)}")
