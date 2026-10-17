---
id: F1
title: Release RoughCut as a single Windows binary via PyApp and GitHub Actions
found: 2026-10-13
source: conversation
capability:
location:
type: idea
size: M
---

## What
Ship RoughCut as one downloadable Windows executable, built with PyApp in a
GitHub Actions workflow and attached to a GitHub Release on
https://github.com/Zerdiox/rough_cut.

## Why it matters
Azzey should not need to install Python or manage dependencies to run
RoughCut. Without an automated pipeline, releases are manual and error-prone.

## Notes
- Blocked until there is an app to ship: today only the gallery runs and there
  is no app entry point. Promote once the editor runs on its own.
- Windows only: RoughCut is Windows-first with one user. Linux and macOS are
  deferred (see below).
- The repo is public, so release binaries can be downloaded by anyone, and
  Actions on `windows-latest` cost nothing. RoughCut is licensed GPLv3, so
  the release must include or point to the source and keep licence notices
  (the public repo covers source).
- Options considered: PyInstaller `--onefile` (truly self-contained, but
  hidden-import/`--add-data` friction and antivirus false positives), Nuitka
  (compiled, slow builds, needs a C compiler), zipapp/shiv/pex (needs Python on
  the user's machine), PyApp (preferred).
- PyApp (by the author of Hatch) is a small Rust launcher. On first run it
  unpacks a standalone Python, creates a venv and pip-installs the app into the
  user's data directory; later runs start directly.
  - Pros: real interpreter, so no freezing quirks; small binary unless
    embedding; `self update` / `self restore` / `self remove`; fewer AV flags;
    `hatch build -t binary` integration.
  - Cons: slower first launch; first run needs internet unless Python and the
    wheel are embedded (dependencies still come from PyPI); leaves an install
    on disk; build needs a Rust toolchain; source is not obfuscated.
- GitHub-hosted runners already include Rust (rustup/cargo).
  `dtolnay/rust-toolchain@stable` pins it if needed.
- Workflow plan:
  - Trigger on `v*` tags; `permissions: contents: write`.
  - One job on `windows-latest`: setup-python, `python -m build --wheel`, then
    `cargo install pyapp --version <pinned> --force --root out` with
    `PYAPP_PROJECT_PATH=<abs path to wheel>`, `PYAPP_EXEC_MODULE=roughcut`
    (or `PYAPP_EXEC_SPEC`), `PYAPP_DISTRIBUTION_EMBED=1`; rename
    `out/bin/pyapp.exe` to `RoughCut.exe`.
  - Attach it with `softprops/action-gh-release@v2` and
    `generate_release_notes: true`.
  - `cargo install pyapp` compiles from source, adding about 1–2 minutes.
- Prerequisites: a `pyproject.toml` that builds a wheel, and an entry point
  (`roughcut/__main__.py` or a console script). Neither exists yet.
- ffmpeg is not bundled; the app fetches it on first need (F2), so the binary
  stays single.
- Deferred:
  - Code signing for Windows SmartScreen (needs a certificate stored as a repo
    secret). Unsigned, SmartScreen warns on first run.
  - Linux and macOS builds: add `ubuntu-latest` / `macos-latest` to a matrix
    on native runners (and macOS Gatekeeper signing) if RoughCut ever leaves
    Windows. F2's lookup is Windows-specific too.
- Related: F2 (ffmpeg availability).
