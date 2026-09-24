#!/usr/bin/env python3
"""Shared release-file helpers for Forever Auto Fog."""

from __future__ import annotations

import re
from pathlib import Path

VERSION_RE = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")


def next_patch(version: str) -> str:
    match = VERSION_RE.fullmatch(version.strip())
    if not match:
        raise ValueError(f"Invalid version: {version!r}")
    major, minor, patch = (int(value) for value in match.groups())
    return f"{major}.{minor}.{patch + 1}"


def replace_release_files(root: Path, version: str, date: str, summary: str) -> None:
    changelog_entry = f"## {version} - {date}\n\n- {summary}\n"
    changelog_path = root / "CHANGELOG.md"
    changelog = changelog_path.read_text(encoding="utf-8")
    first_release = re.search(r"^## \d+\.\d+\.\d+", changelog, re.M)
    if not first_release:
        raise ValueError("CHANGELOG.md has no release heading")
    changelog_path.write_text(
        changelog[:first_release.start()] + changelog_entry + "\n" + changelog[first_release.start():],
        encoding="utf-8",
    )
    (root / "VERSION").write_text(f"{version}\n", encoding="utf-8")
    (root / "RELEASE_NOTES.md").write_text(changelog_entry, encoding="utf-8")
