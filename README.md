# RoughCut

A Windows desktop tool for cutting highlights out of OBS recordings. Mark the interesting moments
(OBS chapter markers, or in RoughCut itself, the way you would in DaVinci Resolve), adjust the clip
around each one, name the clips, and export each clip as its own file.

Right now RoughCut is a **gallery**: every piece of the interface shown on its own with made-up
recordings, so the layout can be agreed before the editor is wired to real video.

## Open the gallery

Double-click `gallery.bat`. The first run creates a Python environment in `.venv` and installs the
packages from `requirements.txt` (needs Python 3.14 and an internet connection); after that it opens
straight away.

From a terminal, with the environment active:

```
python -m roughcut.gallery
python -m roughcut.gallery --story "Components/Timeline/merged windows" --theme dark
```

While the gallery is open, saving any file under `roughcut/` redraws the story you're looking at.
If a change breaks a story, the error shows in its place until the file is fixed and saved again.
Saving the gallery window itself (`roughcut/gallery/app.py`, `reloader.py`, `__main__.py`) restarts
the gallery on the same story and theme; if the saved file doesn't load, the error shows instead and
the gallery stays open until it's fixed.

## Tests

```
python -m unittest discover -s tests
```

## Licence

RoughCut is free software under the GNU General Public License v3.0; see [LICENSE](LICENSE).
