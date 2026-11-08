#!/usr/bin/env python3
"""Create a new skill in this repository from a template.

    python3 scripts/new_skill.py my-skill-name
    python3 scripts/new_skill.py my-skill-name --description "What it does"

Creates skills/<name>/SKILL.md with valid frontmatter, plus a README and
empty scripts/ and references/ directories.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO_ROOT / "skills"

NAME_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]*$")

SKILL_TEMPLATE = """---
name: {name}
description: >
  Use when the user asks for {subject}. {description}
metadata:
  version: 0.1.0
---

# {title}

Describe what this skill does, when to use it, and any hard rules.

## Instructions

1. First step.
2. Second step.
3. Verify the result.

## Resources

- `references/` — supporting documents, if any.
- `scripts/` — helper code, if any.
"""

README_TEMPLATE = """# {name}

{description}

See [SKILL.md](SKILL.md) for the skill definition.
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("name", help="skill name, lowercase kebab-case")
    parser.add_argument(
        "--description",
        default="Describe what this skill does.",
        help="one-line description of what the skill handles",
    )
    parser.add_argument(
        "--subject",
        default="",
        help="the thing the user asks for, e.g. 'a PDF table extractor'",
    )
    args = parser.parse_args()

    if not NAME_PATTERN.match(args.name):
        print(
            f"skill name must be lowercase kebab-case: {args.name}",
            file=sys.stderr,
        )
        return 1

    subject = args.subject or args.description.rstrip(". ")
    target = SKILLS_DIR / args.name
    if target.exists():
        print(f"already exists: {target}", file=sys.stderr)
        return 1

    (target / "scripts").mkdir(parents=True)
    (target / "references").mkdir(parents=True)

    title = args.name.replace("-", " ").capitalize()
    (target / "SKILL.md").write_text(
        SKILL_TEMPLATE.format(
            name=args.name,
            subject=subject,
            description=args.description.rstrip(". "),
            title=title,
        ),
        encoding="utf-8",
    )
    (target / "README.md").write_text(
        README_TEMPLATE.format(name=args.name, description=args.description),
        encoding="utf-8",
    )
    (target / "scripts" / ".gitkeep").write_text("", encoding="utf-8")
    (target / "references" / ".gitkeep").write_text("", encoding="utf-8")

    print(f"created {target}")
    print(f"next: edit {target / 'SKILL.md'}, then run scripts/skill_repo.py install {args.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
