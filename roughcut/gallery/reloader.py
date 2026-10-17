"""Watches the roughcut sources and tells the gallery when to rebuild.

Rebuilding drops every roughcut module except the gallery shell from
sys.modules, so the next import of a story builds it from the saved files.
The shell itself (window, reloader, entry point) is not reloaded; changes to
it need a restart.
"""

import sys
from pathlib import Path

from PySide6.QtCore import QFileSystemWatcher, QObject, QTimer, Signal

ROOT = Path(__file__).resolve().parents[1]
SHELL = frozenset({
    "roughcut",
    "roughcut.gallery",
    "roughcut.gallery.app",
    "roughcut.gallery.reloader",
    "roughcut.gallery.__main__",
})


def purge():
    for name in list(sys.modules):
        if (name == "roughcut" or name.startswith("roughcut.")) and name not in SHELL:
            del sys.modules[name]


class Reloader(QObject):
    sourcesChanged = Signal()

    def __init__(self, root=ROOT, debounce_ms=300, parent=None):
        super().__init__(parent)
        self._root = Path(root)
        self._watcher = QFileSystemWatcher(self)
        self._timer = QTimer(self, singleShot=True, interval=debounce_ms)
        self._timer.timeout.connect(self._fire)
        self._watcher.fileChanged.connect(self._timer.start)
        self._watcher.directoryChanged.connect(self._timer.start)
        self._watch()

    def _watch(self):
        # Editors often save by replacing the file, which drops it from the
        # watcher, so the full set is re-added after every change.
        paths = [str(p) for p in self._root.rglob("*.py") if "__pycache__" not in p.parts]
        paths += [str(p) for p in self._root.rglob("*") if p.is_dir() and p.name != "__pycache__"]
        paths.append(str(self._root))
        missing = sorted(set(paths) - set(self._watcher.files()) - set(self._watcher.directories()))
        if missing:
            self._watcher.addPaths(missing)

    def _fire(self):
        self._watch()
        self.sourcesChanged.emit()
