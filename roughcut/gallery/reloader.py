"""Watches the roughcut sources and tells the gallery when to rebuild.

Rebuilding drops every roughcut module except the gallery shell from
sys.modules, so the next import of a story builds it from the saved files.
The shell itself (window, reloader, entry point) can't be swapped out while it
runs: a change to it is checked in a child process and then restarts the
gallery.
"""

import ctypes
import sys
from ctypes import wintypes
from pathlib import Path

from PySide6.QtCore import QFileSystemWatcher, QObject, QProcess, QTimer, Signal

ROOT = Path(__file__).resolve().parents[1]
SHELL = frozenset({
    "roughcut",
    "roughcut.gallery",
    "roughcut.gallery.app",
    "roughcut.gallery.reloader",
    "roughcut.gallery.__main__",
})


# Imported by the check before a restart; "roughcut" and "roughcut.gallery" come with them.
SHELL_MODULES = ("roughcut.gallery.app", "roughcut.gallery.reloader", "roughcut.gallery.__main__")
# The files behind SHELL, relative to ROOT.
SHELL_FILES = (
    "__init__.py",
    "gallery/__init__.py",
    "gallery/app.py",
    "gallery/reloader.py",
    "gallery/__main__.py",
)


def end_process(pid):
    """End the Python process `pid` if it is still running; True if it was ended.

    A restarted gallery ends the one it replaces, which may be running shell
    code broken badly enough that it can't leave by itself. Process ids get
    reused, so only a running python(w).exe is ended.
    """
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.OpenProcess.restype = wintypes.HANDLE
    query_limited_information, terminate, still_active = 0x1000, 0x0001, 259
    handle = kernel32.OpenProcess(query_limited_information | terminate, False, pid)
    if not handle:
        return False
    try:
        size = wintypes.DWORD(1024)
        image = ctypes.create_unicode_buffer(size.value)
        if not kernel32.QueryFullProcessImageNameW(handle, 0, image, ctypes.byref(size)):
            return False
        if Path(image.value).name.lower() not in ("python.exe", "pythonw.exe"):
            return False
        exit_code = wintypes.DWORD()
        if not kernel32.GetExitCodeProcess(handle, ctypes.byref(exit_code)) or exit_code.value != still_active:
            return False
        return bool(kernel32.TerminateProcess(handle, 1))
    finally:
        kernel32.CloseHandle(handle)


def purge():
    for name in list(sys.modules):
        if (name == "roughcut" or name.startswith("roughcut.")) and name not in SHELL:
            del sys.modules[name]


class ShellSnapshot:
    """The shell files as they were at start; `changed()` tells a shell save from any other.

    Contents, not modification times: editors save by replacing files, and a
    save that changes nothing shouldn't restart the gallery.
    """

    def __init__(self, root=ROOT):
        self._root = Path(root)
        self._contents = self._read()

    def _read(self):
        return {name: (self._root / name).read_bytes() if (self._root / name).exists() else None
                for name in SHELL_FILES}

    def changed(self):
        return self._read() != self._contents


class ShellCheck(QObject):
    """Imports the shell in a child process; `finished(ok, error)` says whether a restart would load.

    A child, so a broken save can't take the running gallery down, and
    asynchronous, since importing PySide6 and QFluentWidgets takes a second.
    A start while a check runs checks again once it ends, so the result is
    always for the files as last saved.
    """

    finished = Signal(bool, str)

    def __init__(self, cwd=ROOT.parent, modules=SHELL_MODULES, parent=None):
        super().__init__(parent)
        self._cwd = str(cwd)
        self._code = "import " + ", ".join(modules)
        self._again = False
        self._process = QProcess(self)
        self._process.setWorkingDirectory(self._cwd)
        self._process.finished.connect(self._done)

    def start(self):
        if self._process.state() != QProcess.ProcessState.NotRunning:
            self._again = True
            return
        self._process.start(sys.executable, ["-c", self._code])

    def _done(self, exit_code, exit_status):
        if self._again:
            self._again = False
            self.start()
            return
        error = bytes(self._process.readAllStandardError()).decode("utf-8", "replace")
        ok = exit_status == QProcess.ExitStatus.NormalExit and exit_code == 0
        self.finished.emit(ok, "" if ok else error.strip())


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
