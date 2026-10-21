---
id: F7
title: Test suite slowed from about 2 s to about 12 s
found: 2026-10-21
source: tidy-gallery-reload-and-marker-editor
capability: component-gallery
location: tests/test_gallery_restart.py
type: tech-debt
size: S
---

## What
The full test run went from about 2 s to 11–13 s. The new gallery restart and shell check tests
start real Python child processes (the import check, `end_process`) and build whole gallery windows.

## Why it matters
The suite gates every commit; a slower gate gets run less often. Growing the gallery tests the same
way will make it worse.

## Notes
The import check needs PySide6 and QFluentWidgets in the child, about a second each. Options: share
one gallery window per test class, or check the child process once with a lighter import and keep
the rest on fakes.
