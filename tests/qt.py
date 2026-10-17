"""Shared Qt setup for tests: offscreen, one application for the whole run."""

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


def app():
    from PySide6.QtWidgets import QApplication

    return QApplication.instance() or QApplication([])
