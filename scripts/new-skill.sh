#!/usr/bin/env bash
# Create a new skill in this repository from a template.
#
#   ./scripts/new-skill.sh my-skill-name
#   ./scripts/new-skill.sh my-skill-name --description "What it does"
#
# Creates skills/<name>/SKILL.md with valid frontmatter.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILLS_DIR="$REPO_ROOT/skills"

NAME="${1:-}"
DESC=""
shift || true
while [ $# -gt 0 ]; do
    case "$1" in
        --description) DESC="${2:?--description needs a value}"; shift 2 ;;
        *) echo "unknown option: $1" >&2; exit 1 ;;
    esac
done

if [ -z "$NAME" ]; then
    echo "usage: $0 <skill-name> [--description \"...\"]" >&2
    exit 1
fi

if ! printf '%s' "$NAME" | grep -Eq '^[a-z0-9][a-z0-9-]*$'; then
    echo "skill name must be lowercase kebab-case: $NAME" >&2
    exit 1
fi

TARGET="$SKILLS_DIR/$NAME"
if [ -e "$TARGET" ]; then
    echo "already exists: $TARGET" >&2
    exit 1
fi

mkdir -p "$TARGET/scripts" "$TARGET/references"

if [ -z "$DESC" ]; then
    DESC="Describe what this skill does and when to use it."
fi

cat > "$TARGET/SKILL.md" <<EOF
---
name: $NAME
description: >
  $DESC Use when the user asks for this specific thing.
---

# ${NAME//-/ }

Describe what this skill does, when to use it, and any hard rules.

## Instructions

1. First step.
2. Second step.
3. Verify the result.

## Files

- \`scripts/\` — helper code, if any.
- \`references/\` — supporting documents, if any.
EOF

cat > "$TARGET/README.md" <<EOF
# $NAME

$DESC

See [SKILL.md](SKILL.md) for the skill definition.
EOF

printf '' > "$TARGET/scripts/.gitkeep"
printf '' > "$TARGET/references/.gitkeep"

echo "created $TARGET"
echo "next: edit $TARGET/SKILL.md, then run ./scripts/install.sh $NAME"
