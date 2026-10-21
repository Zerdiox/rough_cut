import shutil
import tempfile
import unittest
from pathlib import Path

import qt
from PySide6.QtTest import QTest

from roughcut.gallery import reloader


class ShellSnapshotTest(unittest.TestCase):
    """Telling a save to the gallery's own files apart from any other save."""

    @classmethod
    def setUpClass(cls):
        cls.app = qt.app()

    def setUp(self):
        temp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, temp)
        self.root = temp / "roughcut"
        shutil.copytree(reloader.ROOT, self.root, ignore=shutil.ignore_patterns("__pycache__"))
        self.snapshot = reloader.ShellSnapshot(self.root)

    def test_nothing_saved(self):
        self.assertFalse(self.snapshot.changed())

    def test_saving_a_shell_file_unchanged(self):
        app = self.root / "gallery" / "app.py"
        app.write_bytes(app.read_bytes())
        self.assertFalse(self.snapshot.changed())

    def test_saving_a_story_file(self):
        story = self.root / "gallery" / "stories" / "screens.py"
        story.write_text(story.read_text(encoding="utf-8") + "\n# changed\n", encoding="utf-8")
        self.assertFalse(self.snapshot.changed())

    def test_changing_each_shell_file(self):
        for name in ("__init__.py", "gallery/__init__.py", "gallery/app.py",
                     "gallery/reloader.py", "gallery/__main__.py"):
            with self.subTest(name):
                path = self.root / name
                original = path.read_bytes()
                path.write_bytes(original + b"\n# changed\n")
                self.assertTrue(self.snapshot.changed())
                path.write_bytes(original)
                self.assertFalse(self.snapshot.changed())


class ShellCheckTest(unittest.TestCase):
    """Importing the saved shell in a child process before restarting."""

    @classmethod
    def setUpClass(cls):
        cls.app = qt.app()

    def setUp(self):
        self.folder = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.folder)
        self.check = reloader.ShellCheck(cwd=self.folder, modules=["fake_shell"])
        self.results = []
        self.check.finished.connect(lambda ok, error: self.results.append((ok, error)))

    def write(self, text):
        (self.folder / "fake_shell.py").write_text(text, encoding="utf-8")

    def wait_for(self, count=1, timeout_ms=15_000):
        waited = 0
        while len(self.results) < count and waited < timeout_ms:
            QTest.qWait(20)
            waited += 20
        self.assertEqual(len(self.results), count, "the check didn't finish in time")

    def test_a_shell_that_loads(self):
        self.write("VALUE = 1\n")
        self.check.start()
        self.wait_for()
        self.assertEqual(self.results, [(True, "")])

    def test_a_syntax_error(self):
        self.write("def broken(:\n")
        self.check.start()
        self.wait_for()
        ok, error = self.results[0]
        self.assertFalse(ok)
        self.assertIn("SyntaxError", error)
        self.assertIn("fake_shell.py", error)

    def test_a_failing_import(self):
        self.write("from os import does_not_exist\n")
        self.check.start()
        self.wait_for()
        ok, error = self.results[0]
        self.assertFalse(ok)
        self.assertIn("ImportError", error)
        self.assertIn("does_not_exist", error)

    def test_a_save_during_a_check_is_checked_afterwards(self):
        # The first child has read this file and is still running it when the
        # fix is saved; only the fixed version's result is reported.
        self.write("import time\ntime.sleep(1.5)\nraise RuntimeError('old version')\n")
        self.check.start()
        QTest.qWait(700)
        self.write("VALUE = 1\n")
        self.check.start()
        self.wait_for()
        QTest.qWait(300)
        self.assertEqual(self.results, [(True, "")])


if __name__ == "__main__":
    unittest.main()
