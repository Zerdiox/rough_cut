"""Every story module, in the order they appear in the gallery."""

import importlib

MODULES = [
    "foundations",
    "timeline",
    "components",
    "screens",
]


def load():
    """Import every story module so its stories register; returns the registry."""
    for name in MODULES:
        importlib.import_module(f"{__name__}.{name}")
    from roughcut.gallery.registry import REGISTRY

    return REGISTRY
