#!/usr/bin/env python3
"""Copy the standalone OSCT skills into the all-in-one plugin."""

from __future__ import annotations

import argparse
import shutil
import stat
from pathlib import Path


root = Path(__file__).resolve().parents[1]
plugins = root / "plugins"
bundle = plugins / "osct" / "skills"
skill_names = (
    "osct-address-pr-comments",
    "osct-audit",
    "osct-docs",
    "osct-open-issue",
    "osct-open-pr",
    "osct-pr-review",
)
ignored_names = {".claude-plugin", ".codex-plugin", "__pycache__"}


def included_files(path: Path) -> dict[Path, tuple[bytes, bool]]:
    files: dict[Path, tuple[bytes, bool]] = {}
    for candidate in path.rglob("*"):
        relative = candidate.relative_to(path)
        if any(part in ignored_names for part in relative.parts) or not candidate.is_file():
            continue
        executable = bool(candidate.stat().st_mode & stat.S_IXUSR)
        files[relative] = (candidate.read_bytes(), executable)
    return files


def sync() -> None:
    for name in skill_names:
        source = plugins / name
        target = bundle / name
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(
            source,
            target,
            ignore=shutil.ignore_patterns(*ignored_names),
        )
        print(f"synced {name}")


def check() -> None:
    drifted = [
        name
        for name in skill_names
        if included_files(plugins / name) != included_files(bundle / name)
    ]
    if drifted:
        raise SystemExit("Codex bundle is out of date: " + ", ".join(drifted))
    print("Codex bundle is in sync")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail when bundled skills differ")
    args = parser.parse_args()
    check() if args.check else sync()


if __name__ == "__main__":
    main()
