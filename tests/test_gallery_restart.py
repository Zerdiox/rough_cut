import os
import subprocess
import sys
import unittest
from unittest import mock

import qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QPlainTextEdit
from qfluentwidgets import Theme, setTheme

from roughcut.gallery import app as app_module
from roughcut.gallery import reloader
from roughcut.gallery.app import GalleryWindow


class FakeShell:
    def __init__(self, changed):
        self._changed = changed

    def changed(self):
        return self._changed


class FakeCheck:
    """Reports a fixed result as soon as it is started."""

    def __init__(self, window, ok, error=""):
        self.window, self.ok, self.error = window, ok, error
        self.started = 0

    def start(self):
        self.started += 1
        self.window._shell_checked(self.ok, self.error)


class GalleryRestartTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = qt.app()

    def setUp(self):
        setTheme(Theme.DARK)
        self.addCleanup(setTheme, Theme.LIGHT)
        self.window = GalleryWindow(start_story=["Screens", "Main", "loaded"], watch=False)
        self.addCleanup(self.window.close)
        self.restarts = []
        self.restart_works = True
        self.window.restart = self._record_restart

    def _record_restart(self, args):
        self.restarts.append(args)
        return self.restart_works

    def save(self, shell_changed, ok=True, error=""):
        self.window.shell = FakeShell(shell_changed)
        self.window.check = FakeCheck(self.window, ok, error)
        self.window._sources_changed()

    def test_a_shell_save_that_loads_restarts_on_the_same_story_and_theme(self):
        self.save(shell_changed=True)
        self.assertEqual(self.window.check.started, 1)
        self.assertEqual(self.restarts, [[
            "-m", "roughcut.gallery", "--theme", "dark", "--replace", str(os.getpid()),
            "--story", "Screens/Main/loaded"]])

    def test_a_broken_shell_save_shows_the_error_and_stays(self):
        self.save(shell_changed=True, ok=False, error="SyntaxError: invalid syntax (app.py, line 3)")
        self.assertEqual(self.restarts, [])
        self.assertIsInstance(self.window.story_widget, QPlainTextEdit)
        self.assertIn("SyntaxError", self.window.story_widget.toPlainText())
        self.assertIn("gallery window", self.window.stage_title.text())
        self.assertIn("restarts", self.window.stage_hint.text())
        self.assertEqual(self.window.current_key, ("Screens", "Main", "loaded"))

    def test_a_story_save_reloads_in_place_without_a_check(self):
        before = self.window.story_widget
        self.save(shell_changed=False)
        self.assertEqual(self.window.check.started, 0)
        self.assertEqual(self.restarts, [])
        self.assertIsNot(self.window.story_widget, before)
        self.assertNotIsInstance(self.window.story_widget, QPlainTextEdit)

    def test_after_a_restart_further_saves_are_left_to_the_new_gallery(self):
        # A gallery that lingers after starting its successor must never start
        # another one, or every save multiplies the galleries.
        self.save(shell_changed=True)
        self.save(shell_changed=True)
        self.save(shell_changed=False)
        self.assertEqual(len(self.restarts), 1)
        self.assertEqual(self.window.check.started, 0)

    def test_a_restart_that_raises_shows_the_error_and_never_restarts_again(self):
        # The restart code is part of the gallery being edited: a save can
        # leave it broken (e.g. `started // result[0]`), and the next restart
        # may already have started a new gallery when it raises.
        def broken_restart(args):
            self.restarts.append(args)
            raise NameError("name 'started' is not defined")

        self.window.restart = broken_restart
        self.save(shell_changed=True)
        self.assertEqual(len(self.restarts), 1)
        self.assertIsInstance(self.window.story_widget, QPlainTextEdit)
        self.assertIn("NameError", self.window.story_widget.toPlainText())
        self.assertIn("restart", self.window.stage_title.text())
        self.save(shell_changed=True)
        self.save(shell_changed=False)
        self.assertEqual(len(self.restarts), 1)

    def test_a_restart_that_fails_to_start_shows_an_error(self):
        self.restart_works = False
        self.save(shell_changed=True)
        self.assertEqual(len(self.restarts), 1)
        self.assertIsInstance(self.window.story_widget, QPlainTextEdit)
        self.assertIn("restart", self.window.stage_title.text())
        self.assertIn("start it again", self.window.stage_hint.text())


class ReplaceOldGalleryTest(unittest.TestCase):
    """A restarted gallery ends the one it replaces, whatever state that one's code is in."""

    @classmethod
    def setUpClass(cls):
        cls.app = qt.app()

    def test_ends_the_old_gallery_once_shown(self):
        with mock.patch.object(app_module.reloading, "end_process") as end:
            window = GalleryWindow(watch=False, replace_pid=4321)
            self.addCleanup(window.close)
            end.assert_not_called()
            window.show()
            QTest.qWait(50)
        end.assert_called_once_with(4321)

    def test_a_gallery_started_by_hand_ends_nothing(self):
        with mock.patch.object(app_module.reloading, "end_process") as end:
            window = GalleryWindow(watch=False)
            self.addCleanup(window.close)
            window.show()
            QTest.qWait(50)
        end.assert_not_called()


class EndProcessTest(unittest.TestCase):
    def start(self, args):
        process = subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.addCleanup(lambda: process.poll() is None and process.kill())
        return process

    def test_ends_a_python_process(self):
        process = self.start([sys.executable, "-c", "import time; time.sleep(30)"])
        self.assertTrue(reloader.end_process(process.pid))
        self.assertIsNotNone(process.wait(timeout=10))

    def test_leaves_other_programs_alone(self):
        # Process ids are reused; a stale id must never end an unrelated program.
        process = self.start(["ping", "-n", "30", "127.0.0.1"])
        self.assertFalse(reloader.end_process(process.pid))
        self.assertIsNone(process.poll())

    def test_a_process_that_is_gone(self):
        process = self.start([sys.executable, "-c", "pass"])
        process.wait(timeout=10)
        self.assertFalse(reloader.end_process(process.pid))


class StartNewGalleryTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = qt.app()

    def test_exits_unconditionally_once_the_new_gallery_runs(self):
        # quit() only asks, and a window can turn it down; exit() can't be refused.
        with mock.patch.object(app_module.QProcess, "startDetached", return_value=(True, 1234)) as start, \
                mock.patch.object(app_module.QApplication, "exit") as exit_, \
                mock.patch.object(app_module.QApplication, "quit") as quit_:
            self.assertTrue(app_module._start_new_gallery(["-m", "roughcut.gallery"]))
        start.assert_called_once()
        exit_.assert_called_once_with(0)
        quit_.assert_not_called()

    def test_stays_when_the_new_gallery_doesnt_start(self):
        with mock.patch.object(app_module.QProcess, "startDetached", return_value=(False, 0)), \
                mock.patch.object(app_module.QApplication, "exit") as exit_:
            self.assertFalse(app_module._start_new_gallery(["-m", "roughcut.gallery"]))
        exit_.assert_not_called()


if __name__ == "__main__":
    unittest.main()
