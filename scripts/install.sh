#!/usr/bin/env bash
# Install the skills in this repository into Claude Code and/or OpenCode.
#
#   ./scripts/install.sh                  # install every skill into both hosts
#   ./scripts/install.sh --list           # list the skills in this repo
#   ./scripts/install.sh slide-creator    # install only the named skills
#   ./scripts/install.sh --target claude  # claude | opencode | both (default)
#   ./scripts/install.sh --mode copy      # copy instead of symlink (default: link)
#   ./scripts/install.sh --uninstall      # remove installed skills
#   ./scripts/install.sh --dry-run        # show what would happen
#
# Portable: no absolute paths, honours HOME, XDG_CONFIG_HOME, and CLAUDE_CONFIG_DIR.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILLS_DIR="$REPO_ROOT/skills"

CLAUDE_DIR="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
OPENCODE_DIR="${OPENCODE_CONFIG_DIR:-${XDG_CONFIG_HOME:-$HOME/.config}/opencode}"

TARGET="both"
MODE="link"
ACTION="install"
DRY_RUN=0
SELECTED=()

usage() {
    sed -n '2,18p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'
    exit "${1:-0}"
}

while [ $# -gt 0 ]; do
    case "$1" in
        --list)    ACTION="list"; shift ;;
        --target)  TARGET="${2:?--target needs claude, opencode, or both}"; shift 2 ;;
        --mode)    MODE="${2:?--mode needs link or copy}"; shift 2 ;;
        --uninstall) ACTION="uninstall"; shift ;;
        --dry-run) DRY_RUN=1; shift ;;
        -h|--help) usage 0 ;;
        -*)        echo "unknown option: $1" >&2; usage 1 ;;
        *)         SELECTED+=("$1"); shift ;;
    esac
done

# ---------------------------------------------------------------- discovery

skill_description() {
    # Read the description out of the SKILL.md frontmatter.
    # Handles plain values, quoted values, and folded (>) or literal (|) blocks.
    awk '
        { lines[NR] = $0 }
        END {
            if (lines[1] != "---") exit
            for (i = 2; i <= NR; i++) {
                if (lines[i] ~ /^---[[:space:]]*$/) exit
                if (lines[i] ~ /^description[[:space:]]*:/) {
                    rest = lines[i]
                    sub(/^description[[:space:]]*:[[:space:]]*/, "", rest)
                    if (rest ~ /^[>|]/) {
                        block = ""
                        for (j = i + 1; j <= NR; j++) {
                            line = lines[j]
                            if (line ~ /^---[[:space:]]*$/ || line ~ /^[A-Za-z_-]+[[:space:]]*:/) break
                            gsub(/^[[:space:]]+/, "", line)
                            gsub(/[[:space:]]+$/, "", line)
                            if (line != "") block = block (block == "" ? "" : " ") line
                        }
                        print block
                        exit
                    }
                    gsub(/^["'"'"']/, "", rest)
                    gsub(/["'"'"']$/, "", rest)
                    print rest
                    exit
                }
            }
        }
    ' "$1" 2>/dev/null | tr -s ' ' | sed 's/^ //;s/ $//' | cut -c1-90
}

all_skills() {
    [ -d "$SKILLS_DIR" ] || return 0
    for dir in "$SKILLS_DIR"/*/; do
        [ -f "${dir}SKILL.md" ] || continue
        basename "$dir"
    done
}

resolve_targets() {
    case "$TARGET" in
        claude)  echo "$CLAUDE_DIR/skills" ;;
        opencode) echo "$OPENCODE_DIR/skills" ;;
        both)    echo "$CLAUDE_DIR/skills"; echo "$OPENCODE_DIR/skills" ;;
        *)       echo "unknown target: $TARGET (use claude, opencode, or both)" >&2; exit 1 ;;
    esac
}

# ------------------------------------------------------------------- actions

trash_root() {
    echo "${MY_SKILLS_TRASH:-$HOME/.my-skills-trash}"
}

# Move a path into the trash instead of deleting it. Reversible.
trash_move() {
    local path="$1" trash target
    trash="$(mktemp -d "$(trash_root)/$(date +%Y%m%d-%H%M%S)-XXXXXX")"
    target="$trash/$(basename "$path")"
    mv "$path" "$target"
    echo "$target"
}

# The skills to act on: the ones named on the command line, or all of them.
selected_skills() {
    if [ ${#SELECTED[@]} -gt 0 ]; then
        printf '%s\n' "${SELECTED[@]}"
    else
        all_skills
    fi
}

do_install() {
    local skill dest_root
    while IFS= read -r skill; do
        [ -n "$skill" ] || continue
        local src="$SKILLS_DIR/$skill"
        if [ ! -f "$src/SKILL.md" ]; then
            echo "skip: $skill (no SKILL.md in $src)" >&2
            continue
        fi
        while IFS= read -r dest_root; do
            dest="$dest_root/$skill"
            mkdir -p "$dest_root"
            if [ -e "$dest" ] || [ -L "$dest" ]; then
                # Replace only what this installer put there: a symlink, or a
                # directory that holds a SKILL.md. Anything else is left alone.
                if [ -L "$dest" ]; then
                    [ "$DRY_RUN" -eq 1 ] && { echo "would replace $dest"; continue; }
                    rm "$dest"
                elif [ -d "$dest" ] && [ -f "$dest/SKILL.md" ]; then
                    [ "$DRY_RUN" -eq 1 ] && { echo "would replace $dest"; continue; }
                    echo "replaced $dest (previous copy moved to $(trash_move "$dest"))"
                else
                    echo "refusing to overwrite $dest (not a skill directory)" >&2
                    continue
                fi
            fi
            if [ "$DRY_RUN" -eq 1 ]; then
                echo "would $MODE $skill -> $dest"
                continue
            fi
            if [ "$MODE" = "copy" ]; then
                cp -R "$src" "$dest"
            else
                ln -s "$src" "$dest"
            fi
            echo "installed $skill -> $dest"
        done < <(resolve_targets)
    done < <(selected_skills)
}

do_uninstall() {
    local skill dest_root dest
    while IFS= read -r skill; do
        [ -n "$skill" ] || continue
        while IFS= read -r dest_root; do
            dest="$dest_root/$skill"
            if [ -L "$dest" ]; then
                [ "$DRY_RUN" -eq 1 ] && { echo "would remove $dest"; continue; }
                rm "$dest"
                echo "removed $dest"
            elif [ -d "$dest" ] && [ -f "$dest/SKILL.md" ]; then
                [ "$DRY_RUN" -eq 1 ] && { echo "would remove $dest"; continue; }
                echo "removed $dest (moved to $(trash_move "$dest"))"
            elif [ -e "$dest" ]; then
                echo "refusing to remove $dest (not a skill directory)" >&2
            else
                echo "not installed: $skill ($dest)"
            fi
        done < <(resolve_targets)
    done < <(selected_skills)
}

do_list() {
    local skill
    printf '%-24s %s\n' "SKILL" "DESCRIPTION"
    while IFS= read -r skill; do
        [ -n "$skill" ] || continue
        printf '%-24s %s\n' "$skill" "$(skill_description "$SKILLS_DIR/$skill/SKILL.md")"
    done < <(all_skills)
}

case "$ACTION" in
    list)      do_list ;;
    uninstall) do_uninstall ;;
    install)   do_install ;;
esac
