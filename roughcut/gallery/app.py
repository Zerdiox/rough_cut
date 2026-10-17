"""The gallery window: a story tree on the left, the selected story on the right."""

import importlib
import traceback

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QPlainTextEdit, QScrollArea, QTreeWidgetItem, QVBoxLayout, QWidget,
)
from qfluentwidgets import (
    BodyLabel, CaptionLabel, StrongBodyLabel, SwitchButton, Theme, TitleLabel, TreeWidget,
    isDarkTheme, setTheme,
)

from roughcut.gallery import reloader as reloading

KEY_ROLE = Qt.ItemDataRole.UserRole


def _theme():
    # Imported on use so a saved change to the tokens shows after a reload.
    return importlib.import_module("roughcut.ui.theme")


class _StoryLayout(QVBoxLayout):
    """Lays out the story on the stage.

    Word-wrapped labels make a layout height-for-width, and the scroll area then
    sizes the story by its preferred height instead of letting it shrink to its
    minimum, so screens would scroll even when they fit.
    """

    def hasHeightForWidth(self):
        return False


class GalleryWindow(QWidget):
    def __init__(self, start_story=None, watch=True):
        super().__init__()
        self.setObjectName("GalleryWindow")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
        self.setWindowTitle("RoughCut Gallery")
        self.resize(1440, 900)

        self.registry = None
        self.current_key = tuple(start_story) if start_story else None
        self.story_widget = None

        self.title = TitleLabel("RoughCut Gallery")
        self.theme_label = CaptionLabel("Dark theme")
        self.theme_switch = SwitchButton()
        self.theme_switch.setOnText("")
        self.theme_switch.setOffText("")
        self.theme_switch.setChecked(isDarkTheme())
        self.theme_switch.checkedChanged.connect(self._set_dark)

        top = QHBoxLayout()
        top.setContentsMargins(20, 14, 20, 10)
        top.addWidget(self.title)
        top.addStretch(1)
        top.addWidget(self.theme_label)
        top.addWidget(self.theme_switch)

        self.tree = TreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setFixedWidth(270)
        self.tree.itemClicked.connect(self._item_clicked)

        self.stage_title = StrongBodyLabel()
        self.stage_hint = CaptionLabel()
        self.stage = QScrollArea()
        self.stage.setWidgetResizable(True)
        self.stage.setFrameShape(QFrame.Shape.NoFrame)

        stage_column = QVBoxLayout()
        stage_column.setContentsMargins(0, 0, 0, 0)
        stage_column.setSpacing(4)
        stage_column.addWidget(self.stage_title)
        stage_column.addWidget(self.stage_hint)
        stage_column.addWidget(self.stage, 1)

        body = QHBoxLayout()
        body.setContentsMargins(12, 0, 20, 16)
        body.setSpacing(16)
        body.addWidget(self.tree)
        body.addLayout(stage_column, 1)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.addLayout(top)
        root.addLayout(body, 1)

        self.reloader = None
        if watch:
            self.reloader = reloading.Reloader(parent=self)
            self.reloader.sourcesChanged.connect(self.reload)

        self.reload()

    # stories

    def reload(self):
        self._clear_stage()
        reloading.purge()
        try:
            self.registry = importlib.import_module("roughcut.gallery.stories").load()
        except Exception:
            # Keep the tree as it was so the same story comes back once the file is fixed.
            self.registry = None
            self._show_error("The stories failed to load", traceback.format_exc())
            return
        self._fill_tree()
        stories = self.registry.all()
        if self.registry.find(self.current_key or ()) is None:
            self.current_key = stories[0].key if stories else None
        self._show_current()

    def show_story(self, key):
        self.current_key = tuple(key)
        self._show_current()

    def _show_current(self):
        self._clear_stage()
        self._apply_window_style()
        story = self.registry.find(self.current_key) if self.registry and self.current_key else None
        self._select_in_tree(self.current_key)
        if story is None:
            self.stage_title.setText("No stories yet")
            self.stage_hint.setText("")
            return
        self.stage_title.setText(story.title)
        self.stage_hint.setText("Made-up data. Save a file to see the change here.")
        try:
            widget = story.build()
        except Exception:
            self._show_error(f"{story.title} failed to build", traceback.format_exc())
            return
        self._set_stage_widget(widget)

    def _set_stage_widget(self, widget):
        frame = QWidget()
        frame.setObjectName("StoryFrame")
        frame.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
        layout = _StoryLayout(frame)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.addWidget(widget)
        layout.addStretch(1)
        self.story_widget = widget
        self.stage.setWidget(frame)

    def _show_error(self, title, text):
        theme = _theme()
        self.stage_title.setText(title)
        self.stage_hint.setText("Fix the file and save; the story comes back on its own.")
        box = QPlainTextEdit(text)
        box.setReadOnly(True)
        box.setFont(QFont("Consolas", 10))
        box.setStyleSheet(
            f"QPlainTextEdit {{ color: {theme.color('error').name()};"
            f" background: {theme.color('error_fill').name()}; border: none; padding: 12px; }}"
        )
        box.setMinimumHeight(400)
        self._set_stage_widget(box)

    def _clear_stage(self):
        old = self.stage.takeWidget()
        if old is not None:
            old.deleteLater()
        self.story_widget = None

    # tree

    def _fill_tree(self):
        self.tree.clear()
        if self.registry is None:
            return
        for group, components in self.registry.grouped().items():
            group_item = QTreeWidgetItem([group])
            group_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
            self.tree.addTopLevelItem(group_item)
            for component, stories in components.items():
                component_item = QTreeWidgetItem([component])
                component_item.setData(0, KEY_ROLE, stories[0].key)
                group_item.addChild(component_item)
                for each in stories:
                    state_item = QTreeWidgetItem([each.state])
                    state_item.setData(0, KEY_ROLE, each.key)
                    component_item.addChild(state_item)
        self.tree.expandAll()

    def _item_clicked(self, item):
        key = item.data(0, KEY_ROLE)
        if key:
            self.show_story(key)

    def _select_in_tree(self, key):
        if key is None:
            return
        for item in self._tree_items():
            if item.childCount() == 0 and item.data(0, KEY_ROLE) == tuple(key):
                self.tree.setCurrentItem(item)
                return

    def _tree_items(self):
        stack = [self.tree.topLevelItem(i) for i in range(self.tree.topLevelItemCount())]
        while stack:
            item = stack.pop()
            yield item
            stack.extend(item.child(i) for i in range(item.childCount()))

    # theme

    def _set_dark(self, dark):
        setTheme(Theme.DARK if dark else Theme.LIGHT)
        self._show_current()

    def _apply_window_style(self):
        theme = _theme()
        self.setStyleSheet(
            f"#GalleryWindow {{ background: {theme.color('surface_alt').name()}; }}"
            f"#StoryFrame {{ background: {theme.color('surface').name()};"
            f" border: 1px solid {theme.color('border').name()}; border-radius: 8px; }}"
            "QScrollArea { background: transparent; }"
            "QScrollArea > QWidget > QWidget { background: transparent; }"
        )
