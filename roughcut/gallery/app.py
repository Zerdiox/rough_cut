"""The gallery window: a story tree on the left, the selected story on the right."""

import importlib
import os
import sys
import traceback

from PySide6.QtCore import QProcess, Qt, QTimer
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication, QFrame, QHBoxLayout, QPlainTextEdit, QScrollArea, QTreeWidgetItem, QVBoxLayout,
    QWidget,
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


def _start_new_gallery(args):
    """Start a fresh gallery with `args` and leave this one; False if it couldn't start.

    exit(), not quit(): quit() only asks the windows to close and is dropped if
    one declines, which left the old gallery running beside the new one.
    """
    result = QProcess.startDetached(sys.executable, args, str(reloading.ROOT.parent))
    started = result[0] if isinstance(result, tuple) else result
    if started:
        QApplication.exit(0)
    return started


class _StoryLayout(QVBoxLayout):
    """Lays out the story on the stage.

    Word-wrapped labels make a layout height-for-width, and the scroll area then
    sizes the story by its preferred height instead of letting it shrink to its
    minimum, so screens would scroll even when they fit.
    """

    def hasHeightForWidth(self):
        return False


class GalleryWindow(QWidget):
    def __init__(self, start_story=None, watch=True, replace_pid=None):
        super().__init__()
        self.replace_pid = replace_pid
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

        # A save to the gallery's own files restarts it, once a child process
        # has shown that the saved files load.
        self.shell = reloading.ShellSnapshot()
        self.check = reloading.ShellCheck(parent=self)
        self.check.finished.connect(self._shell_checked)
        self.restart = _start_new_gallery
        self.restarted = False

        self.reloader = None
        if watch:
            self.reloader = reloading.Reloader(parent=self)
            self.reloader.sourcesChanged.connect(self._sources_changed)

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

    def _sources_changed(self):
        if self.restarted:
            return  # the new gallery handles saves from here on
        if self.shell.changed():
            self.check.start()
        else:
            self.reload()

    def _shell_checked(self, ok, error):
        if self.restarted:
            return
        if not ok:
            self._clear_stage()
            self._show_error("The gallery window failed to load", error,
                             "Fix the file and save; the gallery restarts on its own.")
            return
        args = ["-m", "roughcut.gallery", "--theme", "dark" if isDarkTheme() else "light",
                "--replace", str(os.getpid())]
        if self.current_key:
            args += ["--story", "/".join(self.current_key)]
        # Set before restarting: the restart code is itself part of what gets
        # edited, and if it raises after starting a new gallery, this one must
        # still never start another.
        self.restarted = True
        try:
            started = self.restart(args)
        except Exception:
            self._clear_stage()
            self._show_error("The gallery couldn't restart", traceback.format_exc(),
                             "A new gallery may have opened anyway. Close this one.")
            return
        if not started:
            self.restarted = False
            self._clear_stage()
            self._show_error("The gallery couldn't restart",
                             "Starting a new gallery failed.", "Close this one and start it again.")

    def showEvent(self, event):
        super().showEvent(event)
        if self.replace_pid is not None:
            # The gallery this one replaces normally leaves by itself; ending it
            # here covers one whose restart code was broken by the edit.
            pid, self.replace_pid = self.replace_pid, None
            QTimer.singleShot(0, lambda: reloading.end_process(pid))

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

    def _show_error(self, title, text, hint="Fix the file and save; the story comes back on its own."):
        theme = _theme()
        self.stage_title.setText(title)
        self.stage_hint.setText(hint)
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
