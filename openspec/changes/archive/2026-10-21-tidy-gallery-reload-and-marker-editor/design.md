# Design

## Context

The gallery watches every `.py` file under `roughcut/` and, after a short debounce, drops RoughCut's
modules from Python's module cache and rebuilds the shown story. Five modules are kept: the
`roughcut` and `roughcut.gallery` packages, the gallery window, the file watcher and the entry
point (the "shell"). They are the running window and watcher, so they can't be swapped out from
under themselves. The gallery is started by `gallery.bat` through `pythonw`, which has no console:
anything printed to stderr is lost.

The marker editor reloads all its fields on `selectionChanged`. The name and note fields push every
keystroke to the session, which then emits `changed`.

## Goals / Non-Goals

**Goals:**
- A shell save behaves like any other save from the user's point of view: the change shows up on
  the same story and theme, and a broken file shows its error instead of closing the gallery.
- The marker editor stays in step with the session without fighting the user's typing.

**Non-Goals:**
- Reloading the shell inside the running process.
- Keeping the window's position and size across a restart; it opens maximized as from
  `gallery.bat`.

## Decisions

### Restart the gallery process for shell saves
On a shell save the gallery starts a new gallery process with `--story` and `--theme` set to the
current story and theme, then quits. The new process loads every file fresh, including the entry
point.

Alternative: reload the shell modules and swap in a new window in the same process. That keeps the
window from blinking, but a reloaded class leaves old instances, signal connections and class
identities behind, and a change to the entry point would still not take effect.

### Tell a shell save apart by content, not by event
The watcher reports that something changed, not reliably what (editors save by replacing files,
which shows up as directory changes). The gallery keeps the contents of the shell files as they were
when it started, and on each change compares them with the files on disk. A difference means a shell
save; otherwise it reloads the story in place as today. Comparing contents also ignores saves that
change nothing.

### Check the new shell in a child process first
Before restarting, the gallery runs a short child process with the same Python that imports the
shell modules, and reads its exit code and error output. Only a clean exit leads to a restart. A
failure shows the child's error on the stage, the way a broken story is shown, and the gallery keeps
running on its previous shell. The next save that changes the shell again runs a new check.

The child runs asynchronously (`QProcess`), because importing PySide6 and QFluentWidgets takes about
a second and the window should stay usable meanwhile. A save that arrives while a check is running
starts a fresh check once the running one ends, so the latest files are what gets checked.

Alternative: compile the files only (`py_compile`). Cheaper, but misses import errors such as a
renamed function, which are the common breakage.

### Start the new gallery detached, from the project folder
The new process is started detached with the same interpreter (`pythonw` when launched from
`gallery.bat`) as `-m roughcut.gallery`, in the folder that holds the `roughcut` package, so it
resolves the package the same way regardless of where the old one was started. The story is passed
as "Group/Component/State", which is safe because the registry already refuses "/" in story names. Once the new process has started, the old one leaves with `exit(0)` rather than `quit()`: in Qt 6
`quit()` only asks every window to close and is dropped if one declines, which left old galleries
running beside new ones. It also stops reacting to saves before running its restart code, so a
gallery never starts more than one successor, even if it lingers.

That restart code is itself part of the shell being edited: a save can leave it valid Python but
broken (`started // result[0]`), so the import check passes and the next restart starts a new gallery
and then fails before the old one leaves. So the new gallery also ends the old one: the old passes its
process id as `--replace`, and the new gallery, running the freshly checked code, ends that process
once its window is shown, but only if it is still a running Python process, since process ids are
reused. A gallery started by hand gets no `--replace` and ends nothing. If starting the new process fails, the gallery shows that as an error
and stays open.

### Marker editor refreshes on `changed` and sets only what differs
The marker editor also refreshes on `changed`, and for each field compares the marker's value with
what the field shows, setting it only when they differ. While the user types, the field already
holds the new text by the time `changed` arrives, so it is left alone and the cursor doesn't move.
A change from elsewhere differs, so it is shown. The color dot follows through the same refresh, so
picking a color no longer sets the dot separately.

Alternative: ignore `changed` while a field has focus. Simpler, but a change made elsewhere while
the user is in the field (an undo, say) would then not show.

## Risks / Trade-offs

- [The gallery blinks on a shell save, and opens maximized even if it was resized] → Shell saves are
  rare; acceptable for a design tool.
- [A shell save could restart the gallery repeatedly if the new gallery sees its own start as a
  change] → The new process takes its own snapshot at start, so only later saves count.
- [Restarting from a console-started gallery leaves the console without the new process' output] →
  Only affects `python -m roughcut.gallery` from a terminal; the gallery itself works.
- [A broken shell file only shows its error in the old window; if the old gallery was closed
  meanwhile, nothing shows] → Restarting by hand after fixing it is the same as today.
