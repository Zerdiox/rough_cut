import unittest

import qt
from roughcut.gallery.registry import Registry, build_all


def label(text):
    def build():
        from PySide6.QtWidgets import QLabel

        return QLabel(text)
    return build


def broken():
    raise RuntimeError("story is broken")


class RegistryTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = qt.app()

    def test_stories_list_grouped_and_in_order(self):
        registry = Registry()
        registry.add("Screens", "Main", "empty", label("main"))
        registry.add("Components", "Timeline", "empty", label("a"))
        registry.add("Components", "Timeline", "merged windows", label("b"))
        registry.add("Components", "Marker list", "few markers", label("c"))

        tree = registry.grouped()
        self.assertEqual(list(tree), ["Components", "Screens"])
        self.assertEqual(list(tree["Components"]), ["Timeline", "Marker list"])
        self.assertEqual([s.state for s in tree["Components"]["Timeline"]], ["empty", "merged windows"])

    def test_unknown_group_is_rejected(self):
        with self.assertRaises(ValueError):
            Registry().add("Widgets", "Timeline", "empty", label("a"))

    def test_slash_in_a_name_is_rejected(self):
        with self.assertRaises(ValueError):
            Registry().add("Components", "Handles", "20 s / 5 s", label("a"))

    def test_same_story_twice_is_rejected(self):
        registry = Registry()
        registry.add("Components", "Timeline", "empty", label("a"))
        with self.assertRaises(ValueError):
            registry.add("Components", "Timeline", "empty", label("b"))

    def test_find_by_key(self):
        registry = Registry()
        added = registry.add("Components", "Timeline", "empty", label("a"))
        self.assertIs(registry.find(("Components", "Timeline", "empty")), added)
        self.assertIsNone(registry.find(("Components", "Timeline", "missing")))

    def test_build_all_reports_broken_stories(self):
        registry = Registry()
        registry.add("Components", "Timeline", "fine", label("a"))
        bad = registry.add("Components", "Timeline", "broken", broken)
        failures = build_all(registry.all())
        self.assertEqual([story for story, _ in failures], [bad])


if __name__ == "__main__":
    unittest.main()
