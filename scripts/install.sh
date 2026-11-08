#!/usr/bin/env bash
# Thin wrapper. The implementation lives in scripts/skill_repo.py.
#
#   ./scripts/install.sh                  # install every skill into both hosts
#   ./scripts/install.sh --list           # list the skills in this repo
#   ./scripts/install.sh slide-creator    # install only the named skills
#   ./scripts/install.sh --target claude  # claude | opencode | both (default)
#   ./scripts/install.sh --mode copy      # copy instead of symlink (default: link)
#   ./scripts/install.sh --uninstall      # remove installed skills
#   ./scripts/install.sh --dry-run        # show what would happen
exec "${PYTHON:-python3}" "$(dirname "${BASH_SOURCE[0]}")/skill_repo.py" \
    install "$@"
