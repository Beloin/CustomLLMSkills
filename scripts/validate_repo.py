#!/usr/bin/env python3
"""Validate this skill repository.

    python3 scripts/validate_repo.py            # human output
    python3 scripts/validate_repo.py --json     # machine output

Checks the portable parts of the Agent Skills specification and the plugin
manifest rules that apply to any repository, not to one organisation's fleet.

Exit code 0 when there are no errors. Warnings do not fail the run.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _frontmatter import read as read_frontmatter  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO_ROOT / "skills"

NAME_PATTERN = re.compile(r"^[a-z0-9][a-z0-9.-]{0,63}$")
DESCRIPTION_LIMIT = 1024
DESCRIPTION_WARN = 500
BODY_WARN = 300
BODY_LIMIT = 500

PORTABLE_PLUGIN_FIELDS = {
    "$schema",
    "name",
    "version",
    "description",
    "author",
    "homepage",
    "repository",
    "license",
    "keywords",
    "extensions",
}

PORTABLE_SCHEMA = "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"

results: list[tuple[str, str, str]] = []


def error(message: str) -> None:
    results.append(("ERROR", message, ""))


def warn(message: str) -> None:
    results.append(("WARNING", message, ""))


def ok(message: str) -> None:
    results.append(("OK", message, ""))


def check_skill(skill_dir: Path) -> None:
    name = skill_dir.name
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        error(f"{name}: SKILL.md is missing")
        return

    text = skill_md.read_text(encoding="utf-8")
    data = read_frontmatter(skill_md)
    if not data:
        error(f"{name}: SKILL.md has no parseable frontmatter")
        return

    declared = data.get("name")
    if not declared:
        error(f"{name}: frontmatter has no name")
    elif declared != name:
        error(f"{name}: frontmatter name '{declared}' does not match the directory")
    elif not NAME_PATTERN.match(str(declared)):
        error(f"{name}: name must be lowercase, 1-64 chars, [a-z0-9.-]")

    description = str(data.get("description", ""))
    if not description:
        error(f"{name}: frontmatter has no description")
    else:
        if not description.startswith("Use when"):
            error(f"{name}: description must start with 'Use when'")
        if len(description) > DESCRIPTION_LIMIT:
            error(f"{name}: description is {len(description)} chars, limit is {DESCRIPTION_LIMIT}")
        elif len(description) > DESCRIPTION_WARN:
            warn(f"{name}: description is {len(description)} chars, past {DESCRIPTION_WARN}")
        if re.search(r"<[A-Za-z/]", description):
            error(f"{name}: description contains an XML-like tag")

    body = text.split("\n---", 1)[-1] if text.startswith("---") else text
    body_lines = len(body.strip().split("\n"))
    if body_lines > BODY_LIMIT:
        error(f"{name}: body is {body_lines} lines, limit is {BODY_LIMIT}")
    elif body_lines > BODY_WARN:
        warn(f"{name}: body is {body_lines} lines, past {BODY_WARN}")

    check_flat_discovery(name, skill_dir, text)


def check_flat_discovery(name: str, skill_dir: Path, text: str) -> None:
    """Every reference and every executable must be named in SKILL.md."""
    references = skill_dir / "references"
    if references.is_dir():
        for reference in sorted(references.glob("*.md")):
            if reference.name not in text:
                warn(f"{name}: references/{reference.name} is not named in SKILL.md")

    scripts = skill_dir / "scripts"
    if scripts.is_dir():
        for script in sorted(scripts.iterdir()):
            if not script.is_file() or script.name.startswith("."):
                continue
            if script.suffix not in {".sh", ".py", ".js", ".ts", ".rb", ".pl"}:
                continue
            if script.name not in text:
                warn(f"{name}: scripts/{script.name} is not named in SKILL.md")

    for mentioned in re.findall(r"`((?:references|scripts)/[^`]+)`", text):
        if not (skill_dir / mentioned).exists():
            error(f"{name}: SKILL.md names {mentioned}, which does not exist")


def check_manifests() -> None:
    portable = REPO_ROOT / "plugin.json"
    claude = REPO_ROOT / ".claude-plugin" / "plugin.json"
    marketplace = REPO_ROOT / ".claude-plugin" / "marketplace.json"

    shared: dict = {}
    if portable.is_file():
        try:
            data = json.loads(portable.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            error(f"plugin.json: invalid JSON ({exc})")
            data = None
        if data:
            extra = set(data) - PORTABLE_PLUGIN_FIELDS
            if extra:
                error(f"plugin.json: unknown field(s) {sorted(extra)}")
            if data.get("$schema") != PORTABLE_SCHEMA:
                error(f"plugin.json: $schema must be {PORTABLE_SCHEMA}")
            if not NAME_PATTERN.match(str(data.get("name", ""))):
                error("plugin.json: name must be lowercase, 1-64 chars, [a-z0-9.-]")
            shared = {k: v for k, v in data.items() if k in PORTABLE_PLUGIN_FIELDS - {"$schema"}}
            ok("plugin.json: portable manifest is valid")
    else:
        error("plugin.json: missing at the repository root")

    if claude.is_file():
        try:
            claude_data = json.loads(claude.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            error(f".claude-plugin/plugin.json: invalid JSON ({exc})")
            claude_data = None
        if claude_data:
            for key, value in shared.items():
                if claude_data.get(key) != value:
                    error(
                        f".claude-plugin/plugin.json: '{key}' differs from plugin.json "
                        f"({value!r} vs {claude_data.get(key)!r})"
                    )
            if shared:
                ok(".claude-plugin/plugin.json: shared fields match plugin.json")
    else:
        error(".claude-plugin/plugin.json: missing")

    if marketplace.is_file():
        try:
            data = json.loads(marketplace.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            error(f".claude-plugin/marketplace.json: invalid JSON ({exc})")
            data = None
        if data:
            if not data.get("name"):
                error(".claude-plugin/marketplace.json: missing name")
            if not data.get("owner"):
                error(".claude-plugin/marketplace.json: missing owner")
            entries = data.get("plugins")
            if not isinstance(entries, list) or not entries:
                error(".claude-plugin/marketplace.json: plugins must be a non-empty array")
            else:
                for entry in entries:
                    if not entry.get("name"):
                        error(".claude-plugin/marketplace.json: a plugin entry has no name")
                    if not entry.get("source"):
                        error(
                            f".claude-plugin/marketplace.json: plugin '{entry.get('name')}' "
                            "has no source"
                        )
                ok(".claude-plugin/marketplace.json: entries are valid")
    else:
        error(".claude-plugin/marketplace.json: missing")


def tracked_files() -> list[str]:
    """Files git tracks. Falls back to the working tree outside a repository."""
    try:
        result = subprocess.run(
            ["git", "ls-files", "-z"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return [
            str(path.relative_to(REPO_ROOT))
            for path in REPO_ROOT.rglob("*")
            if path.is_file() and ".git" not in path.parts
        ]
    return [name for name in result.stdout.split("\0") if name]


def check_repo_hygiene() -> None:
    licenses = [
        path.name
        for path in REPO_ROOT.iterdir()
        if path.is_file() and path.name.upper().startswith(("LICENSE", "LICENCE", "COPYING"))
    ]
    if not licenses:
        warn("no LICENSE file at the repository root")
    else:
        ok(f"licence file(s) present: {', '.join(sorted(licenses))}")

    if not (REPO_ROOT / "README.md").is_file():
        error("README.md: missing at the repository root")

    if not (REPO_ROOT / ".gitignore").is_file():
        warn(".gitignore: missing")

    bytecode = [
        name
        for name in tracked_files()
        if name.endswith((".pyc", ".pyo")) or "/__pycache__/" in f"/{name}"
    ]
    if bytecode:
        warn(f"committed Python bytecode: {bytecode}")

    for name in tracked_files():
        path = REPO_ROOT / name
        if path.is_symlink() and not path.exists():
            error(f"dangling symlink: {name}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    args = parser.parse_args()

    if SKILLS_DIR.is_dir():
        skill_dirs = sorted(
            child for child in SKILLS_DIR.iterdir() if child.is_dir()
        )
        if not skill_dirs:
            error("skills/: no skill directories found")
        for skill_dir in skill_dirs:
            check_skill(skill_dir)
    else:
        error("skills/: missing")

    check_manifests()
    check_repo_hygiene()

    errors = [r for r in results if r[0] == "ERROR"]
    warnings = [r for r in results if r[0] == "WARNING"]

    if args.json:
        print(
            json.dumps(
                {
                    "errors": [r[1] for r in errors],
                    "warnings": [r[1] for r in warnings],
                    "ok": len(results) - len(errors) - len(warnings),
                },
                indent=2,
            )
        )
        return 1 if errors else 0

    for level, message, _ in results:
        if level == "OK":
            print(f"OK:      {message}")
        elif level == "WARNING":
            print(f"WARNING: {message}")
        else:
            print(f"ERROR:   {message}", file=sys.stderr)
    print()
    print(f"Errors:   {len(errors)}")
    print(f"Warnings: {len(warnings)}")
    if errors:
        print("Validation failed.")
        return 1
    print("Validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
