#!/usr/bin/env python3
"""Prepare a patch release when WoW Forever's TOC interface changes."""

from __future__ import annotations

import argparse
import re
import urllib.request
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from release import next_patch, replace_release_files

ROOT = Path(__file__).resolve().parents[1]
VERSIONS_URL = "https://us.version.battle.net/v2/products/wow_classic_beta/versions"
TOC_NAME = "ForeverAutoFog.toc"
GAME_VERSION_RE = re.compile(r"^(\d+)\.(\d+)\.(\d+)\.(\d+)$")


@dataclass(frozen=True)
class GameBuild:
    version: str
    interface: int


def interface_from_version(version: str) -> int:
    match = GAME_VERSION_RE.fullmatch(version)
    if not match:
        raise ValueError(f"Invalid WoW Forever game version: {version}")
    major, minor, patch, _ = (int(part) for part in match.groups())
    return int(f"{major}{minor:02d}{patch:02d}")


def parse_versions(text: str, region: str = "us") -> GameBuild:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    headers = [field.split("!", 1)[0] for field in lines[0].split("|")]
    for line in lines[1:]:
        values = line.split("|")
        if len(values) != len(headers):
            continue
        row = dict(zip(headers, values, strict=True))
        if row.get("Region") == region:
            version = row["VersionsName"]
            return GameBuild(version, interface_from_version(version))
    raise ValueError(f"Blizzard version feed has no {region!r} region")


def update(root: Path, build: GameBuild, date: str, dry_run: bool = False) -> bool:
    toc_path = root / TOC_NAME
    toc = toc_path.read_text(encoding="utf-8")
    if re.search(rf"^## Interface: {build.interface}$", toc, re.M):
        return False
    toc = re.sub(r"^## Interface: .+$", f"## Interface: {build.interface}", toc, count=1, flags=re.M)
    if not dry_run:
        toc_path.write_text(toc, encoding="utf-8")
        version = next_patch((root / "VERSION").read_text(encoding="utf-8"))
        replace_release_files(
            root, version, date,
            f"Update WoW Forever compatibility for game build {build.version} (Interface {build.interface}).",
        )
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--versions-file", type=Path)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--date", default=datetime.now(UTC).date().isoformat())
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    text = args.versions_file.read_text(encoding="utf-8") if args.versions_file else urllib.request.urlopen(VERSIONS_URL, timeout=30).read().decode()
    changed = update(args.root, parse_versions(text), args.date, args.dry_run)
    print("updated" if changed else "already current")


if __name__ == "__main__":
    main()
