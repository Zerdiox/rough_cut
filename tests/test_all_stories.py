import unittest

import qt
from roughcut.gallery.registry import build_all


class AllStoriesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = qt.app()

    def test_every_registered_story_builds(self):
        from roughcut.gallery import stories

        registry = stories.load()
        failures = build_all(registry.all())
        self.assertEqual([f"{story.title}: {error!r}" for story, error in failures], [])


if __name__ == "__main__":
    unittest.main()
