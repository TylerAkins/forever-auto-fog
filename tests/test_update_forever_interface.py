#!/usr/bin/env python3
"""Tests for automated WoW Forever interface updates."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from update_forever_interface import GameBuild, parse_versions, prepare_update

VERSIONS = """\
Region!STRING:0|BuildId!DEC:4|VersionsName!String:0
## seqn = 1
us|69913|1.60.1.69913
eu|69913|1.60.1.69913
"""


class ForeverInterfaceUpdateTests(unittest.TestCase):
    def test_parses_forever_build_and_interface(self) -> None:
        build = parse_versions(VERSIONS)

        self.assertEqual("1.60.1.69913", build.version)
        self.assertEqual(69913, build.build_id)
        self.assertEqual(16001, build.interface)

    def test_new_interface_prepares_patch_release_idempotently(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = self._repository_fixture(Path(temp_dir))
            build = GameBuild("1.60.2.70123", 70123, 16002)

            result = prepare_update(build, root=root, release_date="2026-09-23")

            self.assertTrue(result.changed)
            self.assertEqual("0.1.1", result.addon_version)
            self.assertIn(
                "## Interface: 16002",
                (root / "ForeverAutoFog.toc").read_text(encoding="utf-8"),
            )
            notes = (root / "RELEASE_NOTES.md").read_text(encoding="utf-8")
            self.assertIn("## 0.1.1 - 2026-09-23", notes)
            self.assertEqual(1, notes.count("## "))

            second = prepare_update(build, root=root)
            self.assertFalse(second.changed)

    def test_dry_run_reports_without_writing(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = self._repository_fixture(Path(temp_dir))
            before_toc = (root / "ForeverAutoFog.toc").read_text(encoding="utf-8")

            result = prepare_update(
                GameBuild("1.60.2.70123", 70123, 16002),
                root=root,
                release_date="2026-09-23",
                dry_run=True,
            )

            self.assertTrue(result.changed)
            self.assertEqual(before_toc, (root / "ForeverAutoFog.toc").read_text(encoding="utf-8"))

    @staticmethod
    def _repository_fixture(root: Path, *, interface: int = 16001) -> Path:
        (root / "ForeverAutoFog.toc").write_text(
            f"## Interface: {interface}\n## Version: @project-version@\n",
            encoding="utf-8",
        )
        (root / "VERSION").write_text("0.1.0\n", encoding="utf-8")
        (root / "CHANGELOG.md").write_text(
            "# Changelog\n\n## 0.1.0 - 2026-09-24\n\n- Initial release.\n",
            encoding="utf-8",
        )
        (root / "RELEASE_NOTES.md").write_text(
            "## 0.1.0 - 2026-09-24\n\n- Initial release.\n",
            encoding="utf-8",
        )
        return root


if __name__ == "__main__":
    unittest.main()
