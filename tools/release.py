#!/usr/bin/env python3
"""Shared release-file helpers for Forever Auto Fog."""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION_RE = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")


@dataclass(frozen=True, order=True)
class Version:
    major: int
    minor: int
    patch: int

    @classmethod
    def parse(cls, value: str) -> Version:
        match = VERSION_RE.fullmatch(value.strip())
        if not match:
            raise ValueError(f"Invalid stable version: {value!r}")
        return cls(*(int(part) for part in match.groups()))

    def next_patch(self) -> Version:
        return Version(self.major, self.minor, self.patch + 1)

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"


def release_notes(entry: str, version: Version) -> str:
    """Return validated notes containing only the current release entry."""
    notes = entry.rstrip() + "\n"
    validate_release_notes(notes, version)
    return notes


def validate_release_notes(notes: str, version: Version) -> None:
    """Require current-version, single-release notes without email addresses."""
    headings = re.findall(r"^## (\d+\.\d+\.\d+)(?:\s+[-—].*)?$", notes, re.MULTILINE)
    if headings != [str(version)]:
        raise ValueError(
            f"RELEASE_NOTES.md must contain exactly one release heading for {version}"
        )
    if EMAIL_RE.search(notes):
        raise ValueError("RELEASE_NOTES.md must not contain email addresses")


def replace_or_insert_changelog_entry(
    changelog: str, version: Version, entry: str
) -> str:
    """Insert a release entry, or refresh the matching prepared entry."""
    version_heading = re.compile(
        rf"^## {re.escape(str(version))}(?:\s+[-—].*)?\n.*?(?=^## |\Z)",
        re.MULTILINE | re.DOTALL,
    )
    if version_heading.search(changelog):
        return version_heading.sub(entry.rstrip() + "\n\n", changelog, count=1)

    first_release = re.search(r"^## \d+\.\d+\.\d+", changelog, re.MULTILINE)
    if not first_release:
        raise ValueError("CHANGELOG.md has no release heading")
    return (
        changelog[: first_release.start()]
        + entry
        + "\n"
        + changelog[first_release.start() :]
    )


def write_interface_release(
    root: Path,
    version: Version,
    release_date: str,
    summary: str,
) -> None:
    """Bump VERSION and refresh CHANGELOG.md and RELEASE_NOTES.md."""
    entry = f"## {version} - {release_date}\n\n- {summary}\n"
    changelog_path = root / "CHANGELOG.md"
    changelog_path.write_text(
        replace_or_insert_changelog_entry(
            changelog_path.read_text(encoding="utf-8"),
            version,
            entry,
        ),
        encoding="utf-8",
    )
    (root / "VERSION").write_text(f"{version}\n", encoding="utf-8")
    (root / "RELEASE_NOTES.md").write_text(release_notes(entry, version), encoding="utf-8")


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_notes = subparsers.add_parser(
        "validate-notes", help="validate the current release notes"
    )
    validate_notes.add_argument("--version", required=True)
    validate_notes.add_argument("--root", type=Path, default=ROOT)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    if args.command == "validate-notes":
        validate_release_notes(
            (args.root / "RELEASE_NOTES.md").read_text(encoding="utf-8"),
            Version.parse(args.version),
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
