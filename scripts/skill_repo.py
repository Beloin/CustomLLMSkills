#!/usr/bin/env python3
"""Manage the skills in this repository: list, install, uninstall.

    python3 scripts/skill_repo.py list
    python3 scripts/skill_repo.py install [skill ...]
    python3 scripts/skill_repo.py uninstall [skill ...]

Targets:
    claude    ~/.claude/skills/<name>          (CLAUDE_CONFIG_DIR overrides)
    opencode  ~/.config/opencode/skills/<name> (OPENCODE_CONFIG_DIR, XDG_CONFIG_HOME)

By default a skill is symlinked, so edits in this repository take effect
immediately. Use --mode copy for a standalone copy.
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _frontmatter import read as read_frontmatter  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO_ROOT / "skills"
TRASH_DIR = Path(
    os.environ.get("MY_SKILLS_TRASH", Path.home() / ".my-skills-trash")
)


def claude_dir() -> Path:
    override = os.environ.get("CLAUDE_CONFIG_DIR")
    return Path(override) if override else Path.home() / ".claude"


def opencode_dir() -> Path:
    override = os.environ.get("OPENCODE_CONFIG_DIR")
    if override:
        return Path(override)
    xdg = os.environ.get("XDG_CONFIG_HOME")
    base = Path(xdg) if xdg else Path.home() / ".config"
    return base / "opencode"


def target_dirs(target: str) -> list[Path]:
    if target == "claude":
        return [claude_dir() / "skills"]
    if target == "opencode":
        return [opencode_dir() / "skills"]
    if target == "both":
        return [claude_dir() / "skills", opencode_dir() / "skills"]
    raise SystemExit(f"unknown target: {target} (use claude, opencode, or both)")


def all_skills() -> list[str]:
    if not SKILLS_DIR.is_dir():
        return []
    return sorted(
        child.name
        for child in SKILLS_DIR.iterdir()
        if child.is_dir() and (child / "SKILL.md").is_file()
    )


def skill_description(skill_md: Path) -> str:
    data = read_frontmatter(skill_md)
    description = data.get("description", "")
    return " ".join(str(description).split())


def trash_move(path: Path) -> Path:
    """Move a path into the trash instead of deleting it. Returns its new home."""
    TRASH_DIR.mkdir(parents=True, exist_ok=True)
    stamp = subprocess.run(
        ["date", "+%Y%m%d-%H%M%S"], capture_output=True, text=True, check=False
    ).stdout.strip()
    target_dir = Path(
        subprocess.run(
            ["mktemp", "-d", str(TRASH_DIR / f"{stamp}-XXXXXX")],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
    )
    target = target_dir / path.name
    shutil.move(str(path), str(target))
    return target


def install(names: list[str], target: str, mode: str, dry_run: bool) -> int:
    failures = 0
    for name in names:
        source = SKILLS_DIR / name
        if not (source / "SKILL.md").is_file():
            print(f"skip: {name} (no SKILL.md in {source})", file=sys.stderr)
            failures += 1
            continue
        for root in target_dirs(target):
            destination = root / name
            root.mkdir(parents=True, exist_ok=True)
            if destination.is_symlink() or destination.exists():
                if destination.is_symlink():
                    if dry_run:
                        print(f"would replace {destination}")
                        continue
                    destination.unlink()
                elif (destination / "SKILL.md").is_file():
                    if dry_run:
                        print(f"would replace {destination}")
                        continue
                    moved = trash_move(destination)
                    print(f"replaced {destination} (previous copy moved to {moved})")
                else:
                    print(
                        f"refusing to overwrite {destination} (not a skill directory)",
                        file=sys.stderr,
                    )
                    failures += 1
                    continue
            if dry_run:
                print(f"would {mode} {name} -> {destination}")
                continue
            if mode == "copy":
                shutil.copytree(source, destination, symlinks=True)
            else:
                destination.symlink_to(source, target_is_directory=True)
            print(f"installed {name} -> {destination}")
    return failures


def uninstall(names: list[str], target: str, dry_run: bool) -> int:
    failures = 0
    for name in names:
        for root in target_dirs(target):
            destination = root / name
            if destination.is_symlink():
                if dry_run:
                    print(f"would remove {destination}")
                    continue
                destination.unlink()
                print(f"removed {destination}")
            elif destination.is_dir() and (destination / "SKILL.md").is_file():
                if dry_run:
                    print(f"would remove {destination}")
                    continue
                moved = trash_move(destination)
                print(f"removed {destination} (moved to {moved})")
            elif destination.exists():
                print(
                    f"refusing to remove {destination} (not a skill directory)",
                    file=sys.stderr,
                )
                failures += 1
            else:
                print(f"not installed: {name} ({destination})")
    return failures


def list_skills() -> int:
    print(f"{'SKILL':<24} DESCRIPTION")
    for name in all_skills():
        description = skill_description(SKILLS_DIR / name / "SKILL.md")
        print(f"{name:<24} {description}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Manage the skills in this repository.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "action",
        nargs="?",
        choices=["list", "install", "uninstall"],
        default="install",
        help="list skills, install them, or remove them (default: install)",
    )
    parser.add_argument(
        "skills", nargs="*", help="skill names; defaults to every skill in the repo"
    )
    parser.add_argument(
        "--target",
        choices=["claude", "opencode", "both"],
        default="both",
        help="which host to install into (default: both)",
    )
    parser.add_argument(
        "--mode",
        choices=["link", "copy"],
        default="link",
        help="symlink the skill (default) or copy it",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="show what would happen, change nothing"
    )
    parser.add_argument(
        "--list", dest="list_only", action="store_true", help="alias for 'list'"
    )
    parser.add_argument(
        "--uninstall", dest="uninstall_flag", action="store_true", help="alias for 'uninstall'"
    )
    args = parser.parse_args()

    action = args.action
    if args.list_only:
        action = "list"
    if args.uninstall_flag:
        action = "uninstall"

    names = args.skills or all_skills()
    if action == "list":
        return list_skills()
    if action == "install":
        return 1 if install(names, args.target, args.mode, args.dry_run) else 0
    return 1 if uninstall(names, args.target, args.dry_run) else 0


if __name__ == "__main__":
    raise SystemExit(main())
