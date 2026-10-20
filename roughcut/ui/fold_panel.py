"""A side panel section that folds to a one-line header showing its current state."""

from PySide6.QtCore import QRectF, QSize, Qt, Signal
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QAbstractButton, QHBoxLayout, QVBoxLayout, QWidget
from qfluentwidgets import CaptionLabel, FluentIcon, IconWidget, StrongBodyLabel

from roughcut.ui import theme


class ElidedLabel(CaptionLabel):
    """A caption that cuts its text with "..." to whatever width the layout gives it."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.full_text = ""
        self.setMinimumWidth(0)

    def set_full_text(self, text):
        self.full_text = text
        self.setToolTip(text)
        self._elide()

    def _elide(self):
        metrics = self.fontMetrics()
        self.setText(metrics.elidedText(self.full_text, Qt.TextElideMode.ElideRight, self.width()))

    def minimumSizeHint(self):
        return QSize(0, super().minimumSizeHint().height())

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._elide()


class FoldHeader(QAbstractButton):
    """Chevron, title and state text; clicking anywhere on it folds or opens the panel."""

    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.title = title
        self.state = ""
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.chevron = IconWidget(FluentIcon.CHEVRON_RIGHT_MED)
        self.chevron.setFixedSize(12, 12)
        self.title_label = StrongBodyLabel(title)
        self.state_label = ElidedLabel()
        self.state_label.setStyleSheet(f"color: {theme.color('text_muted').name()};")
        self.state_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        for child in (self.chevron, self.title_label, self.state_label):
            child.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 6, 4, 6)
        layout.setSpacing(8)
        layout.addWidget(self.chevron)
        layout.addWidget(self.title_label)
        layout.addWidget(self.state_label, 1)

    def set_open(self, is_open):
        self.chevron.setIcon(FluentIcon.CHEVRON_DOWN_MED if is_open else FluentIcon.CHEVRON_RIGHT_MED)

    def set_state(self, text):
        self.state = text
        self.state_label.set_full_text(text)

    def paintEvent(self, event):
        if not self.underMouse():
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(theme.color("track"))
        painter.drawRoundedRect(QRectF(self.rect()), 4, 4)

    def enterEvent(self, event):
        super().enterEvent(event)
        self.update()

    def leaveEvent(self, event):
        super().leaveEvent(event)
        self.update()


class FoldPanel(QWidget):
    """A header above a body; `summary(session)` gives the header's state text."""

    toggled = Signal(bool)

    def __init__(self, title, body, session, summary, folded=False, parent=None):
        super().__init__(parent)
        self.session = session
        self.summary = summary
        self.body = body
        self.header = FoldHeader(title)
        self.header.clicked.connect(lambda: self.set_open(not self.is_open()))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        layout.addWidget(self.header)
        layout.addWidget(body)

        self._open = not folded
        body.setHidden(folded)
        self.header.set_open(self._open)

        session.changed.connect(self.refresh)
        session.selectionChanged.connect(self.refresh)
        self.refresh()

    def is_open(self):
        return self._open

    def set_open(self, is_open):
        if is_open == self._open:
            return
        self._open = is_open
        self.body.setHidden(not is_open)
        self.header.set_open(is_open)
        self.toggled.emit(is_open)

    def refresh(self):
        self.header.set_state(self.summary(self.session))
