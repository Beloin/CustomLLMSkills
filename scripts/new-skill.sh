#!/usr/bin/env bash
# Thin wrapper. The implementation lives in scripts/new_skill.py.
#
#   ./scripts/new-skill.sh my-skill-name
#   ./scripts/new-skill.sh my-skill-name --description "What it does"
exec "${PYTHON:-python3}" "$(dirname "${BASH_SOURCE[0]}")/new_skill.py" "$@"
