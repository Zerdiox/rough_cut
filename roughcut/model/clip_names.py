"""Clip names, which become file names on export.

A clip is identified by its earliest marker. A name the user typed is stored
against that marker; any other name is worked out from the marker's name, so
renaming a marker flows into clips the user never renamed. Clip names never
write back to markers.
"""

FORBIDDEN_CHARACTERS = '\\/:*?"<>|'
RESERVED_NAMES = frozenset(
    ["CON", "PRN", "AUX", "NUL"]
    + [f"COM{n}" for n in range(1, 10)]
    + [f"LPT{n}" for n in range(1, 10)]
)


class ClipNames:
    def __init__(self):
        self._typed = {}  # earliest marker id -> name the user typed

    def rename(self, clip, name):
        self._typed[clip.key] = name

    def is_typed(self, clip):
        return clip.key in self._typed

    def default_name(self, recording, clip, position):
        marker_name = recording.marker(clip.key).name.strip()
        return marker_name or f"{recording.name} {position:02d}"

    def name(self, recording, clip, position):
        typed = self._typed.get(clip.key)
        return typed if typed is not None else self.default_name(recording, clip, position)

    def names_for(self, recording, clips):
        return [self.name(recording, clip, position) for position, clip in enumerate(clips, start=1)]


def name_problems(names):
    """One problem message per name, or None where the name can be used as a file name."""
    seen = {}
    for index, name in enumerate(names):
        seen.setdefault(name.casefold(), []).append(index)

    problems = []
    for index, name in enumerate(names):
        problems.append(_problem(name) or _duplicate_problem(seen[name.casefold()], index))
    return problems


def _problem(name):
    if not name.strip():
        return "Give this clip a name"
    bad = sorted({c for c in name if c in FORBIDDEN_CHARACTERS or ord(c) < 32}, key=name.index)
    if bad:
        shown = " ".join(c if ord(c) >= 32 else "control character" for c in bad)
        return f"Windows doesn't allow {shown} in file names"
    if name[-1] in " .":
        return "Can't end with a space or a dot"
    base = name.split(".", 1)[0].rstrip().upper()
    if base in RESERVED_NAMES:
        return f"{base} is a name Windows reserves"
    return None


def _duplicate_problem(indexes, index):
    others = [i + 1 for i in indexes if i != index]
    if not others:
        return None
    return "Same name as clip " + ", ".join(str(i) for i in others)
