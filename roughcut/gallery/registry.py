"""Stories: small functions that build one widget, or one whole screen, from made-up data."""

from dataclasses import dataclass
from typing import Callable

GROUPS = ("Foundations", "Components", "Screens")


@dataclass(frozen=True)
class Story:
    group: str
    component: str
    state: str
    build: Callable

    @property
    def key(self):
        return (self.group, self.component, self.state)

    @property
    def title(self):
        return " / ".join(self.key)


class Registry:
    def __init__(self):
        self._stories = []

    def add(self, group, component, state, build):
        if group not in GROUPS:
            raise ValueError(f"group must be one of {GROUPS}, not {group!r}")
        if any("/" in part for part in (component, state)):
            raise ValueError(f"story names can't contain '/', which separates them in --story")
        story = Story(group, component, state, build)
        if any(existing.key == story.key for existing in self._stories):
            raise ValueError(f"story {story.title!r} is registered twice")
        self._stories.append(story)
        return story

    def all(self):
        return [story for group in GROUPS for story in self._stories if story.group == group]

    def grouped(self):
        """{group: {component: [story, ...]}}, groups in GROUPS order, the rest in registration order."""
        tree = {}
        for story in self.all():
            tree.setdefault(story.group, {}).setdefault(story.component, []).append(story)
        return tree

    def find(self, key):
        for story in self._stories:
            if story.key == tuple(key):
                return story
        return None


REGISTRY = Registry()


def story(group, component, state):
    """Register the decorated function as a story; it takes no arguments and returns a widget."""
    def register(build):
        REGISTRY.add(group, component, state, build)
        return build
    return register


def build_all(stories):
    """Build and discard every story; return (story, exception) for each that failed."""
    failures = []
    for each in stories:
        try:
            widget = each.build()
            widget.deleteLater()
        except Exception as error:  # a broken story must not hide the others
            failures.append((each, error))
    return failures
