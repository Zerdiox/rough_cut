"""python -m roughcut.gallery [--story "Group/Component/State"] [--theme light|dark]"""

import os
import sys

# Started with pythonw (gallery.bat) there is no console, so stdout and stderr
# are None and the first print, such as QFluentWidgets' banner on import, would
# crash the gallery before its window opens.
if sys.stdout is None:
    sys.stdout = open(os.devnull, "w")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w")

import argparse  # noqa: E402

from PySide6.QtWidgets import QApplication  # noqa: E402
from qfluentwidgets import Theme, setTheme  # noqa: E402

from roughcut.gallery.app import GalleryWindow  # noqa: E402


def main(argv=None):
    parser = argparse.ArgumentParser(prog="python -m roughcut.gallery")
    parser.add_argument("--story", help='open this story first, e.g. "Components/Timeline/merged windows"')
    parser.add_argument("--theme", choices=["light", "dark"], default="light")
    args = parser.parse_args(argv)

    app = QApplication(sys.argv[:1])
    setTheme(Theme.DARK if args.theme == "dark" else Theme.LIGHT)
    window = GalleryWindow(start_story=args.story.split("/") if args.story else None)
    window.showMaximized()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
