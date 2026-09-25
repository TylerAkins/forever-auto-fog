#!/usr/bin/env python3
"""Tests for release notes and changelog helpers."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from release import (
    Version,
    release_notes,
    replace_or_insert_changelog_entry,
    validate_release_notes,
)


class ReleaseTests(unittest.TestCase):
    def test_release_notes_require_exactly_one_current_heading(self) -> None:
        version = Version.parse("0.1.2")
        entry = "## 0.1.2 - 2026-09-25\n\n- Summary.\n"
        notes = release_notes(entry, version)
        self.assertEqual(entry, notes)
        self.assertEqual(1, notes.count("## "))

        with self.assertRaisesRegex(ValueError, "exactly one release heading"):
            validate_release_notes("## 0.1.1 - 2026-09-24\n\n- Old.\n", version)

    def test_replace_or_insert_changelog_entry_is_idempotent(self) -> None:
        version = Version.parse("0.1.2")
        entry = "## 0.1.2 - 2026-09-25\n\n- New release.\n"
        changelog = "# Changelog\n\n## 0.1.1 - 2026-09-24\n\n- Prior.\n"

        updated = replace_or_insert_changelog_entry(changelog, version, entry)
        self.assertIn("## 0.1.2 - 2026-09-25", updated)
        self.assertLess(updated.index("## 0.1.2"), updated.index("## 0.1.1"))

        refreshed = replace_or_insert_changelog_entry(updated, version, entry)
        self.assertEqual(1, refreshed.count("## 0.1.2"))

    def test_pkgmeta_uses_release_notes_for_github_changelog(self) -> None:
        pkgmeta = (ROOT / ".pkgmeta").read_text(encoding="utf-8")
        self.assertIn("filename: RELEASE_NOTES.md", pkgmeta)
        self.assertIn("markup-type: markdown", pkgmeta)


if __name__ == "__main__":
    unittest.main()
