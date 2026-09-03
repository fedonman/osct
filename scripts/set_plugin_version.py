#!/usr/bin/env python3
"""Set or check the shared version in every OSCT plugin manifest."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


repo_root = Path(__file__).resolve().parents[1]
stable_semver = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")
version_line = re.compile(
    r'(?m)^([ \t]*"version"[ \t]*:[ \t]*")[^"]+("[ \t]*,?[ \t]*)$'
)


def manifests() -> list[Path]:
    paths = sorted((repo_root / "plugins").glob("*/.claude-plugin/plugin.json"))
    paths.append(repo_root / "plugins/osct/.codex-plugin/plugin.json")
    missing = [path for path in paths if not path.is_file()]
    if missing:
        raise SystemExit("missing plugin manifest: " + ", ".join(map(str, missing)))
    return paths


def parse_version(value: str) -> tuple[int, int, int]:
    match = stable_semver.fullmatch(value)
    if match is None:
        raise SystemExit(f"invalid version {value!r}; expected MAJOR.MINOR.PATCH")
    return tuple(map(int, match.groups()))


def manifest_versions(paths: list[Path]) -> dict[Path, str]:
    versions: dict[Path, str] = {}
    for path in paths:
        payload = json.loads(path.read_text(encoding="utf-8"))
        value = payload.get("version")
        if not isinstance(value, str):
            raise SystemExit(f"{path} has no string version")
        parse_version(value)
        versions[path] = value
    return versions


def shared_version(versions: dict[Path, str]) -> str:
    values = set(versions.values())
    if len(values) != 1:
        details = ", ".join(f"{path}: {value}" for path, value in versions.items())
        raise SystemExit("plugin manifest versions differ: " + details)
    return values.pop()


def set_version(paths: list[Path], current: str, target: str) -> None:
    if parse_version(target) <= parse_version(current):
        raise SystemExit(f"new version {target} must be greater than {current}")

    for path in paths:
        text = path.read_text(encoding="utf-8")
        updated, replacements = version_line.subn(
            lambda match: f"{match.group(1)}{target}{match.group(2)}",
            text,
            count=1,
        )
        if replacements != 1:
            raise SystemExit(f"could not update exactly one version in {path}")
        path.write_text(updated, encoding="utf-8")
        print(f"updated {path.relative_to(repo_root)} to {target}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("version", nargs="?", help="stable semantic version without v")
    parser.add_argument("--check", action="store_true", help="check every manifest")
    parser.add_argument("--current", action="store_true", help="print the shared version")
    args = parser.parse_args()

    paths = manifests()
    versions = manifest_versions(paths)
    current = shared_version(versions)

    if args.current:
        if args.check or args.version is not None:
            parser.error("--current cannot be combined with a version or --check")
        print(current)
        return

    if args.version is None:
        parser.error("version is required unless --current is used")
    parse_version(args.version)

    if args.check:
        mismatched = [path for path, value in versions.items() if value != args.version]
        if mismatched:
            raise SystemExit(
                f"expected {args.version} in: "
                + ", ".join(str(path.relative_to(repo_root)) for path in mismatched)
            )
        print(f"all plugin manifests use {args.version}")
        return

    set_version(paths, current, args.version)


if __name__ == "__main__":
    main()
